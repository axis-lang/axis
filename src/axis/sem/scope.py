from __future__ import annotations

from typing import Optional

from protobase import Consed, frozendict

from axis import dom, expr, syn


class Scope(Consed):
    name: str | None
    parent: Optional["Scope"] = None
    bindings: frozendict[str, dom.Val] = frozendict()

    class Builder:
        def __init__(self, name: str | None = None, parent: Optional["Scope"] = None):
            self.name = name
            self.parent = parent
            self.bindings: dict[str, dom.Val] = {}

        def define(self, name: str, value: dom.Val) -> None:
            self.bindings[name] = value

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
                return dom.Err(message=f"Scope not found: {sym.at}", origin=sym)
            return scope._lookup_name(sym.name, origin=sym)
        return self._lookup_name(sym.name, origin=sym)

    def _lookup_name(self, name: str, origin: syn.Node) -> dom.Val:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent._lookup_name(name, origin=origin)
        return dom.Err(message=f"Unbound symbol: {name}", origin=origin)

    def _find_scope(self, name: str) -> Optional["Scope"]:
        current: Optional[Scope] = self
        while current is not None:
            if current.name == name:
                return current
            current = current.parent
        return None
