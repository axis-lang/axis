import protomorph as pm

from axis import expr, items, log, sem, syn
from axis.expr.index import Index
from axis.items.defs.base import build_binding_struct
from tests.helpers import SemanticTestCase, StdPackageTestCase, TestPackage

TEST_PKG = TestPackage.with_std()


def parse_def(source: str) -> items.Def:
    return TEST_PKG.parse_any_def(source)


class DefFromSrcTest(SemanticTestCase):
    def test_from_src_parses_def_without_unit_wrapper(self):
        cases = (
            ("def Optional T", items.QualDef),
            ("def Integer", items.AtomDef),
            ("def Extends[X, from=Y]", items.FactDef),
            ("def E[A](x, y)", items.ClassDef),
        )

        for source, expected_type in cases:
            with self.subTest(source=source):
                node = parse_def(source)
                self.assertIsInstance(node, expected_type)

    def test_from_src_preserves_inline_shape_information(self):
        node = TEST_PKG.parse_def(
            items.QualDef,
            """def Array[..Dims, ...] T
where:
    val Dims: Array Natural
    val T: Type = Sym
""",
        )

        self.assertIsInstance(node, items.QualDef)
        self.assertIsNotNone(node.spec)
        assert node.spec is not None
        self.assertTrue(node.spec.elements[0].is_spread)
        self.assertTrue(node.spec.elements[1].is_ellipsis)
        self.assertEqual(
            tuple(str(element) for element in node.where[0].elements),
            ("Dims: Array Natural", "T: Type = Sym"),
        )

    def test_from_src_preserves_inline_args_and_takes_blocks(self):
        node = TEST_PKG.parse_def(
            items.ClassDef,
            """def E[A, ...](x, y)
where:
    val A: Type
    val K: Type = Sym
takes:
    val x: Whole
    val y: Text
""",
        )

        self.assertIsInstance(node, items.ClassDef)
        self.assertEqual(str(node.spec), "(A, Lit(Ellipsis))")
        self.assertEqual(str(node.args), "(x, y)")
        self.assertEqual(
            tuple(str(element) for element in node.takes[0].elements),
            ("x: Whole", "y: Text"),
        )

    def test_from_src_preserves_extends_block(self):
        node = TEST_PKG.parse_def(
            items.FactDef,
            """def Pair[T]
extends Box[T]
""",
        )

        self.assertEqual(len(node.extends), 1)
        self.assertIsInstance(node.extends[0].expr, Index)


class DefBuildBindingStructTest(SemanticTestCase):
    def test_inline_only_bindings_are_preserved(self):
        node = TEST_PKG.parse_def(items.FactDef, "def Struct[Key: Type = Text]")
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=None,
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertEqual(len(struct.values), 1)
        self.assertEqual(struct.values[0].binder_name, "Key")
        self.assertEqual(struct.values[0].slot_key, None)
        self.assertEqual(str(struct.values[0].bound_expr), "Type")
        self.assertEqual(str(struct.values[0].default_expr), "Text")
        self.assertFalse(struct.open_tail)

    def test_block_only_bindings_remain_nominal(self):
        node = TEST_PKG.parse_def(
            items.AtomDef,
            """def E
where:
    val A: Type
    val B: Type = Sym
""",
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, ("A", "B"))
        self.assertEqual(tuple(binding.slot_key for binding in struct.values), ("A", "B"))

    def test_prefix_match_with_spread(self):
        node = parse_def(
            """def Array[..Dims, ...] T
where:
    val Dims: Array Natural
    val T: Type = Sym
"""
        )
        assert isinstance(node, items.QualDef)
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None, "T"))
        self.assertEqual(len(struct.values), 2)
        self.assertTrue(struct.values[0].is_variadic)
        self.assertTrue(struct.open_tail)

    def test_param_bindings_use_real_takes_blocks(self):
        node = TEST_PKG.parse_def(
            items.ClassDef,
            """def E[A](x, ...)
where:
    val A: Type
takes:
    val x: Whole
    val y: Text
""",
        )
        struct = build_binding_struct(
            inline_expr=node.args,
            block_expr=node.takes[0],
        )
        self.assertEqual(struct.index.keys, (None, "y"))
        self.assertEqual(len(struct.values), 2)
        self.assertTrue(struct.open_tail)

    def test_inline_placeholder_merges_with_block_placeholder(self):
        node = TEST_PKG.parse_def(
            items.FactDef,
            """def E[_]
where:
    val _: Natural
""",
        )
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertTrue(struct.values[0].is_placeholder)
        self.assertEqual(str(struct.values[0].bound_expr), "Natural")

    def test_block_only_spread_is_supported(self):
        node = parse_def(
            """def E
where:
    val ..Args: Array Natural
"""
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertTrue(struct.values[0].is_variadic)
        self.assertEqual(struct.values[0].binder_name, "Args")

    def test_closed_inline_rejects_extra_block_bindings(self):
        node = TEST_PKG.parse_def(
            items.FactDef,
            """def E[A]
where:
    val A: Type
    val B: Type
""",
        )
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None, "B"))
        self.assertEqual(tuple(binding.binder_name for binding in struct.values), ("A", "B"))

    def test_rejects_conflicting_bounds(self):
        node = TEST_PKG.parse_def(
            items.FactDef,
            """def E[A: Whole]
where:
    val A: Text
""",
        )
        with self.suppress_report_output(), self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=node.spec,
                block_expr=node.where[0],
            )

    def test_rejects_nonfinal_ellipsis(self):
        inline_expr = expr.Tuple.from_str("(a, ..., b)")
        with self.suppress_report_output(), self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=inline_expr,
                block_expr=None,
            )

    def test_rejects_nonfinal_spread(self):
        inline_expr = expr.Tuple.from_str("(..rest, a)")
        with self.suppress_report_output(), self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=inline_expr,
                block_expr=None,
            )


class ContributionBoundExprTest(StdPackageTestCase):
    def test_fact_def_exposes_predicate_contribution(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        contrib = next(iter(pkg.contributions("demo.facts.Extends", sem.Entity.PredicateContribution)))
        assert isinstance(contrib, sem.Entity.PredicateContribution)

        entity = pkg.entity("demo.facts.Extends")

        self.assertIn(contrib, entity.predicate_signatures)

    def test_qual_contribution_exposes_underlying_bound_expr_and_bound(self):
        contrib = self.assertContribution(
            "std.qualifiers.Optional",
            sem.Entity.QualContribution,
        )
        assert isinstance(contrib, sem.Entity.QualContribution)

        self.assertEqual(str(contrib.underlying_bound_expr), "T")
        self.assertIsInstance(contrib.underlying_bound, pm.Op)
        assert isinstance(contrib.underlying_bound, pm.Op)
        self.assertIsInstance(contrib.underlying_bound.__data__, pm.Satisfy)

    def test_array_qual_contribution_exposes_nontrivial_underlying_bound(self):
        qual_contribs = tuple(
            contrib
            for contrib in self.pkg.contributions(
                "std.qualifiers.Array",
                sem.Entity.QualContribution,
            )
            if isinstance(contrib, sem.Entity.QualContribution)
        )
        contrib = next(
            contrib
            for contrib in qual_contribs
            if str(contrib.underlying_bound_expr) == "T"
        )

        self.assertEqual(str(contrib.underlying_bound_expr), "T")
        self.assertIsNotNone(contrib.underlying_bound)

    def test_overload_layout_resolves_spec_vars_from_args(self):
        node = TEST_PKG.parse_def(
            items.ClassDef,
            """def Box[T](value)
where:
    val T: Type
takes:
    val value: T
"""
        )
        contrib = next(iter(node.contributions))
        assert isinstance(contrib, sem.Entity.OverloadContribution)

        layout = contrib.layout(pm.Struct.new(T=pm.val(self.type_bound("core.Sym"))))

        self.assertIsNotNone(layout)
        assert isinstance(layout, pm.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), (None,))
        self.assertEqual(layout.fields.values[0], self.type_bound("core.Sym"))

    def test_class_def_extends_emits_fact_contribution(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit test

            def Box[T](value)
            where:
                val T: Type
            takes:
                val value: T

            def Pair[T](value)
            extends Box[T]
            where:
                val T: Type
            takes:
                val value: T
            """
        )
        contrib = next(iter(pkg.contributions("std.facts.Extends", sem.Context.FactContribution)))
        assert isinstance(contrib, sem.Context.FactContribution)

        self.assertEqual(len(contrib.facts), 1)
        fact = next(iter(contrib.facts))
        self.assertEqual(fact.anchor.path, "std.facts.Extends")

    def test_qual_def_extends_emits_fact_contribution(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit test

            def Maybe T
            where:
                val T: Type

            def Optional T
            extends Maybe[T]
            where:
                val T: Type
            """
        )
        contrib = next(iter(pkg.contributions("std.facts.Extends", sem.Context.FactContribution)))
        assert isinstance(contrib, sem.Context.FactContribution)

        self.assertEqual(len(contrib.facts), 1)
        fact = next(iter(contrib.facts))
        self.assertEqual(fact.anchor.path, "std.facts.Extends")
