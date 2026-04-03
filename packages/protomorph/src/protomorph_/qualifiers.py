from __future__ import annotations

from typing import ClassVar, cast

import protomorph_ as pm

from .base import Data
from .types import _decode_struct_data, _encode_struct_data, _normalize_struct_input
from .types import Type

__all__ = ["Qualifier", "NominalQualifier"]


class Qualifier(Type, abstract=True):
    ANCHOR: ClassVar[str] = "std.types.Qualifier"

    underlying: Type


class NominalQualifier(Qualifier):
    ANCHOR: ClassVar[str] = "std.types.NominalQualifier"

    spec_ref: pm.Spec

    def _metaspec(self):
        spec_args = self.spec_ref.__type__._metaspec()
        return pm.struct(
            S=cast(pm.Const, spec_args),
            U=cast(pm.Const, pm.val(self.underlying._metatype())),
        )

    def layout(self) -> pm.Layout | None:
        bridge = pm.BRIDGE.get(pm.DEFAULT_BRIDGE)
        return bridge.layout(self)

    def decode(self, raw_data: Data) -> pm.Val:
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.decode is not available for opaque qualified types")
        layout = resolved_layout

        decoded = _decode_struct_data(layout.fields, raw_data)
        if layout.builtin_cls is None:
            return self._wrap(decoded)

        attrs = {
            key: value
            for key, value in zip(layout.fields.index.keys, decoded)
            if key is not None
        }
        return self._wrap(layout.builtin_cls(**attrs))

    def construct(self, *args, **kwargs) -> pm.Val:
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.construct is not available for opaque qualified types")
        layout = resolved_layout
        raw = _normalize_struct_input(layout.fields, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, pm.StructLayout):
            raise TypeError(f"{type(self).__name__}.encode is not available for opaque qualified types {self}")
        layout = resolved_layout
        return _encode_struct_data(layout.fields, data)

    def _get(self, data: Data, key: str | int) -> pm.Val:
        _ = (data, key)
        raise NotImplementedError(
            "NominalQualifier._get remains undefined for value projection; use SemanticBridge.project for type-level semantics"
        )
