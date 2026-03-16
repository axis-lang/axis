import unittest

import protomorph as pm

from axis import expr, items, sem
from axis.expr.ir import Scope


class SemanticBridgeMigrationTest(unittest.TestCase):
    def test_realm_installs_pm_bridge_context(self):
        pkg = items.Package.from_path("codebase/std-core")
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
        pkg = items.Package.from_path("codebase/std-core")

        self.assertGreater(len(pkg.entities_by_anchor), 0)
        self.assertGreater(len(pkg.namespaces_by_anchor), 0)

    def test_mods_emit_namespace_contributions(self):
        pkg = items.Package.from_path("codebase/std-core")

        namespace_anchors = {
            contrib.anchor
            for contrib in pkg.all_contributions
            if isinstance(contrib, sem.Context.NamespaceContribution)
        }

        self.assertIn(pm.anchor("std"), namespace_anchors)
        self.assertIn(pm.anchor("std.Ref"), namespace_anchors)
        self.assertIn(pm.anchor("std.Nominal"), namespace_anchors)

    def test_context_scopes_use_expr_ir_scope(self):
        pkg = items.Package.from_path("codebase/std-core")

        self.assertTrue(all(isinstance(ctx.scope, Scope) for ctx in pkg.all_contexts))

    def test_realm_exposes_layout_contract_not_fields(self):
        pkg = items.Package.from_path("codebase/std-core")

        self.assertTrue(hasattr(pkg, "layout"))
        self.assertFalse(hasattr(pkg, "fields"))

    def test_realm_layout_returns_none_without_matching_nominal_overload(self):
        pkg = items.Package.from_path("codebase/std-core")

        self.assertIsNone(pkg.layout(pm.nominal_type("std.Struct", pm.spec(I=pm.nominal_type("std.Sym")))))

    def test_realm_project_uses_semantic_structure_when_available(self):
        pkg = items.Package.from_path("codebase/std-core")

        projected = pkg.project(pm.nominal_type("std.Struct.Type", pm.spec(I=pm.TEXT_TYPE)), "meta_attrs")

        self.assertEqual(
            projected,
            pm.nominal_qual(
                "std.Struct",
                pm.spec(pm.TEXT_TYPE),
                underlying=pm.nominal_type("std.Type"),
            ),
        )

    def test_realm_lift_rebuilds_nominal_qualifier_with_new_underlying(self):
        pkg = items.Package.from_path("codebase/std-core")
        qualifier = pm.nominal_qual("std.Optional", pm.spec(), underlying=pm.TEXT_TYPE)

        lifted = pkg.lift(qualifier, pm.INTEGER_TYPE)

        self.assertEqual(lifted, pm.nominal_qual("std.Optional", pm.spec(), underlying=pm.INTEGER_TYPE))

    def test_realm_project_lifts_through_nominal_qualifiers(self):
        pkg = items.Package.from_path("codebase/std-core")
        qualifier = pm.nominal_qual("std.Optional", pm.spec(), underlying=pm.nominal_type("std.Struct.Type", pm.spec(I=pm.TEXT_TYPE)))

        projected = pkg.project(qualifier, "meta_attrs")

        self.assertEqual(
            projected,
            pm.nominal_qual(
                "std.Optional",
                pm.spec(),
                underlying=pm.nominal_qual(
                    "std.Struct",
                    pm.spec(pm.TEXT_TYPE),
                    underlying=pm.nominal_type("std.Type"),
                ),
            ),
        )

    def test_realm_projects_nominal_metatype_spec_ref_semantically(self):
        pkg = items.Package.from_path("codebase/std-core")

        projected = pkg.project(
            pm.nominal_type("std.Nominal.Type", pm.spec(S=pm.TEXT_TYPE)),
            "spec_ref",
        )

        self.assertEqual(
            projected,
            pm.nominal_type("std.Ref.Spec.Type", pm.spec(pm.TEXT_TYPE)),
        )

    def test_realm_projects_qualifier_metatype_fields_semantically(self):
        pkg = items.Package.from_path("codebase/std-core")
        qualifier_meta = pm.type_of(
            pm.val(pm.nominal_qual("std.Optional", pm.spec(), underlying=pm.TEXT_TYPE))
        ).data
        assert isinstance(qualifier_meta, pm.Type)

        self.assertEqual(
            pkg.project(qualifier_meta, "spec_ref"),
            pm.nominal_type("std.Ref.Spec.Type", pm.spec(pm.spec())),
        )
        self.assertEqual(
            pkg.project(qualifier_meta, "underlying"),
            pm.nominal_type("std.Nominal.Type"),
        )

    # def test_contributions_expose_bound_and_default_structs(self):
    #     pkg = items.Package.from_path("codebase/std-core")

    #     contribution = next(
    #         contrib
    #         for contrib in pkg.all_contributions
    #         if hasattr(contrib, "spec_bounds") and hasattr(contrib, "spec_defaults")
    #     )

    #     self.assertIsNotNone(contribution.spec_bounds)
    #     self.assertIsNotNone(contribution.spec_defaults)


if __name__ == "__main__":
    unittest.main()
