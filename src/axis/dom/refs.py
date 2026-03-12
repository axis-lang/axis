from __future__ import annotations

from typing import cast

from protobase import _, Consed

from axis import dom
from .types import Type, Data, Missing, MissingType

__all__ = ["RefType", "Ref", "AnchorType", "Anchor", "SpecType", "Spec"]

class RefType(Type, abstract=True): ...
    


class Ref(dom.Val, Consed, abstract=True):
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

    def _decode(self, raw_data: Data) -> Data:
        match raw_data: 
            case tuple() as segments if all(isinstance(segment, str) for segment in segments):
                return segments
            case _:
                raise ValueError(f"Invalid raw data for AnchorType: {raw_data!r}")

    def _dir(
        self, data: Data | MissingType = Missing
    ) -> dom.Struct[str, Type] | None:
        return None

type AnchorSegments = tuple[str, ...]


class Anchor(Ref):
    type: AnchorType = AnchorType()
    data: AnchorSegments = _

    def __str__(self) -> str:
        return ".".join(self.data)

    def __invariants__(self) -> None:
        if not isinstance(self.data, tuple) or not all(
            isinstance(seg, str) for seg in self.data
        ):
            raise TypeError(
                f"Anchor.data must be a tuple of strings, got {self.data!r}"
            )
        if not self.data:
            raise ValueError("Anchor.data must have at least one segment")

    @classmethod
    def from_root(cls, value: str) -> "Anchor":
        return cls(data=(value,))

    @classmethod
    def from_str(cls, path: str) -> "Anchor":
        return dom.anchor(path)

    def child(self, name: str) -> "Anchor":
        return self.__class__(data=(*self.data, name))

    @property
    def root(self) -> str:
        return self.data[0]

    @property
    def name(self) -> str:
        return self.data[-1]

    @property
    def parent(self) -> Anchor | None:
        if len(self.data) > 1:
            return self.__class__(data=self.data[:-1])

    @property
    def segments(self) -> AnchorSegments:
        return self.data

    def specialize(self, spec: dom.Const | None) -> "Spec":
        return dom.spec_ref(self, spec)


class SpecType(RefType):
    "dom.Ref.Spec.Type[..I]"

    ANCHOR = "dom.Ref.Spec.Type"

    meta_args: dom.StructType | None = None

    def _metaspec(self):
        return self.meta_args._metaspec() if self.meta_args is not None else None
    

    def _encode(self, data):
        match data:
            case (anchor_data, None):
                return anchor_data, None
            case (anchor_data, spec_data):
                if self.meta_args is None:
                    raise ValueError("Unexpected args data for SpecType with no meta_args")
                if not isinstance(spec_data, tuple):
                    raise ValueError(f"Expected tuple data for SpecType args, got {type(spec_data)}")
                encoded_spec = tuple(
                    self.meta_args.meta_attrs[n]._encode(v) for n, v in enumerate(spec_data)
                )
                return anchor_data, encoded_spec
            case _:
                raise ValueError(f"Invalid data for SpecType: {data!r}")
       

    def _decode(self, raw_data: Data) -> Data:
        match raw_data:
            case (raw_anchor, None):
                return raw_anchor, None

            case (raw_anchor, raw_spec):
                if not isinstance(raw_spec, tuple):
                    raise ValueError(f"Expected tuple data for SpecType args, got {type(raw_spec)}")
                if self.meta_args is None:
                    raise ValueError("Unexpected args data for SpecType with no meta_args")
                
                spec = tuple(self.meta_args.meta_attrs[n]._decode(v) for n, v in enumerate(raw_spec))
                
                return raw_anchor, spec
            case _:
                raise ValueError(f"Invalid raw data for SpecType: {raw_data!r}")

    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        return self.meta_args.meta_attrs if self.meta_args is not None else None
        

type SpecData = tuple[AnchorSegments, dom.Data]


class Spec(Ref):
    type: SpecType = _
    data: SpecData = _

    @property
    def anchor(self) -> Anchor:
        return Anchor(data=self.data[0])

    @property
    def segments(self) -> AnchorSegments:
        return self.data[0]

    @property
    def args(self) -> dom.Struct[str | None, dom.Val] | None:
        if self.data[1] is None or self.type.meta_args is None:
            return None

        raw_args = cast(tuple[dom.Data, ...], self.data[1])
        values = tuple(
            field_type.wrap(field_data)
            for field_type, field_data in zip(self.type.meta_args.meta_attrs, raw_args)
        )
        return dom.Struct.from_keys(self.type.meta_args.meta_attrs.index.keys, values)

    def _args_const(self) -> dom.Const | None:
        args = self.args
        if args is None:
            return None

        positional: list[dom.Const | dom.Var] = []
        nominal: dict[str, dom.Const | dom.Var] = {}
        for key, value in zip(args.index.keys, args.values):
            typed = cast(dom.Const | dom.Var, value)
            if key is None:
                positional.append(typed)
            else:
                nominal[key] = typed
        return dom.struct(*positional, **nominal)

    def __invariants__(self) -> None:
        pass
