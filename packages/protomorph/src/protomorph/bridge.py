from __future__ import annotations

from contextvars import ContextVar, Token
from types import TracebackType
from typing import Protocol, Self, runtime_checkable
from weakref import WeakKeyDictionary

from protobase import Consed, Inmutable, mutate

import protomorph as morph

__all__ = [
    "Layout",
    "AtomicLayout",
    "StructLayout",
    "SemanticBridge",
    "SemanticBridgeBase",
    "StructuralBridge",
    "DEFAULT_BRIDGE",
    "BRIDGE",
    "layout_of",
]


class Layout(Consed, abstract=True):
    pass


class AtomicLayout(Layout):
    valid_types: frozenset[type]


class StructLayout(Layout):
    fields: morph.Struct[str, morph.Type]
    builtin_cls: type[morph.Builtin] | None = None


@runtime_checkable
class SemanticBridge(Protocol):
    def layout(self, type: morph.Type) -> Layout | None: ...

    def project(self, type: morph.Type, key: str | int) -> morph.Type: ...

    def lift(self, qualifier: morph.Qualifier, result: morph.Type) -> morph.Type: ...

    def combine(
        self,
        left: morph.Type,
        right: morph.Type,
        *,
        op: str | None = None,
    ) -> morph.Type: ...


class SemanticBridgeBase(Inmutable, abstract=True):
    def layout(self, type: morph.Type) -> Layout | None:
        if isinstance(type, morph.NominalQualifier):
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

    def project(self, type: morph.Type, key: str | int) -> morph.Type:
        return _project_type(self, type, key)

    def lift(self, qualifier: morph.Qualifier, result: morph.Type) -> morph.Type:
        return _lift_qualifier(qualifier, result)

    def combine(
        self,
        left: morph.Type,
        right: morph.Type,
        *,
        op: str | None = None,
    ) -> morph.Type:
        _ = (left, right, op)
        raise NotImplementedError(
            f"{type(self).__name__}.combine is reserved for semantic-layer operator rules"
        )

    def __enter__(self) -> Self:
        tokens = _BRIDGE_TOKENS.setdefault(self, [])
        tokens.append(BRIDGE.set(self))
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
            BRIDGE.reset(token)


class StructuralBridge(SemanticBridgeBase, Consed):
    def project(self, type: morph.Type, key: str | int) -> morph.Type:
        return _project_type(self, type, key)

    def lift(self, qualifier: morph.Qualifier, result: morph.Type) -> morph.Type:
        return _lift_qualifier(qualifier, result)

    def combine(
        self,
        left: morph.Type,
        right: morph.Type,
        *,
        op: str | None = None,
    ) -> morph.Type:
        _ = (left, right, op)
        raise NotImplementedError(
            "StructuralBridge.combine is reserved for host semantic rules"
        )


def _project_type(
    bridge: SemanticBridge,
    type: morph.Type,
    key: str | int,
) -> morph.Type:
    layout = type.layout()
    if not isinstance(layout, StructLayout):
        raise KeyError(f"No member {key!r} on opaque type {type!r}")
    return _project_fields(layout.fields, key)


def _lift_qualifier(
    qualifier: morph.Qualifier,
    result: morph.Type,
) -> morph.Type:
    if isinstance(qualifier, morph.NominalQualifier):
        return mutate(qualifier, underlying=result)

    raise NotImplementedError(
        f"Cannot lift unsupported qualifier {type(qualifier).__name__}"
    )


def _project_fields(
    fields: morph.Struct[str, morph.Type],
    key: str | int,
) -> morph.Type:
    if isinstance(key, str):
        return fields.get(key)
    if isinstance(key, int):
        return fields[key]
    raise TypeError(f"Unsupported key type: {type(key)}")


DEFAULT_BRIDGE: SemanticBridge = StructuralBridge()

BRIDGE: ContextVar[SemanticBridge] = ContextVar(
    "protomorph.bridge.BRIDGE",
    default=DEFAULT_BRIDGE,
)

_BRIDGE_TOKENS: WeakKeyDictionary[SemanticBridgeBase, list[Token[SemanticBridge]]] = (
    WeakKeyDictionary()
)


def layout_of(type: morph.Type) -> Layout | None:
    bridge = BRIDGE.get(DEFAULT_BRIDGE)
    layout = bridge.layout(type)
    if layout is not None:
        return layout

    from .native import DEFAULT_NATIVE_REGISTRY

    return DEFAULT_NATIVE_REGISTRY.layout(type) if isinstance(type, morph.NominalType) else None
