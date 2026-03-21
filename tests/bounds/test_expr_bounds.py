import protomorph as pm

from axis import expr, log, sem, syn
from axis.expr.ir import Scope
from axis.expr.ir.bound import build_bound, build_default, build_term

from tests.helpers import StdPackageTestCase


class DummyBoundContext(pm.ContextProto):
    pass


class DummyBoundVar(pm.VarType[DummyBoundContext]):
    pass


class ExprBoundsTest(StdPackageTestCase):
    std_root_scope: sem.Scope

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.std_root_scope = cls.pkg.scope("std")

        dummy_ctx = DummyBoundContext()
        builder = Scope.Builder(name="bounds")
        for name in ("Optional", "Array", "Text", "Natural", "Sym", "Whole"):
            builder.define(name, pm.anchor(name), origin=expr.Sym(name=name))
        for name in ("K", "N", "rank"):
            builder.define(
                name,
                pm.val(pm.var(DummyBoundVar, dummy_ctx, name)),
                origin=expr.Sym(name=name),
            )
        cls.bound_scope = builder.build()

    def test_sym_uses_scope_only(self):
        self.assertIsInstance(build_bound(expr.Sym(name="std"), self.std_root_scope), pm.Err)
        self.assertEqual(
            build_bound(expr.Sym(name="core"), self.std_root_scope),
            pm.anchor("std.core"),
        )
        self.assertEqual(
            build_bound(expr.Sym(name="types"), self.std_root_scope),
            pm.anchor("std.types"),
        )

    def test_member_requires_anchor_base(self):
        self.assertIsInstance(
            build_bound(expr.Member(of=expr.Sym(name="std"), name="Text"), self.std_root_scope),
            pm.Err,
        )
        bound = build_bound(
            expr.Member(of=expr.Member(of=expr.Sym(name="core"), name="Text"), name="Inner"),
            self.std_root_scope,
        )
        assert bound is not None
        self.assertEqual(bound, pm.anchor("std.core.Text.Inner"))

    def test_index_builds_specialized_ref_from_anchor(self):
        indexed = build_bound(
            expr.Index(origin=expr.Member(of=expr.Sym(name="core"), name="Text"), indices=expr.Member(of=expr.Sym(name="core"), name="Natural")),
            self.std_root_scope,
        )

        assert indexed is not None
        term = build_term(
            expr.Index(
                origin=expr.Member(of=expr.Sym(name="core"), name="Text"),
                indices=expr.Member(of=expr.Sym(name="core"), name="Natural"),
            ),
            self.std_root_scope,
        )
        assert term is not None
        self.assertEqual(indexed, term)

    def test_nested_std_module_spec_anchor_resolves_from_scope(self):
        indexed = self.bound("types.Spec[core.Text]", self.std_root_scope)
        term = build_term(syn.Expr.from_str("types.Spec[core.Text]"), self.std_root_scope)

        assert term is not None
        self.assertEqual(indexed, term)

    def test_lit_and_tuple_build_structural_values(self):
        self.assertEqual(build_bound(expr.Lit(value=42), self.std_root_scope), pm.literal(42))

        tuple_bound = build_bound(
            expr.Tuple(
                elements=(
                    expr.Tuple.Positional(value=expr.Lit(value=1)),
                    expr.Tuple.Nominal(
                        key=expr.Sym(name="name"),
                        bound=None,
                        value=expr.Lit(value="x"),
                    ),
                )
            ),
            self.std_root_scope,
        )

        self.assertEqual(tuple_bound, pm.struct(pm.literal(1), name=pm.literal("x")))

    def test_apply_degrades_to_pm_err(self):
        bound = build_bound(
            expr.Apply(
                function=expr.Sym(name="Text"),
                argument=expr.Tuple(
                    elements=(expr.Tuple.Positional(value=expr.Sym(name="Natural")),)
                ),
            ),
            self.std_root_scope,
        )

        self.assertIsInstance(bound, pm.Err)

    def test_unsupported_anchor_expression_throws_structured_report(self):
        with self.assertRaises(log.Report.Exception):
            expr.Index(
                origin=expr.Sym(name="Text"),
                indices=expr.Sym(name="Natural"),
            ).to_anchor(None)

    def test_default_construction_matches_bound_rules(self):
        self.assertEqual(build_default(expr.Lit(value=7), self.std_root_scope), pm.literal(7))
        self.assertEqual(
            build_default(syn.Expr.from_str("Optional Text"), self.bound_scope),
            build_term(syn.Expr.from_str("Optional Text"), self.bound_scope),
        )

    def test_binding_pattern_compiles_open_tail_to_variadic_struct(self):
        bindings = expr.build_binding_struct(expr.Tuple.from_str("(x, ..rest)"), None)

        pattern = expr.build_binding_pattern(bindings, self.bound_scope)

        self.assertIsInstance(pattern, pm.Op)
        assert isinstance(pattern, pm.Op)
        self.assertIsInstance(pattern.__data__, pm.VariadicStruct)

    def test_build_struct_schema_builds_closed_schema_from_bindings(self):
        bindings = expr.build_binding_struct(expr.Tuple.from_str("(x: Whole, name: Text = Sym)"), None)
        schema = sem.binding_schema(sem.lower_binding_struct(bindings, self.bound_scope))

        self.assertEqual(schema.fields.index.keys, ("x", "name"))
        self.assertIsNone(schema.varsign)
        self.assertEqual(schema.fields.values[0].match_expr, pm.anchor("Whole"))
        self.assertEqual(schema.fields.values[1].default, pm.anchor("Sym"))

    def test_build_struct_schema_builds_variadic_schema_from_spread(self):
        bindings = expr.build_binding_struct(expr.Tuple.from_str("(x, ..rest)"), None)
        schema = sem.binding_schema(sem.lower_binding_struct(bindings, self.bound_scope))

        self.assertIsNotNone(schema.varsign)
        assert schema.varsign is not None
        self.assertEqual(schema.varsign.prefix_index.keys, (None,))
        self.assertEqual(schema.varsign.suffix_index.keys, ())
        self.assertEqual(schema.middle, pm.ANY)

    def test_build_struct_schema_marks_open_tail_from_inline_ellipsis(self):
        bindings = expr.build_binding_struct(
            expr.Tuple.from_str("(x, ... )"),
            expr.Tuple.from_str("(x: Whole)"),
        )
        schema = sem.binding_schema(sem.lower_binding_struct(bindings, self.bound_scope))

        self.assertIsNotNone(schema.varsign)
        assert schema.varsign is not None
        self.assertEqual(schema.varsign.prefix_index.keys, (None,))
        self.assertEqual(schema.middle, pm.ANY)

    def test_compound_bound_returns_nominal_qualifier_term(self):
        bound = build_bound(syn.Expr.from_str("Optional Text"), self.bound_scope)
        term = build_term(syn.Expr.from_str("Optional Text"), self.bound_scope)

        assert bound is not None
        assert term is not None
        self.assertEqual(bound, term)

    def test_compound_builds_nested_qualifiers_right_to_left(self):
        self.assertTypeEq(
            "qualifiers.Optional qualifiers.Struct[core.Text] types.Type",
            "qualifiers.Optional qualifiers.Struct[core.Text] types.Type",
        )
        bound = self.type_bound("qualifiers.Optional qualifiers.Struct[core.Text] types.Type")
        assert isinstance(bound, pm.NominalQualifier)
        self.assertEqual(bound.underlying, self.type_bound("qualifiers.Struct[core.Text] types.Type"))

    # def test_compound_requires_qualifier_symbols_from_scope(self):
    #     self.assertIsInstance(
    #         build_bound(syn.Expr.from_str("Optional Text"), self.std_scope),
    #         pm.Err,
    #     )

    def test_std_core_qualifier_patterns(self):
        patterns = (
            ("Optional Text", "Optional"),
            ("Array[Natural] Natural", "Array"),
        )

        for source, path in patterns:
            value = build_bound(syn.Expr.from_str(source), self.bound_scope)
            term = build_term(syn.Expr.from_str(source), self.bound_scope)
            assert isinstance(term, pm.Const)
            assert isinstance(term.__data__, pm.NominalQualifier)
            self.assertEqual(term.__data__.spec_ref.path, path)
            assert value is not None
            self.assertEqual(value, term)

    def test_nested_member_plus_index_builds_qualified_value(self):
        nested_scope = Scope.Builder(name="nested")
        nested_scope.define(
            "Struct",
            pm.anchor("Struct"),
            origin=expr.Sym(name="Struct"),
        )
        nested_scope.define(
            "Whole",
            pm.anchor("Whole"),
            origin=expr.Sym(name="Whole"),
        )
        nested_scope.define(
            "Sym",
            pm.anchor("Sym"),
            origin=expr.Sym(name="Sym"),
        )
        scope = nested_scope.build()

        value = build_bound(syn.Expr.from_str("Struct.Index[Whole] Sym"), scope)

        term = build_term(syn.Expr.from_str("Struct.Index[Whole] Sym"), scope)
        assert isinstance(term, pm.Const)
        assert isinstance(term.__data__, pm.NominalQualifier)
        self.assertEqual(term.__data__.spec_ref.path, "Struct.Index")
        assert value is not None
        self.assertEqual(value, term)

    def test_canonical_std_scope_builder_helper(self):
        self.assertBoundEq("core.Text", "core.Text", scope=self.std_root_scope)

    def test_use_scope_imports_canonical_aliases(self):
        scope = self.use_scope("std(core.Text, types.StructType)")

        self.assertBoundEq("Text", "core.Text", scope=scope)
        self.assertBoundEq("StructType", "types.StructType", scope=scope)

    def test_use_scope_accepts_explicit_use_prefix(self):
        scope = self.resolve_scope("use std(qualifiers.Optional, core.Text)")

        self.assertBoundEq("Optional", "qualifiers.Optional", scope=scope)
        self.assertBoundEq("Text", "core.Text", scope=scope)

    def test_scope_resolver_accepts_context_instance(self):
        types_ctx = self.pkg.context("std.types")

        resolved = self.resolve_scope(types_ctx)

        self.assertIsInstance(resolved, sem.Scope)
        self.assertEqual(resolved, types_ctx.scope)
