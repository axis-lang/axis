from __future__ import annotations

from typing import Optional

from protobase import Consed, frozendict

from axis import dom, expr, syn
from axis.log import report as log


class Scope(Consed):
    name: str | None
    parent: Optional["Scope"] = None
    bindings: frozendict[str, dom.Val] = frozendict()

    class Builder:
        def __init__(self, name: str | None = None, parent: Optional["Scope"] = None):
            self.name = name
            self.parent = parent
            self.bindings: dict[str, dom.Val] = {}
            self.origins: dict[str, syn.Node] = {}

        def define(
            self,
            sym: expr.Sym,
            value: dom.Val,
            *,
            origin: syn.Node | None = None,
        ) -> None:
            name = sym.name
            if name in self.bindings:
                report = log.error(f"Name collision: {name}")
                primary_origin = sym if sym.span is not None else (origin or sym)
                report = report.label(
                    primary_origin,
                    "conflicting definition",
                    style=log.Report.LabelStyle.PRIMARY,
                )
                previous_origin = self.origins.get(name)
                if previous_origin is not None:
                    report = report.label(
                        previous_origin,
                        "previous definition",
                        style=log.Report.LabelStyle.SECONDARY,
                    )
                report.emit()
                self.bindings[name] = dom.Err(diagnostic=report.build())
                return

            self.bindings[name] = value
            if origin is None:
                origin = sym
            self.origins.setdefault(name, origin)

        def extend(self, parent: Optional["Scope"]) -> None:
            self.parent = parent

        def build(self) -> "Scope":
            return Scope(
                name=self.name,
                parent=self.parent,
                bindings=frozendict(self.bindings),
            )

    def lookup(self, sym: expr.Sym) -> dom.Val:
        if sym.at:
            scope = self._find_scope(sym.at)
            if scope is None:
                return (
                    log.error(f"Scope not found: {sym.at}")
                    .label(sym, "unknown scope")
                    .tag(dom.Err())
                )
            return scope._lookup_name(sym.name, origin=sym)
        return self._lookup_name(sym.name, origin=sym)

    def _lookup_name(self, name: str, origin: syn.Node) -> dom.Val:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent._lookup_name(name, origin=origin)
        return (
            log.error(f"Unbound symbol: {name}")
            .label(origin, "unbound symbol")
            .tag(dom.Err())
        )

    def _find_scope(self, name: str) -> Optional["Scope"]:
        current: Optional[Scope] = self
        while current is not None:
            if current.name == name:
                return current
            current = current.parent
        return None
