from __future__ import annotations

from typing import cast

from protobase import _, Consed

import protomorph_ as pm

from .base import Data
from .types import Type

__all__ = [
    "Fact",
    "RefType",
    "Ref",
    "AnchorType",
    "Anchor",
    "SpecType",
    "Spec",
]


class RefType(Type, abstract=True):
    pass


type AnchorSegments = tuple[str, ...]
type SpecData = tuple[AnchorSegments, pm.Data]


class Ref(pm.Val, Consed, abstract=True):
    @property
    def segments(self) -> AnchorSegments:
        raise NotImplementedError(
            f"Ref.segments is not implemented in {self.__class__.__name__}"
        )

    @property
    def path(self) -> str:
        return ".".join(self.segments)


class AnchorType(RefType):
    ANCHOR = "std.types.Anchor"

    def _wrap(self, data: Data) -> pm.Val:
        decoded = self.deserialize(data)
        assert isinstance(decoded, tuple)
        return Anchor(self, cast(AnchorSegments, decoded))

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
        return cls(pm._ANCHOR_TYPE, (value,))

    @classmethod
    def from_str(cls, path: str) -> Anchor:
        return pm.anchor(path)

    def child(self, name: str) -> Anchor:
        return self.__class__(
            pm._ANCHOR_TYPE,
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
            return self.__class__(pm._ANCHOR_TYPE, self.__data__[:-1])
        return None

    @property
    def segments(self) -> AnchorSegments:
        return self.__data__

    def specialize(self, spec: pm.Const | None) -> Spec:
        return pm.spec_ref(self, spec)


class SpecType(RefType):
    ANCHOR = "std.types.Spec"

    meta_args: pm.StructType = _

    def _wrap(self, data: Data) -> pm.Val:
        decoded = self.deserialize(data)
        assert isinstance(decoded, tuple)
        return Spec(self, cast(SpecData, decoded))

    def _metaspec(self):
        return self.meta_args._metaspec()

    def serialize(self, data, format: str | None = None):
        _ = format
        match data:
            case (anchor_data, spec_data):
                if not isinstance(spec_data, tuple):
                    raise ValueError(
                        f"Expected tuple data for SpecType args, got {type(spec_data)}"
                    )
                if not spec_data and self.meta_args == pm.EMPTY_STRUCT_TYPE:
                    return anchor_data, ()
                if len(spec_data) != len(self.meta_args.meta_attrs):
                    raise ValueError(
                        f"Expected {len(self.meta_args.meta_attrs)} spec args, got {len(spec_data)}"
                    )
                encoded_spec = tuple(
                    self.meta_args.meta_attrs[n].serialize(v) for n, v in enumerate(spec_data)
                )
                return anchor_data, encoded_spec
            case _:
                raise ValueError(f"Invalid data for SpecType: {data!r}")

    def deserialize(self, raw_data: Data) -> Data:
        match raw_data:
            case (raw_anchor, raw_spec):
                if not isinstance(raw_spec, tuple):
                    raise ValueError(
                        f"Expected tuple data for SpecType args, got {type(raw_spec)}"
                    )
                if not raw_spec and self.meta_args == pm.EMPTY_STRUCT_TYPE:
                    return raw_anchor, ()
                if len(raw_spec) != len(self.meta_args.meta_attrs):
                    raise ValueError(
                        f"Expected {len(self.meta_args.meta_attrs)} spec args, got {len(raw_spec)}"
                    )
                spec = tuple(self.meta_args.meta_attrs[n].deserialize(v) for n, v in enumerate(raw_spec))
                return raw_anchor, spec
            case _:
                raise ValueError(f"Invalid raw data for SpecType: {raw_data!r}")

    def layout(self) -> pm.StructLayout | None:
        return pm.StructLayout(fields=self.meta_args.meta_attrs)


class Spec(Ref):
    __type__: SpecType = _
    __data__: SpecData = _

    @property
    def anchor(self) -> Anchor:
        return Anchor(pm._ANCHOR_TYPE, self.__data__[0])

    @property
    def segments(self) -> AnchorSegments:
        return self.__data__[0]

    @property
    def args(self) -> pm.Struct[str | None, pm.Val] | None:
        meta_args = self.__type__.meta_args

        if self.__data__[1] is None:
            return None

        raw_args = cast(tuple[pm.Data, ...], self.__data__[1])
        if not raw_args and meta_args == pm.EMPTY_STRUCT_TYPE:
            return pm.Struct.Empty
        values = tuple(
            field_type._wrap(field_data)
            for field_type, field_data in zip(meta_args.meta_attrs, raw_args)
        )
        return pm.Struct.from_keys(meta_args.meta_attrs.index.keys, values)

    @property
    def struct_shape(self) -> pm.Struct.Shape[str | None]:
        args = self.args
        if args is None:
            return pm.Struct.Empty.shape
        return args.shape

    @property
    def struct_index(self) -> pm.Struct.Index[str | None]:
        args = self.args
        if args is None:
            return pm.Struct.Empty.index
        return args.index

    def _args_const(self) -> pm.Const:
        args = self.args
        if args is None:
            return pm.EmptyStruct

        positional: list[pm.Val] = []
        nominal: dict[str, pm.Val] = {}
        for key, value in zip(args.index.keys, args.values):
            if key is None:
                positional.append(value)
            else:
                nominal[key] = value
        return pm.struct(*positional, **nominal)

    def __invariants__(self) -> None:
        pass


Fact = Spec
