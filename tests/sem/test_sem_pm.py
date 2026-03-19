import protomorph as pm

from axis import expr, items, sem
from axis.expr.ir import Scope

from tests.helpers import StdPackageTestCase


class SemanticBridgeMigrationTest(StdPackageTestCase):
    def assertSemanticLayoutDisabled(self, fn):
        with self.assertRaises(RuntimeError) as cm:
            fn()
        self.assertIn("Semantic layout disabled", str(cm.exception))

    def test_realm_installs_pm_bridge_context(self):
        try:
            before = pm.BRIDGE.get()
        except LookupError:
            before = None

        with self.pkg:
            self.assertIs(pm.BRIDGE.get(), self.pkg)

        if before is None:
            with self.assertRaises(LookupError):
                pm.BRIDGE.get()
        else:
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
        self.assertGreater(len(self.pkg.entities_by_anchor), 0)
        self.assertGreater(len(self.pkg.namespaces_by_anchor), 0)

    def test_mods_emit_namespace_contributions(self):
        namespace_anchors = {
            contrib.anchor
            for contrib in self.pkg.all_contributions
            if isinstance(contrib, sem.Context.NamespaceContribution)
        }

        self.assertIn(pm.anchor("std"), namespace_anchors)
        self.assertIn(pm.anchor("std.types"), namespace_anchors)
        self.assertIn(pm.anchor("std.qualifiers"), namespace_anchors)

    def test_context_scopes_use_expr_ir_scope(self):
        self.assertTrue(all(isinstance(ctx.scope, Scope) for ctx in self.pkg.all_contexts))

    def test_realm_exposes_layout_contract_not_fields(self):
        self.assertTrue(hasattr(self.pkg, "layout"))
        self.assertFalse(hasattr(self.pkg, "fields"))

    def test_realm_layout_returns_none_without_matching_nominal_overload(self):
        with self.pkg:
            self.assertIsNone(self.pkg.layout(self.type_bound("qualifiers.Struct[core.Sym]")))

    def test_realm_project_reports_semantic_layout_disabled(self):
        self.assertSemanticLayoutDisabled(
            lambda: self.assertProjectEq(
                "types.StructType[core.Text]",
                "meta_attrs",
                "qualifiers.Struct[core.Text] types.Type",
            )
        )

    def test_realm_lift_rebuilds_nominal_qualifier_with_new_underlying(self):
        qualifier = self.type_bound("qualifiers.Optional core.Text")
        assert isinstance(qualifier, pm.NominalQualifier)

        lifted = self.pkg.lift(qualifier, pm.INTEGER_TYPE)

        self.assertEqual(
            lifted,
            self.type_bound("qualifiers.Optional core.Integer"),
        )

    def test_realm_project_lifts_through_nominal_qualifiers_is_disabled(self):
        qualifier = self.type_bound("qualifiers.Optional types.StructType[core.Text]")

        self.assertSemanticLayoutDisabled(
            lambda: self.pkg.project(qualifier, "meta_attrs")
        )

    def test_realm_projects_nominal_metatype_spec_ref_is_disabled(self):
        self.assertSemanticLayoutDisabled(
            lambda: self.pkg.project(
                self.type_bound("types.NominalType[core.Text]"),
                "spec_ref",
            )
        )

    def test_realm_projects_qualifier_metatype_fields_are_disabled(self):
        qualifier_meta = pm.type_of(
            pm.val(self.type_bound("qualifiers.Optional core.Text"))
        ).data
        assert isinstance(qualifier_meta, pm.Type)

        self.assertSemanticLayoutDisabled(
            lambda: self.pkg.project(qualifier_meta, "spec_ref")
        )
        self.assertSemanticLayoutDisabled(
            lambda: self.pkg.project(qualifier_meta, "underlying")
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
