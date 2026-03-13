import unittest

import protomorph as pm

from axis import expr, items, syn
from axis.expr.ir import Scope
from axis.expr.ir.bound import build_bound, build_default


class DummyBoundContext(pm.ContextProto):
    pass


class DummyBoundVar(pm.VarType[DummyBoundContext]):
    pass


class ExprBoundsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = items.Package.from_path("codebase/std.core")
        cls.std_scope = next(
            ctx for ctx in cls.pkg.all_contexts if type(ctx).__name__ == "Unit"
        ).scope

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
        self.assertIsInstance(build_bound(expr.Sym(name="std"), self.std_scope), pm.Err)
        self.assertEqual(
            build_bound(expr.Sym(name="Text"), self.std_scope),
            pm.anchor("std.Text"),
        )

    def test_member_requires_anchor_base(self):
        self.assertIsInstance(
            build_bound(expr.Member(of=expr.Sym(name="std"), name="Text"), self.std_scope),
            pm.Err,
        )
        self.assertEqual(
            build_bound(
                expr.Member(of=expr.Sym(name="Text"), name="Inner"),
                self.std_scope,
            ),
            pm.anchor("std.Text.Inner"),
        )

    def test_index_builds_specialized_ref_from_anchor(self):
        indexed = build_bound(
            expr.Index(origin=expr.Sym(name="Text"), indices=expr.Sym(name="Natural")),
            self.std_scope,
        )

        assert isinstance(indexed, pm.Spec)
        self.assertEqual(indexed.path, "std.Text")
        self.assertIsNotNone(indexed.args)

    def test_lit_and_tuple_build_structural_values(self):
        self.assertEqual(build_bound(expr.Lit(value=42), self.std_scope), pm.literal(42))

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
            self.std_scope,
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
            self.std_scope,
        )

        self.assertIsInstance(bound, pm.Err)

    def test_default_construction_matches_bound_rules(self):
        self.assertEqual(build_default(expr.Lit(value=7), self.std_scope), pm.literal(7))
        self.assertEqual(
            build_default(syn.Expr.from_str("Optional Text"), self.bound_scope),
            build_bound(syn.Expr.from_str("Optional Text"), self.bound_scope),
        )

    def test_compound_builds_nominal_qualifier_type_values(self):
        bound = build_bound(syn.Expr.from_str("Optional Text"), self.bound_scope)

        assert isinstance(bound, pm.Const)
        assert isinstance(bound.data, pm.NominalQualifier)
        self.assertEqual(bound.data.spec_ref.path, "Optional")
        self.assertEqual(repr(pm.val(bound.data.underlying)), "Text")

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
            assert isinstance(value, pm.Const)
            assert isinstance(value.data, pm.NominalQualifier)
            self.assertEqual(value.data.spec_ref.path, path)

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

        assert isinstance(value, pm.Const)
        assert isinstance(value.data, pm.NominalQualifier)
        self.assertEqual(value.data.spec_ref.path, "Struct.Index")


if __name__ == "__main__":
    unittest.main()
