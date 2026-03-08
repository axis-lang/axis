from __future__ import annotations

from typing import Optional

from protobase import Consed, frozendict, Record

from axis import dom, expr, syn
from axis.log import report as log


class Scope(Consed):
    name: str | None
    parent: Optional["Scope"] = None
    bindings: frozendict[str, dom.Val] = frozendict()

    class Builder(Record):
        name: str | None = None
        parent: Scope | None = None
        bindings: dict[str, dict[dom.Val, set[syn.Node]]] = {}

        def define(
            self,
            name: str,
            value: dom.Val,
            *,
            origin: syn.Node,
        ) -> None:
            self.bindings.setdefault(name, {}).setdefault(value, set()).add(origin)

        def build(self) -> "Scope":
            bindings: dict[str, dom.Val] = {}
            for name, val_by_origin in self.bindings.items():
                first, *more = val_by_origin.keys()
                if more:
                    report = log.error(f"Name conflict: {name}")
                    for val, origins in val_by_origin.items():
                        report.labels(origins, f"conflicting definition: {val}")
                    bindings[name] = report.emit().tag(dom.Err())
                else:
                    bindings[name] = first

            return Scope(
                name=self.name,
                parent=self.parent,
                bindings=frozendict(bindings),
            )

    def lookup(self, sym: expr.Sym) -> dom.Val:
        if sym.at:
            scope = _find_scope(self, sym.at)
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

def _find_scope(current: Scope | None, name: str) -> Optional["Scope"]:
    #current: Optional[Scope] = self
    while current is not None:
        if current.name == name:
            return current
        current = current.parent
    return None
