from axis import log

from tests.helpers import StdPackageTestCase, TestPackage


class ClaimContributionCheckTest(StdPackageTestCase):
    def test_claim_head_admitted_by_fact_facet_passes(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types, core)

            mod facts
                def Extends[X, from: types.Type]

            claim facts.Extends[core.Text, from: types.Type]
            """
        )

        with self.suppress_report_output():
            pkg.check()

    def test_claim_head_rejected_when_required_nominal_missing(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types, core)

            mod facts
                def Extends[X, from: types.Type]

            claim facts.Extends[core.Text]
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertIn(
            "Claim head is not admitted by any declared fact spec",
            str(raised.exception),
        )

    def test_rule_claim_body_goals_admitted_by_fact_facets_pass(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types, core)

            mod facts
                def Extends[X, from: types.Type]
                def Conforms[X, to: types.Type]

            claim facts.Extends[core.Text, from=types.Type]
            when:
                - facts.Conforms[core.Text, to=types.Type]
            """
        )

        with self.suppress_report_output():
            pkg.check()

    def test_rule_claim_body_goal_rejected_when_required_nominal_missing(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            use std(types, core)

            mod facts
                def Extends[X, from: types.Type]
                def Conforms[X, to: types.Type]

            claim facts.Extends[core.Text, from=types.Type]
            when:
                - facts.Conforms[core.Text]
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertIn(
            "Claim body goal is not admitted by any declared fact spec",
            str(raised.exception),
        )
