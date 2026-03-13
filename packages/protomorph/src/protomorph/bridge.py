from __future__ import annotations

from contextvars import ContextVar, Token
from types import TracebackType
from typing import Protocol, Self, runtime_checkable
from weakref import WeakKeyDictionary

from protobase import Object, Record, mutate

import protomorph as morph

__all__ = [
    "SemanticBridge",
    "SemanticBridgeBase",
    "StructuralBridge",
    "DEFAULT_BRIDGE",
    "BRIDGE",
]


@runtime_checkable
class SemanticBridge(Protocol):
    def fields(self, type: morph.Type) -> morph.Struct[str, morph.Type] | None: ...

    def project(self, type: morph.Type, key: str | int) -> morph.Type: ...

    def lift(self, qualifier: morph.Qualifier, result: morph.Type) -> morph.Type: ...

    def combine(
        self,
        left: morph.Type,
        right: morph.Type,
        *,
        op: str | None = None,
    ) -> morph.Type: ...


class SemanticBridgeBase(Object, abstract=True):
    def fields(self, type: morph.Type) -> morph.Struct[str, morph.Type] | None:
        _ = type
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


class StructuralBridge(SemanticBridgeBase, Record):
    def fields(self, type: morph.Type) -> morph.Struct[str, morph.Type] | None:
        _ = type
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
            "StructuralBridge.combine is reserved for host semantic rules"
        )


def _project_type(
    bridge: SemanticBridge,
    type: morph.Type,
    key: str | int,
) -> morph.Type:
    if isinstance(type, morph.NominalQualifier):
        return bridge.lift(type, bridge.project(type.underlying, key))

    if isinstance(type, morph.StructType):
        return _project_fields(type.meta_attrs, key)

    if isinstance(type, morph.NominalType):
        fields = bridge.fields(type)
        if fields is None:
            raise KeyError(f"No member {key!r} on opaque nominal type {type!r}")
        return _project_fields(fields, key)

    raise KeyError(f"No member {key!r} on type {type!r}")


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
