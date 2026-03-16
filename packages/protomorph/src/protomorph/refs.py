from __future__ import annotations

from typing import cast

from protobase import _, Consed

import protomorph as morph

from .types import Type, Data

__all__ = [
    "ANCHOR_TYPE_INSTANCE",
    "Fact",
    "RefType",
    "Ref",
    "AnchorType",
    "Anchor",
    "SpecType",
    "Spec",
]


ANCHOR_TYPE_INSTANCE: AnchorType | None = None


def _anchor_type_instance() -> AnchorType:
    if ANCHOR_TYPE_INSTANCE is None:
        raise RuntimeError("protomorph.ANCHOR_TYPE_INSTANCE is not initialized")
    return ANCHOR_TYPE_INSTANCE


class RefType(Type, abstract=True):
    pass


type AnchorSegments = tuple[str, ...]
type SpecData = tuple[AnchorSegments, morph.Data]


class Ref(morph.Val, Consed, abstract=True):
    @property
    def segments(self) -> AnchorSegments:
        raise NotImplementedError(
            f"Ref.segments is not implemented in {self.__class__.__name__}"
        )

    @property
    def path(self) -> str:
        return ".".join(self.segments)


class AnchorType(RefType):
    ANCHOR = "dom.Ref.Anchor"

    def deserialize(self, raw_data: Data) -> Data:
        match raw_data:
            case tuple() as segments if all(isinstance(segment, str) for segment in segments):
                return segments
            case _:
                raise ValueError(f"Invalid raw data for AnchorType: {raw_data!r}")


class Anchor(Ref):
    __type__: AnchorType
    __data__: AnchorSegments = _

    def __str__(self) -> str:
        return ".".join(self.__data__)

    def __invariants__(self) -> None:
        if not isinstance(self.__data__, tuple) or not all(isinstance(seg, str) for seg in self.__data__):
            raise TypeError(f"Anchor.data must be a tuple of strings, got {self.__data__!r}")
        if not self.__data__:
            raise ValueError("Anchor.data must have at least one segment")

    @classmethod
    def from_root(cls, value: str) -> Anchor:
        return cls(_anchor_type_instance(), (value,))

    @classmethod
    def from_str(cls, path: str) -> Anchor:
        return morph.anchor(path)

    def child(self, name: str) -> Anchor:
        return self.__class__(
            _anchor_type_instance(),
            cast(AnchorSegments, (*self.__data__, name)),
        )

    @property
    def root(self) -> str:
        return self.__data__[0]

    @property
    def name(self) -> str:
        return self.__data__[-1]

    @property
    def parent(self) -> Anchor | None:
        if len(self.__data__) > 1:
            return self.__class__(_anchor_type_instance(), self.__data__[:-1])
        return None

    @property
    def segments(self) -> AnchorSegments:
        return self.__data__

    def specialize(self, spec: morph.Const | None) -> Spec:
        return morph.spec_ref(self, spec)


class SpecType(RefType):
    ANCHOR = "dom.Ref.Spec.Type"

    meta_args: morph.StructType | None = None

    def _metaspec(self):
        return self.meta_args._metaspec() if self.meta_args is not None else None

    def serialize(self, data, format: str | None = None):
        _ = format
        match data:
            case (anchor_data, None):
                return anchor_data, None
            case (anchor_data, spec_data):
                if self.meta_args is None:
                    raise ValueError("Unexpected args data for SpecType with no meta_args")
                if not isinstance(spec_data, tuple):
                    raise ValueError(
                        f"Expected tuple data for SpecType args, got {type(spec_data)}"
                    )
                encoded_spec = tuple(
                    self.meta_args.meta_attrs[n].serialize(v) for n, v in enumerate(spec_data)
                )
                return anchor_data, encoded_spec
            case _:
                raise ValueError(f"Invalid data for SpecType: {data!r}")

    def deserialize(self, raw_data: Data) -> Data:
        match raw_data:
            case (raw_anchor, None):
                return raw_anchor, None
            case (raw_anchor, raw_spec):
                if not isinstance(raw_spec, tuple):
                    raise ValueError(
                        f"Expected tuple data for SpecType args, got {type(raw_spec)}"
                    )
                if self.meta_args is None:
                    raise ValueError("Unexpected args data for SpecType with no meta_args")
                spec = tuple(self.meta_args.meta_attrs[n].deserialize(v) for n, v in enumerate(raw_spec))
                return raw_anchor, spec
            case _:
                raise ValueError(f"Invalid raw data for SpecType: {raw_data!r}")

    def layout(self) -> morph.StructLayout | None:
        if self.meta_args is None:
            return None
        return morph.StructLayout(fields=self.meta_args.meta_attrs)


class Spec(Ref):
    __type__: SpecType = _
    __data__: SpecData = _

    @property
    def anchor(self) -> Anchor:
        return Anchor(_anchor_type_instance(), self.__data__[0])

    @property
    def segments(self) -> AnchorSegments:
        return self.__data__[0]

    @property
    def args(self) -> morph.Struct[str | None, morph.Val] | None:
        meta_args = self.__type__.meta_args

        if self.__data__[1] is None or meta_args is None:
            return None

        raw_args = cast(tuple[morph.Data, ...], self.__data__[1])
        values = tuple(
            field_type._wrap(field_data)
            for field_type, field_data in zip(meta_args.meta_attrs, raw_args)
        )
        return morph.Struct.from_keys(meta_args.meta_attrs.index.keys, values)

    @property
    def struct_shape(self) -> morph.Struct.Shape[str | None]:
        args = self.args
        if args is None:
            return morph.Struct.Empty.shape
        return args.shape

    @property
    def struct_index(self) -> morph.Struct.Index[str | None]:
        args = self.args
        if args is None:
            return morph.Struct.Empty.index
        return args.index

    def _args_const(self) -> morph.Const | None:
        args = self.args
        if args is None:
            return None

        positional: list[morph.Const | morph.Var] = []
        nominal: dict[str, morph.Const | morph.Var] = {}
        for key, value in zip(args.index.keys, args.values):
            typed = cast(morph.Const | morph.Var, value)
            if key is None:
                positional.append(typed)
            else:
                nominal[key] = typed
        return morph.struct(*positional, **nominal)

    def __invariants__(self) -> None:
        pass


Fact = Spec
