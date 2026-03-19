import protomorph as pm

from axis import items, sem

from tests.helpers import InlinePackageTestCase, TestPackage


class TestPackageHelperTest(InlinePackageTestCase):
    EXTRA_DEFS = (
        """
        def Box[T](value)
        where:
            val T: types.Type
        takes:
            val value: T
        """,
    )
    DEFAULT_UNIT = "demo"

    def test_with_def_injects_unit_wrapped_definition(self):
        entity = self.assertEntity("demo.Box")

        self.assertAnchor("Box", "demo.Box", scope=self.scope("demo"))
        self.assertTrue(entity.contributions)

    def test_inline_package_exposes_injected_unit_scope(self):
        demo_scope = self.scope("demo")

        self.assertAnchor("Box", "demo.Box", scope=demo_scope)

    def test_assert_type_eq_uses_semantic_string_comparison(self):
        self.assertTypeEq(
            "Box[core.Text]",
            "Box[core.Text]",
            scope="use demo(Box), std(core)",
        )

    def test_assert_type_eq_supports_nested_qualifier_compounds(self):
        self.assertTypeEq(
            "qualifiers.Optional qualifiers.Struct[core.Text] types.Type",
            "qualifiers.Optional qualifiers.Struct[core.Text] types.Type",
        )


class UseScopeHelperTest(InlinePackageTestCase):
    SOURCES = {
        "demo.ax": """
        unit demo
        mod values
            def Alias
            takes:
                val value: core.Text
        """
    }

    def test_use_scope_supports_alias_assignment_shape(self):
        scope = self.use_scope("demo(values=values)", "std(core=core)")

        self.assertAnchor("values", "demo.values", scope=scope)
        self.assertAnchor("core", "std.core", scope=scope)


class TestPackageApiSmokeTest(InlinePackageTestCase):
    def test_spec_index_empty_tree_behaves(self):
        index = sem.SpecIndex(contribs=frozenset())

        self.assertIsNone(index.tree)
        self.assertFalse(index.exists(pm.Struct.Empty))
        self.assertEqual(index.match(pm.Struct.Empty), frozenset())

    def test_test_package_parse_def_uses_std_core_base(self):
        pkg = TestPackage.with_std()
        node = pkg.parse_def(
            items.QualDef,
            """
            def Optional T
            where:
                val T: types.Type
            """
        )

        self.assertIsInstance(node, items.QualDef)

    def test_test_package_contributions_filter_by_type(self):
        pkg = TestPackage.with_std().with_def(
            """
            def Maybe T
            where:
                val T: types.Type
            """,
            unit="demo",
        )

        contributions = pkg.contributions("demo.Maybe", sem.Entity.QualifierContribution)

        self.assertEqual(len(contributions), 1)
        self.assertIsInstance(contributions[0], sem.Entity.QualifierContribution)

    def test_entity_exposes_spec_tree_and_overload_facets(self):
        pkg = TestPackage.with_std().with_def(
            """
            def Box[T](value)
            where:
                val T: types.Type
            takes:
                val value: T
            """,
            unit="demo",
        )

        entity = pkg.entity("demo.Box")

        self.assertTrue(entity.spec_index.facet(sem.Entity.OverloadContribution))
        self.assertTrue(entity.facet(sem.Entity.ClassFacet))

    def test_entity_exposes_predicate_facets(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        self.assertTrue(entity.spec_index.facet(sem.Entity.PredicateFacet))

    def test_entity_match_specs_can_select_predicate_facets(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        matched = entity.match_specs(
            pm.spec_ref("demo.facts.Extends", pm.struct(pm.literal(1), **{"from": pm.literal(2)})),
            sem.Entity.PredicateFacet,
        )
        self.assertEqual(len(matched), 1)

    def test_entity_match_specs_rejects_wrong_anchor(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        matched = entity.match_specs(
            pm.spec_ref("demo.facts.Other", pm.struct(pm.literal(1), **{"from": pm.literal(2)})),
            sem.Entity.PredicateFacet,
        )

        self.assertEqual(matched, frozenset())

    def test_entity_spec_match_tree_exposes_goal_buckets(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
                def Implements[X, trait=T]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        assert entity.spec_index.tree is not None
        self.assertTrue(entity.spec_index.tree.goals)

    def test_spec_index_search_exposes_goal_buckets_and_envs(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        entity = pkg.entity("demo.facts.Extends")
        result = entity.search_specs(
            pm.spec_ref("demo.facts.Extends", pm.struct(pm.literal(1), **{"from": pm.literal(2)})),
            sem.Entity.PredicateFacet,
        )

        self.assertEqual(len(result.goals), 1)
        self.assertEqual(len(result.goal_buckets), 1)
        self.assertTrue(result.leaves)
        self.assertEqual(len(result.envs_by_goal), 1)
        goal = next(iter(result.goals))
        self.assertEqual(result.envs_by_goal[goal][0].bindings, pm.frozendict())

    def test_entity_exists_spec_reports_predicate_membership(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
            """
        )

        entity = pkg.entity("demo.facts.Extends")

        self.assertTrue(
            entity.exists_spec(
                pm.spec_ref("demo.facts.Extends", pm.struct(pm.literal(1), **{"from": pm.literal(2)})),
                sem.Entity.PredicateFacet,
            )
        )
