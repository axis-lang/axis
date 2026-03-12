from __future__ import annotations

from typing import ClassVar, cast

from protobase import Missing, MissingType

from axis import dom

from .types import Data, Type

__all__ = ["Qualifier", "NominalQualifier"]


class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "dom.Qual"

    underlying: Type

    @property
    def is_meta(self) -> bool:
        return self.underlying.is_meta


class NominalQualifier(Qualifier):
    """
    def dom.Qual.Nominal[..S, U](..super, spec_ref: Ref.Spec[..S])
    extends dom.Qual[U]
    """

    ANCHOR: ClassVar[str] = "dom.Qual.Nominal"

    spec_ref: dom.Spec

    def _metaspec(self):
        s = self.spec_ref._args_const()
        return dom.struct(
            S=cast(dom.Const, s if s else dom.val(None)),
            U=cast(dom.Const, dom.val(self.underlying._metatype())),
        )

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        introspector = dom.INTROSPECTOR.get(dom.DEFAULT_INTROSPECTOR)
        if introspector is None:
            return None

        fields = self.underlying._dir(Missing)
        if fields is None:
            return None

        return fields.map(lambda field_type: introspector.lift(self, field_type))

    def _get(self, data: Data, key: str | int) -> dom.Val:
        _ = (data, key)
        raise NotImplementedError(
            "NominalQualifier._get remains undefined for value projection; use Introspector.project for type-level semantics"
        )

    def _encode(self, data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._encode is not implemented yet")

    def _decode(self, raw_data: Data) -> Data:
        raise NotImplementedError("NominalQualifier._decode is not implemented yet")
