import protomorph as pm

from axis import items, log, sem

from tests.helpers import InlinePackageTestCase, TestPackage


class ClaimFrontendTest(InlinePackageTestCase):
    SOURCES = {
        "demo.ax": """
        unit demo

        mod facts
            def Extends[X, from=Y]
            def Conforms[X, to=T]
            def Transitive[of=R]

        def Natural
        def Integer
        extends Natural
        def Text
        extends Integer

        claim facts.Transitive[of=facts.Extends]
        claim facts.Extends[Text, from=Integer]
        claim facts.Extends[Integer, from=Natural]

        claim facts.Conforms[X, to=T]
        where:
            val X
            val T
        when:
            - facts.Extends[X, from=T]

        claim facts.Conforms[X, to=T]
        where:
            val X
            val U
            val T
        when:
            - facts.Extends[X, from=U]
            - facts.Conforms[U, to=T]
        """
    }

    def test_empirical_claim_emits_fact_contribution(self):
        contrib = next(iter(self.pkg.contributions("demo.facts.Transitive", sem.Context.ClaimContribution)))

        self.assertIsInstance(contrib, sem.Context.ClaimContribution)
        self.assertEqual(len(contrib.facts), 1)
        self.assertFalse(contrib.clauses)
        fact = next(iter(contrib.facts))
        self.assertEqual(fact.anchor.path, "demo.facts.Transitive")

    def test_conditional_claim_emits_clause_contribution(self):
        contribs = tuple(self.pkg.contributions("demo.facts.Conforms", sem.Context.ClaimContribution))
        contrib = next(contrib for contrib in contribs if contrib.clauses)

        self.assertEqual(sum(len(contrib.clauses) for contrib in contribs), 2)
        clause = next(
            clause
            for contrib in contribs
            for clause in contrib.clauses
            if len(clause.body) == 1
        )
        self.assertEqual(clause.head.anchor.path, "demo.facts.Conforms")
        self.assertEqual(clause.body[0].anchor.path, "demo.facts.Extends")

    def test_where_constraints_emit_implicit_conforms_goals(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Conforms[X, to=T]
                def Uses[T]

            def Integer

            claim facts.Uses[T]
            where:
                val T: Integer
            """
        )

        contrib = next(iter(pkg.contributions("demo.facts.Uses", sem.Context.ClaimContribution)))
        clause = next(iter(contrib.clauses))

        self.assertEqual(clause.head.anchor.path, "demo.facts.Uses")
        self.assertEqual(len(clause.body), 1)
        self.assertEqual(clause.body[0].anchor.path, "std.facts.Conforms")

    def test_realm_aggregates_claim_facts_and_clauses(self):
        fact_anchors = {fact.anchor.path for fact in self.pkg.all_facts}
        clause_anchors = {clause.head.anchor.path for clause in self.pkg.all_clauses}

        self.assertIn("demo.facts.Transitive", fact_anchors)
        self.assertIn("demo.facts.Conforms", clause_anchors)

        conforms = self.pkg.entity("demo.facts.Conforms")
        transitive = self.pkg.entity("demo.facts.Transitive")

        self.assertTrue(conforms.clauses)
        self.assertTrue(transitive.facts)

    def test_logic_solver_derives_recursive_claims(self):
        goal = pm.spec_ref(
            "demo.facts.Conforms",
            pm.struct(
                pm.val(pm.nominal_type("demo.Text")),
                to=pm.val(pm.nominal_type("demo.Natural")),
            ),
        )

        answers = self.pkg.logic_solver.answers(goal)

        self.assertEqual(answers, (pm.MatchState(),))


class ClaimParsingSmokeTest(InlinePackageTestCase):
    def test_claim_item_parses_from_source(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]

            claim facts.Extends[A, from=B]
            where:
                val A
                val B
            """
        )

        claim = next(item for item in pkg.items if isinstance(item, items.Claim))

        self.assertIsInstance(claim, items.Claim)
        self.assertEqual(claim.anchor.path, "demo.facts.Extends")
        self.assertEqual(tuple(binding.binder_name for binding in claim.bindings.values), ("A", "B"))


class ClaimValidationTest(InlinePackageTestCase):
    def test_empirical_claim_rejects_head_not_admitted_by_predicate_spec(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]

            claim facts.Extends[from=Y]
            where:
                val Y
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertEqual(
            raised.exception.report.message,
            "Claim head is not admitted by any declared predicate spec",
        )

    def test_claim_rejects_undeclared_when_variable(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
                def Conforms[X, to=T]

            claim facts.Conforms[X, to=T]
            where:
                val X
                val T
            when:
                - facts.Extends[X, from=U]
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertEqual(
            raised.exception.report.message,
            "Claim references an unresolved symbol",
        )
        self.assertEqual(raised.exception.report.notes, ("Unbound symbol: U",))

    def test_claim_rejects_unrestricted_head_variable(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Extends[X, from=Y]
                def Conforms[X, to=T]

            claim facts.Conforms[X, to=T]
            where:
                val X
                val U
                val T
            when:
                - facts.Extends[X, from=U]
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertEqual(
            raised.exception.report.message,
            "Conditional claim must be range-restricted",
        )

    def test_claim_rejects_where_defaults_for_now(self):
        pkg = TestPackage.with_std().with_unit(
            """
            unit demo

            mod facts
                def Uses[T]

            claim facts.Uses[T]
            where:
                val T: Integer = Integer
            """
        )

        with self.suppress_report_output(), self.assertRaises(log.Report.Exception) as raised:
            pkg.check()

        self.assertEqual(
            raised.exception.report.message,
            "Claim where bindings do not support defaults yet",
        )
