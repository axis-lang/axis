import protomorph as pm
from protomorph import reasoning as urs
from typing import cast

from axis import expr, items, sem
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
            ("def Extends[X, from: Type]", items.FactDef),
            ("def E[A](x, y)", items.ClassDef),
        )

        for source, expected_type in cases:
            with self.subTest(source=source):
                node = parse_def(source)
                self.assertIsInstance(node, expected_type)

    def test_from_src_preserves_extends_block(self):
        node = TEST_PKG.parse_def(
            items.FactDef,
            """
            def Pair[T]
            extends Box[T]
            """,
        )

        self.assertEqual(len(node.extends), 1)
        self.assertIsInstance(node.extends[0].expr, Index)


class DefBuildBindingStructTest(SemanticTestCase):
    def test_inline_nominal_bound_is_required(self):
        node = TEST_PKG.parse_def(items.FactDef, "def Struct[Key: Type]")
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=None,
        )

        self.assertEqual(len(struct.values), 1)
        binding = struct.values[0]
        self.assertEqual(binding.binder_name, "Key")
        self.assertEqual(binding.slot_key, "Key")
        self.assertEqual(str(binding.bound_expr), "Type")
        self.assertIsNone(binding.default_expr)
        self.assertTrue(binding.is_required)

    def test_inline_nominal_default_is_optional(self):
        node = TEST_PKG.parse_def(items.FactDef, "def Struct[Key: Type = Text]")
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=None,
        )

        self.assertEqual(len(struct.values), 1)
        binding = struct.values[0]
        self.assertEqual(binding.binder_name, "Key")
        self.assertEqual(binding.slot_key, "Key")
        self.assertEqual(str(binding.bound_expr), "Type")
        self.assertEqual(str(binding.default_expr), "Text")
        self.assertTrue(binding.is_optional)

    def test_block_nominal_bindings_remain_named(self):
        node = TEST_PKG.parse_def(
            items.AtomDef,
            """
            def E
            where:
                val A: Type
                val B: Type = Sym
            """,
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )

        self.assertEqual(tuple(binding.slot_key for binding in struct.values), ("A", "B"))
        self.assertEqual(tuple(binding.binder_name for binding in struct.values), ("A", "B"))

    def test_block_only_spread_is_supported(self):
        node = parse_def(
            """
            def E
            where:
                val ..Args: Array Natural
            """
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )

        self.assertEqual(len(struct.values), 1)
        self.assertTrue(struct.values[0].is_variadic)
        self.assertEqual(struct.values[0].binder_name, "Args")


class FactFacetTest(StdPackageTestCase):
    def test_fact_def_emits_fact_facet(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types)

            mod facts
                def Extends[X, from: types.Type]
            """
        )

        contrib = next(iter(pkg.contributions("demo.facts.Extends", sem.Entity.FactFacet)))
        self.assertIsInstance(contrib, sem.Entity.FactFacet)

        entity = pkg.entity("demo.facts.Extends")
        self.assertEqual(len(entity.facet(sem.Entity.FactFacet).contributions), 1)

    def test_entity_for_filters_contributions(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            def Box[T](value)
            where:
                val T: types.Type
            takes:
                val value: T
            """
        )

        entity = pkg.entity("demo.Box")
        class_view = entity.for_(facet=sem.Entity.ClassFacet)

        self.assertEqual(class_view.anchor, entity.anchor)
        self.assertEqual(len(class_view.contributions), 1)

    def test_entity_exposes_fact_pattern_for_fact_facet(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types)

            mod facts
                def Extends[X, from: types.Type]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        self.assertIsNotNone(entity.spec_pattern_for(sem.Entity.FactFacet))

    def test_fact_facet_pattern_matches_admitted_fact_args(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types, core)

            mod facts
                def Extends[X, from: types.Type]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        pattern = entity.spec_pattern_for(sem.Entity.FactFacet)
        self.assertIsNotNone(pattern)
        assert pattern is not None

        subject = pm.Spec.of(
            "demo.facts.Extends",
            pm.Anchor("std.types.Text"),
            **{"from": pm.Spec.of("std.types.Type")},
        ).args
        self.assertIsNotNone(subject)
        assert subject is not None

        self.assertIsNotNone(pattern.match(subject))

    def test_fact_facet_pattern_rejects_missing_required_nominal(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types)

            mod facts
                def Extends[X, from: types.Type]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        pattern = entity.spec_pattern_for(sem.Entity.FactFacet)
        self.assertIsNotNone(pattern)
        assert pattern is not None

        subject = pm.Spec.of(
            "demo.facts.Extends",
            pm.Anchor("std.types.Text"),
        ).args
        self.assertIsNotNone(subject)
        assert subject is not None

        self.assertIsNone(pattern.match(subject))

    def test_fact_def_extends_is_semantically_inert(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Pair[T]
                extends Box[T]
            """
        )

        contribs = pkg.contributions("demo.facts.Pair", sem.Entity.FactFacet)
        self.assertEqual(len(contribs), 1)
        self.assertEqual(tuple(pkg.workspace.all_facts), ())


class ConstraintGoalTest(StdPackageTestCase):
    def test_constraint_goal_uses_it_template_and_substitutes_subject(self):
        constraint = sem.Constraint(
            subject=pm.val(pm.Anchor("std.types.Text")),
            term=pm.val(pm.Spec.of("std.types.Type")),
            target=pm.val(pm.Spec.of("std.types.Type")),
        )

        self.assertEqual(constraint.template_goal.anchor, expr.CONFORMS_FACT)
        self.assertEqual(constraint.template_goal.args.content[0], pm.Anchor("std.types.Text"))

        goal = constraint.goal_for(pm.Anchor("std.types.Text"))
        self.assertEqual(goal.anchor, expr.CONFORMS_FACT)
        self.assertEqual(goal.args.content[0], pm.Anchor("std.types.Text"))

    def test_spec_constraint_template_uses_typeof_over_subject_attr(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(core)

            mod facts
                def Choice[X: core.Text]
            """
        )

        contrib = next(iter(pkg.contributions("demo.facts.Choice", sem.EntityView.FactFacet)))
        templates_result = contrib.spec_constraint_templates
        self.assertFalse(templates_result.is_err)
        templates = cast(tuple[pm.Constraint, ...], templates_result.unwrap().fetch())
        self.assertEqual(len(templates), 1)
        subject = templates[0].subject.fetch()
        self.assertIsInstance(subject, urs.TypeOfOperator)
        assert isinstance(subject, urs.TypeOfOperator)
        self.assertIsInstance(subject.of_value.fetch(), urs.AttrOperator)


class SpecClusterTest(StdPackageTestCase):
    def test_entity_view_derives_structural_spec_clusters(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Choice[X]
                def Choice[Y]
            """
        )

        view = pkg.entity("demo.facts.Choice").for_(facet=sem.Entity.FactFacet)
        clusters = view.spec_clusters

        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0].contributions), 2)
        self.assertEqual(clusters[0].bucket.kind, "leaf")
        self.assertEqual(clusters[0].bucket.id, 0)


class EntityViewDispatchTest(StdPackageTestCase):
    def test_dispatch_resolves_unique_candidate_by_constraints(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types)

            mod facts
                def Choice[X: types.Text]
                def Choice[X: types.Natural]
            """
        )

        view = pkg.entity("demo.facts.Choice").for_(facet=sem.EntityView.FactFacet)
        spec = pm.Spec.of("demo.facts.Choice", **{"X": "hey"})

        with pkg.workspace:
            selected = view.dispatch(spec)

        self.assertEqual(selected.anchor, pm.Anchor("demo.facts.Choice"))
        self.assertEqual(str(selected.spec_bindings.fields[0].bound_expr), "types.Text")

    def test_dispatch_rejects_when_no_candidate_survives_constraints(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types)

            mod facts
                def Choice[X: types.Text]
                def Choice[X: types.Natural]
            """
        )

        view = pkg.entity("demo.facts.Choice").for_(facet=sem.EntityView.FactFacet)
        spec = pm.Spec.of("demo.facts.Choice", **{"X": True})

        with pkg.workspace, self.assertRaises(ValueError) as raised:
            view.dispatch(spec)

        self.assertIn("not admitted by constraints", str(raised.exception))
