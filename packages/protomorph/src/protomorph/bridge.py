from __future__ import annotations

from contextvars import ContextVar
from typing import Protocol, runtime_checkable

from protobase import Record, mutate

import protomorph as morph


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


class StructuralBridge(Record):
    def fields(self, type: morph.Type) -> morph.Struct[str, morph.Type] | None:
        _ = type
        return None

    def project(self, type: morph.Type, key: str | int) -> morph.Type:
        if isinstance(type, morph.NominalQualifier):
            return self.lift(type, self.project(type.underlying, key))

        if isinstance(type, morph.StructType):
            return _project_fields(type.meta_attrs, key)

        if isinstance(type, morph.NominalType):
            fields = self.fields(type)
            if fields is None:
                raise KeyError(f"No member {key!r} on opaque nominal type {type!r}")
            return _project_fields(fields, key)

        raise KeyError(f"No member {key!r} on type {type!r}")

    def lift(self, qualifier: morph.Qualifier, result: morph.Type) -> morph.Type:
        if isinstance(qualifier, morph.NominalQualifier):
            return mutate(qualifier, underlying=result)

        raise NotImplementedError(
            f"StructuralBridge.lift does not support qualifier {type(qualifier).__name__}"
        )

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
