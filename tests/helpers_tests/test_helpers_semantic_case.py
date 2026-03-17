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

        contributions = pkg.contributions("demo.Maybe", sem.Entity.QualContribution)

        self.assertEqual(len(contributions), 1)
        self.assertIsInstance(contributions[0], sem.Entity.QualContribution)
