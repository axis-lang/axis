from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Any, Iterable, Self, cast

import protomorph as pm

from axis import Codebase, Workspace, items, sem, src


STD_CORE_PATH = Path("codebase/std-core")
STD_CORE_FILE = STD_CORE_PATH / "std.ax"


class TestPackage(items.Package):
    dir: src.SourceDir = src.SourceDir.from_path(STD_CORE_PATH)
    test_sources: frozenset[src.Source] = frozenset()

    @classmethod
    def from_sources(
        cls,
        sources: dict[str, str],
        *,
        with_std: bool = True,
    ) -> Self:
        test_sources: list[src.Source] = []
        if with_std:
            test_sources.append(
                src.SourceBuffer.from_str(
                    STD_CORE_FILE.read_text(encoding="utf-8"),
                    path=STD_CORE_FILE,
                )
            )

        for path, content in sources.items():
            test_sources.append(src.SourceBuffer.from_str(content, path=path))

        return cls(test_sources=frozenset(test_sources))

    @classmethod
    def with_std(
        cls,
        *units: str,
        names: tuple[str, ...] | None = None,
    ) -> Self:
        pkg = cls.from_sources({}, with_std=True)
        if not units:
            return pkg
        return pkg._with_units(units, names=names)

    @property
    def source_files(self) -> frozenset[src.Source]:  # type: ignore[override]
        return self.test_sources

    def with_unit(self, source: str, *, path: str | None = None) -> Self:
        return self._with_units((dedent(source),), names=(path,) if path is not None else None)

    def with_def(
        self,
        source: str,
        *,
        unit: str = "test",
        path: str | None = None,
    ) -> Self:
        unit_source = f"unit {unit}\n{dedent(source).strip()}\n"
        return self.with_unit(unit_source, path=path)

    def parse_def[D: items.Def](
        self,
        def_cls: type[D],
        source: str,
    ) -> D:
        node = items.Def.from_src(dedent(source), package=self)[0]
        assert node is not None
        assert isinstance(node, def_cls)
        return cast(D, node)

    def parse_any_def(
        self,
        source: str,
    ) -> items.Def:
        node = items.Def.from_src(dedent(source), package=self)[0]
        assert node is not None
        assert isinstance(node, items.Def)
        return node

    def unit(self, path: str = "std") -> items.Unit:
        anchor = pm.Anchor(path)
        for ctx in self.workspace.all_contexts:
            if isinstance(ctx, items.Unit) and cast(Any, ctx).anchor == anchor:
                return ctx
        raise KeyError(f"Unit {path!r} not found")

    def context(self, path: str) -> sem.Context:
        anchor = pm.Anchor(path)
        for ctx in self.workspace.all_contexts:
            if cast(Any, ctx).anchor == anchor:
                return ctx
        raise KeyError(f"Context {path!r} not found")

    def scope(self, path: str = "std") -> sem.Scope:
        return self.context(path).scope

    def entity(self, anchor: str) -> sem.Entity:
        return self.workspace[anchor]

    def contributions(
        self,
        anchor: str,
        cls: type | None = None,
    ) -> tuple[sem.Context.Contribution, ...]:
        target = pm.Anchor(anchor)
        return tuple(
            contrib
            for contrib in self.workspace.all_contributions
            if contrib.anchor == target and (cls is None or isinstance(contrib, cls))
        )

    @property
    def workspace(self) -> Workspace:
        codebase = self.codebase
        if not isinstance(codebase, Codebase):
            codebase = Codebase.from_path(STD_CORE_PATH.parent)
        return Workspace(codebase=codebase, roots=(self,))

    @property
    def all_contributions(self):
        return self.workspace.all_contributions

    @property
    def all_facts(self):
        return self.workspace.all_facts

    @property
    def entities_by_anchor(self):
        return self.workspace.entities_by_anchor

    @property
    def namespaces_by_anchor(self):
        return self.workspace.namespaces_by_anchor

    @property
    def logic_solver(self):
        return self.workspace.logic_solver

    def check(self) -> None:
        workspace = self.workspace
        with workspace:
            for context in workspace.all_contexts:
                context.check()
            for contribution in workspace.all_contributions:
                contribution.check()
            for entity in workspace.all_entities:
                entity.check()

    def _with_units(
        self,
        units: Iterable[str],
        *,
        names: tuple[str, ...] | None = None,
    ) -> Self:
        existing = list(self.test_sources)
        next_index = len(existing)
        inline_sources: list[src.Source] = []

        for offset, unit_source in enumerate(units):
            path = names[offset] if names is not None else f"<test:{next_index + offset}.ax>"
            inline_sources.append(src.SourceBuffer.from_str(unit_source, path=path))

        return type(self)(test_sources=frozenset((*existing, *inline_sources)))
