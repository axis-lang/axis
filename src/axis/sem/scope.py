from __future__ import annotations

from typing import Optional

from protobase import Consed, frozendict

from axis import dom, expr, src, syn


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
                diag = src.error(f"Name collision: {name}")
                primary_origin = sym if sym.span is not None else (origin or sym)
                primary_span = src.span_of(primary_origin)
                if primary_span is not None:
                    diag = diag.with_label(
                        src.Label(
                            span=primary_span,
                            message="conflicting definition",
                            style=src.LabelStyle.PRIMARY,
                        )
                    )
                previous_origin = self.origins.get(name)
                previous_span = (
                    src.span_of(previous_origin) if previous_origin is not None else None
                )
                if previous_span is not None:
                    diag = diag.with_label(
                        src.Label(
                            span=previous_span,
                            message="previous definition",
                            style=src.LabelStyle.SECONDARY,
                        )
                    )
                diag.emit()
                self.bindings[name] = dom.Err(diagnostic=diag)
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
                diag = src.error(f"Scope not found: {sym.at}")
                span = src.span_of(sym)
                if span is not None:
                    diag = diag.with_label(
                        src.Label(span=span, message="unknown scope")
                    )
                return dom.Err(diagnostic=diag)
            return scope._lookup_name(sym.name, origin=sym)
        return self._lookup_name(sym.name, origin=sym)

    def _lookup_name(self, name: str, origin: syn.Node) -> dom.Val:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent._lookup_name(name, origin=origin)
        diag = src.error(f"Unbound symbol: {name}")
        span = src.span_of(origin)
        if span is not None:
            diag = diag.with_label(src.Label(span=span, message="unbound symbol"))
        return dom.Err(diagnostic=diag)

    def _find_scope(self, name: str) -> Optional["Scope"]:
        current: Optional[Scope] = self
        while current is not None:
            if current.name == name:
                return current
            current = current.parent
        return None
