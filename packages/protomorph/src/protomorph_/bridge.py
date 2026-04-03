from __future__ import annotations

from collections.abc import Iterable
from contextvars import Token
from types import TracebackType
from typing import Protocol, Self, runtime_checkable
from weakref import WeakKeyDictionary

from protobase import Consed, Inmutable, mutate

import protomorph_ as pm

__all__ = [
    "Layout",
    "AtomicLayout",
    "StructLayout",
    "SemanticBridge",
    "SemanticBridgeBase",
    "StructuralBridge",
    "layout_of",
]


class Layout(Consed, abstract=True):
    pass


class AtomicLayout(Layout):
    valid_types: frozenset[type]


class StructLayout(Layout):
    fields: pm.Struct[str, pm.Type]
    builtin_cls: type[pm.Builtin] | None = None


@runtime_checkable
class SemanticBridge(Protocol):
    def layout(self, type: pm.Type) -> Layout | None: ...

    def view(self, trait: pm.Spec, value: pm.Val) -> tuple[pm.Val, ...]: ...

    def solve(self, goal: pm.Spec, state: pm.MatchState) -> Iterable[pm.MatchState]: ...

    def project(self, type: pm.Type, key: str | int) -> pm.Type: ...

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type: ...

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type: ...


class SemanticBridgeBase(Inmutable, abstract=True):
    def layout(self, type: pm.Type) -> Layout | None:
        if isinstance(type, pm.NominalQualifier):
            underlying_layout = type.underlying.layout()
            if underlying_layout is None:
                return None
            if isinstance(underlying_layout, AtomicLayout):
                return AtomicLayout(valid_types=underlying_layout.valid_types)
            assert isinstance(underlying_layout, StructLayout)
            return StructLayout(
                fields=underlying_layout.fields.map(
                    lambda field_type: self.lift(type, field_type)
                ),
                builtin_cls=underlying_layout.builtin_cls,
            )
        return None

    def view(self, trait: pm.Spec, value: pm.Val) -> tuple[pm.Val, ...]:
        if trait.path == "std.traits.Type":
            resolved = value.as_type()
            return () if resolved is None else (pm.val(resolved),)
        return ()

    def solve(
        self,
        goal: pm.Spec,
        state: pm.MatchState,
    ) -> Iterable[pm.MatchState]:
        solver = getattr(self, "logic_solver", None)
        if solver is None:
            return ()
        return solver.answers(goal, state)

    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        return _project_type(self, type, key)

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        return _lift_qualifier(qualifier, result)

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type:
        _ = (left, right, op)
        raise NotImplementedError(
            f"{type(self).__name__}.combine is reserved for semantic-layer operator rules"
        )

    def __enter__(self) -> Self:
        tokens = _BRIDGE_TOKENS.setdefault(self, [])
        tokens.append(pm.BRIDGE.set(self))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        _ = (exc_type, exc, tb)
        tokens = _BRIDGE_TOKENS.get(self)
        if not tokens:
            return

        token = tokens.pop()
        if not tokens:
            _BRIDGE_TOKENS.pop(self, None)

        if token is not None:
            pm.BRIDGE.reset(token)


class StructuralBridge(SemanticBridgeBase, Consed):
    def project(self, type: pm.Type, key: str | int) -> pm.Type:
        return _project_type(self, type, key)

    def lift(self, qualifier: pm.Qualifier, result: pm.Type) -> pm.Type:
        return _lift_qualifier(qualifier, result)

    def combine(
        self,
        left: pm.Type,
        right: pm.Type,
        *,
        op: str | None = None,
    ) -> pm.Type:
        _ = (left, right, op)
        raise NotImplementedError(
            "StructuralBridge.combine is reserved for host semantic rules"
        )


def _project_type(
    bridge: SemanticBridge,
    type: pm.Type,
    key: str | int,
) -> pm.Type:
    layout = type.layout()
    if not isinstance(layout, StructLayout):
        raise KeyError(f"No member {key!r} on opaque type {type!r}")
    return _project_fields(layout.fields, key)


def _lift_qualifier(
    qualifier: pm.Qualifier,
    result: pm.Type,
) -> pm.Type:
    if isinstance(qualifier, pm.NominalQualifier):
        return mutate(qualifier, underlying=result)

    raise NotImplementedError(
        f"Cannot lift unsupported qualifier {type(qualifier).__name__}"
    )


def _project_fields(
    fields: pm.Struct[str, pm.Type],
    key: str | int,
) -> pm.Type:
    if isinstance(key, str):
        return fields.get(key)
    if isinstance(key, int):
        return fields[key]
    raise TypeError(f"Unsupported key type: {type(key)}")

_BRIDGE_TOKENS: WeakKeyDictionary[SemanticBridgeBase, list[Token[SemanticBridge]]] = (
    WeakKeyDictionary()
)


def layout_of(type: pm.Type) -> Layout | None:
    bridge = pm.BRIDGE.get(pm.DEFAULT_BRIDGE)

    layout = bridge.layout(type)
    if layout is not None:
        return layout

    return pm.NATIVE_REGISTRY.layout(type) if isinstance(type, pm.NominalType) else None
