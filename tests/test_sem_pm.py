import unittest

import protomorph as pm

from axis import expr, items
from axis.expr.ir import Scope


class SemanticBridgeMigrationTest(unittest.TestCase):
    def test_realm_installs_pm_bridge_context(self):
        pkg = items.Package.from_path("codebase/std.core")
        before = pm.BRIDGE.get()

        with pkg:
            self.assertIs(pm.BRIDGE.get(), pkg)

        self.assertIs(pm.BRIDGE.get(), before)

    def test_use_entries_resolve_nested_anchor_scope(self):
        use = items.blocks.Use(
            import_expr=expr.Apply(
                function=expr.Sym(name="std"),
                argument=expr.Tuple(
                    elements=(
                        expr.Tuple.Positional(value=expr.Sym(name="foo")),
                    )
                ),
            )
        )

        self.assertEqual(
            use.entries,
            frozenset({(expr.Sym(name="foo"), pm.anchor("std.foo"))}),
        )

    def test_database_build_still_works_with_pm_semantics(self):
        pkg = items.Package.from_path("codebase/std.core")

        self.assertGreater(len(pkg.entities_by_anchor), 0)
        self.assertGreater(len(pkg.namespaces_by_anchor), 0)

    def test_context_scopes_use_expr_ir_scope(self):
        pkg = items.Package.from_path("codebase/std.core")

        self.assertTrue(all(isinstance(ctx.scope, Scope) for ctx in pkg.all_contexts))

    def test_contributions_expose_bound_and_default_structs(self):
        pkg = items.Package.from_path("codebase/std.core")

        contribution = next(
            contrib
            for contrib in pkg.all_contributions
            if hasattr(contrib, "spec_bounds") and hasattr(contrib, "spec_defaults")
        )

        self.assertIsNotNone(contribution.spec_bounds)
        self.assertIsNotNone(contribution.spec_defaults)


if __name__ == "__main__":
    unittest.main()
