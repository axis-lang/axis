from __future__ import annotations

from typing import ClassVar, cast

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

    def layout(self) -> morph.Layout | None:
        bridge = morph.BRIDGE.get(morph.DEFAULT_BRIDGE)
        return bridge.layout(self)

    def decode(self, raw_data: Data) -> morph.Val:
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, morph.StructLayout):
            raise TypeError(f"{type(self).__name__}.decode is not available for opaque qualified types")
        layout = resolved_layout

        decoded = morph._decode_struct_data(layout.fields, raw_data)
        if layout.builtin_cls is None:
            return self._wrap(decoded)

        attrs = {
            key: value
            for key, value in zip(layout.fields.index.keys, decoded)
            if key is not None
        }
        return self._wrap(layout.builtin_cls(**attrs))

    def construct(self, *args, **kwargs) -> morph.Val:
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, morph.StructLayout):
            raise TypeError(f"{type(self).__name__}.construct is not available for opaque qualified types")
        layout = resolved_layout
        raw = morph._normalize_struct_input(layout.fields, args, kwargs)
        return self.decode(raw)

    def serialize(self, data: Data, format: str | None = None) -> Data:
        _ = format
        resolved_layout = self.layout()
        if not isinstance(resolved_layout, morph.StructLayout):
            raise TypeError(f"{type(self).__name__}.encode is not available for opaque qualified types")
        layout = resolved_layout
        return morph._encode_struct_data(layout.fields, data)

    def _get(self, data: Data, key: str | int) -> morph.Val:
        _ = (data, key)
        raise NotImplementedError(
            "NominalQualifier._get remains undefined for value projection; use SemanticBridge.project for type-level semantics"
        )
