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

    def test_with_def_exposes_entity(self):
        entity = self.assertEntity("demo.Box")
        self.assertTrue(entity.contributions)


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

        contributions = pkg.contributions("demo.Maybe", sem.Entity.QualifierContribution)

        self.assertEqual(len(contributions), 1)
        self.assertIsInstance(contributions[0], sem.Entity.QualifierContribution)
