from __future__ import annotations

import unittest
from typing import ClassVar

import protomorph as pm

from axis import items, sem, syn
from axis.items.blocks.use import Use

from .package import TestPackage
from .sem import bound as sem_bound
from .sem import default as sem_default
from .sem import layout as sem_layout
from .sem import parse, project as sem_project, term as sem_term, type_bound as sem_type_bound


class SemanticTestCase(unittest.TestCase):
    pkg: ClassVar[TestPackage]

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "pkg"):
            cls.pkg = TestPackage.with_std()

    def expr(self, source: str) -> syn.Expr:
        return parse(source)

    def context(self, path: str) -> sem.Context:
        return self.pkg.context(path)

    def scope(self, path: str = "std") -> sem.Scope:
        return self.pkg.scope(path)

    def std_scope(self) -> sem.Scope:
        return self.scope("std")

    def core_scope(self) -> sem.Scope:
        return self.scope("std.core")

    def types_scope(self) -> sem.Scope:
        return self.scope("std.types")

    def qualifiers_scope(self) -> sem.Scope:
        return self.scope("std.qualifiers")

    def use_scope(self, *imports: str, base=None) -> sem.Scope:
        scope = self.resolve_scope(base)
        builder = sem.Scope.Builder(name=scope.name, parent=scope.parent)
        for name, value in scope.bindings.items():
            builder.define(name, value, origin=syn.Expr.from_str(name))

        namespaces = self.pkg.namespaces_by_anchor
        for import_spec in imports:
            use = self.parse_use(import_spec)
            use._contribute_to_scope(builder, namespaces)

        return builder.build()

    def parse_use(self, spec: str) -> Use:
        source = spec.strip()
        if source.startswith("use "):
            source = source[4:].strip()
        return Use(import_expr=syn.Expr.from_str(source))

    def resolve_scope(self, scope=None) -> sem.Scope:
        if scope is None:
            return self.std_scope()
        if isinstance(scope, sem.Scope):
            return scope
        if isinstance(scope, sem.Context):
            return scope.scope
        if isinstance(scope, str):
            stripped = scope.strip()
            if stripped.startswith("use ") or any(ch in stripped for ch in "(),"):
                return self.use_scope(stripped)
            return self.scope(stripped)
        raise TypeError(f"Unsupported scope reference: {scope!r}")

    def bound(self, source: str, scope=None) -> pm.Val:
        return sem_bound(source, self.resolve_scope(scope))

    def term(self, source: str, scope=None) -> pm.Val:
        return sem_term(source, self.resolve_scope(scope))

    def default(self, source: str, scope=None) -> pm.Val:
        return sem_default(source, self.resolve_scope(scope))

    def type_bound(self, source: str, scope=None) -> pm.Type:
        return sem_type_bound(source, self.resolve_scope(scope))

    def project(self, type_source: str, key: str | int, scope=None) -> pm.Type:
        with self.pkg:
            return sem_project(type_source, key, self.resolve_scope(scope), pkg=self.pkg)

    def layout(self, type_source: str, scope=None) -> pm.Layout | None:
        with self.pkg:
            return sem_layout(type_source, self.resolve_scope(scope), pkg=self.pkg)

    def _scope_desc(self, scope=None) -> str:
        resolved = self.resolve_scope(scope)
        return f"scope={resolved.name!r}"

    def _assert_semantic_equal(
        self,
        actual,
        expected,
        *,
        label: str,
        source: str,
        scope=None,
    ) -> None:
        self.assertEqual(
            actual,
            expected,
            msg=(
                f"{label} mismatch for {source!r} ({self._scope_desc(scope)})\n"
                f"actual:   {actual!r}\n"
                f"expected: {expected!r}"
            ),
        )

    def suppress_report_output(self):
        import contextlib
        import io

        return contextlib.redirect_stdout(io.StringIO())

    def assertBound(self, source: str, expected: pm.Val, scope=None) -> None:
        self._assert_semantic_equal(
            self.bound(source, scope),
            expected,
            label="bound",
            source=source,
            scope=scope,
        )

    def assertBoundEq(self, source: str, expected_source: str, scope=None) -> None:
        resolved_scope = self.resolve_scope(scope)
        self._assert_semantic_equal(
            self.bound(source, resolved_scope),
            self.bound(expected_source, resolved_scope),
            label=f"bound == {expected_source!r}",
            source=source,
            scope=resolved_scope,
        )

    def assertAnchor(self, source: str, path: str, scope=None) -> None:
        term = self.term(source, scope)
        self.assertIsInstance(
            term,
            pm.Anchor,
            msg=f"Expected anchor from {source!r} ({self._scope_desc(scope)}), got {term!r}",
        )
        assert isinstance(term, pm.Anchor)
        self.assertEqual(str(term), path)

    def assertType(self, source: str, expected: pm.Type, scope=None) -> None:
        self._assert_semantic_equal(
            self.type_bound(source, scope),
            expected,
            label="type",
            source=source,
            scope=scope,
        )

    def assertTypeEq(self, source: str, expected_source: str, scope=None) -> None:
        resolved_scope = self.resolve_scope(scope)
        self._assert_semantic_equal(
            self.type_bound(source, resolved_scope),
            self.type_bound(expected_source, resolved_scope),
            label=f"type == {expected_source!r}",
            source=source,
            scope=resolved_scope,
        )

    def assertProject(self, type_source: str, key: str | int, expected: pm.Type, scope=None) -> None:
        self._assert_semantic_equal(
            self.project(type_source, key, scope),
            expected,
            label=f"project[{key!r}]",
            source=type_source,
            scope=scope,
        )

    def assertProjectEq(self, type_source: str, key: str | int, expected_source: str, scope=None) -> None:
        resolved_scope = self.resolve_scope(scope)
        self._assert_semantic_equal(
            self.project(type_source, key, resolved_scope),
            self.type_bound(expected_source, resolved_scope),
            label=f"project[{key!r}] == {expected_source!r}",
            source=type_source,
            scope=resolved_scope,
        )

    def assertLayoutKeys(self, type_source: str, expected_keys: tuple[str | None, ...], scope=None) -> None:
        layout = self.layout(type_source, scope)
        self.assertIsInstance(layout, pm.StructLayout)
        assert isinstance(layout, pm.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), expected_keys)

    def assertSemanticError(self, source: str, scope=None) -> None:
        value = self.bound(source, scope)
        self.assertIsInstance(
            value,
            pm.Err,
            msg=f"Expected semantic error from {source!r} ({self._scope_desc(scope)}), got {value!r}",
        )

    def assertEntity(self, anchor: str) -> sem.Entity:
        entity = self.pkg.entity(anchor)
        self.assertIsNotNone(entity)
        return entity

    def assertContribution(self, anchor: str, cls: type | None = None):
        contributions = self.pkg.contributions(anchor, cls)
        self.assertTrue(contributions)
        return contributions[0]


class StdPackageTestCase(SemanticTestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = TestPackage.with_std()


class InlinePackageTestCase(SemanticTestCase):
    SOURCES: ClassVar[dict[str, str]] = {}
    EXTRA_UNITS: ClassVar[tuple[str, ...]] = ()
    EXTRA_DEFS: ClassVar[tuple[str, ...]] = ()
    DEFAULT_UNIT: ClassVar[str] = "test"

    @classmethod
    def setUpClass(cls):
        cls.pkg = TestPackage.from_sources(cls.SOURCES, with_std=True)
        for unit_source in cls.EXTRA_UNITS:
            cls.pkg = cls.pkg.with_unit(unit_source)
        for def_source in cls.EXTRA_DEFS:
            cls.pkg = cls.pkg.with_def(def_source, unit=cls.DEFAULT_UNIT)
