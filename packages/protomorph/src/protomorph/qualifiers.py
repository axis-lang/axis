from __future__ import annotations

from typing import ClassVar, cast

from protobase import Missing, MissingType

import protomorph as morph

from .types import Data, Type

__all__ = ["Qualifier", "NominalQualifier"]


class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "dom.Qual"

    underlying: Type

    @property
    def is_meta(self) -> bool:
        return self.underlying.is_meta


class NominalQualifier(Qualifier):
    ANCHOR: ClassVar[str] = "dom.Qual.Nominal"

    spec_ref: morph.Spec

    def _metaspec(self):
        spec_args = self.spec_ref._args_const()
        return morph.struct(
            S=cast(morph.Const, spec_args if spec_args else morph.val(None)),
            U=cast(morph.Const, morph.val(self.underlying._metatype())),
        )

    def _dir(self, data: Data | MissingType = Missing) -> morph.Struct[str, Type] | None:
        _ = data
        bridge = morph.BRIDGE.get(morph.DEFAULT_BRIDGE)
        fields = self.underlying._dir(Missing)
        if fields is None:
            return None
        return fields.map(lambda field_type: bridge.lift(self, field_type))

    def _get(self, data: Data, key: str | int) -> morph.Val:
        _ = (data, key)
        raise NotImplementedError(
            "NominalQualifier._get remains undefined for value projection; use SemanticBridge.project for type-level semantics"
        )

    def _encode(self, data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._encode is not implemented in protomorph core")

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._decode is not implemented in protomorph core")
