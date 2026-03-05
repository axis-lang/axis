from __future__ import annotations

from typing import Self

from protobase import _

from axis import dom
from .type_ import Type


class RefType(Type, abstract=True): ...

class Ref(dom.Pure, abstract=True):
    @property
    def anchor(self) -> "Anchor":
        raise NotImplementedError(
            f"Ref.anchor is not implemented in {self.__class__.__name__}"
        )

    @property
    def spec(self) -> "Spec":
        raise NotImplementedError(
            f"Ref.spec is not implemented in {self.__class__.__name__}"
        )


class AnchorType(RefType):
    pass


type AnchorSegments = tuple[str, ...]


class Anchor(Ref):
    type: AnchorType = AnchorType()
    data: AnchorSegments = _

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
    def from_str(cls, value: str) -> "Anchor":
        return cls(data=tuple(p for part in value.split(".") if (p := part.strip())))

    def child(self, name: str) -> "Anchor":
        return self.__class__(data=(*self.data, name))

    @property
    def parent(self) -> Anchor | None:
        if len(self.data) > 1:
            return self.__class__(data=self.data[:-1])

    @property
    def anchor(self) -> Anchor:
        return self

    @property
    def segments(self) -> AnchorSegments:
        return self.data

    @property
    def spec(self) -> "Spec":
        return Spec.from_anchor_spec(self, None)

    def specialize(self, spec: dom.Const | None) -> "Spec":
        return Spec.from_anchor_spec(self, spec)


class SpecType(RefType):
    spec: dom.StructType | None = None


type SpecData = tuple[AnchorSegments, tuple[dom.Data, ...] | None]


class Spec(Ref):
    type: SpecType = SpecType()
    data: SpecData = _

    @classmethod
    def new(cls, ref: dom.Ref | str, **spec) -> "Spec":
        if isinstance(ref, str):
            ref = Anchor.from_str(ref)
        return cls.from_anchor_spec(ref.anchor, dom.Const.of_struct(**spec))

    @classmethod
    def from_anchor_spec(cls, anchor: Anchor, spec: dom.Const | None) -> Self:
        if spec is None:
            spec_type = None
            spec_data = None
        else:
            if not isinstance(spec.type, dom.StructType):
                raise TypeError("Spec.from_anchor_spec requires a StructType value")
            if not isinstance(spec.data, tuple):
                raise TypeError("Spec.from_anchor_spec requires tuple data")
            spec_type = spec.type
            spec_data = spec.data

        return cls(
            type=SpecType(spec=spec_type),
            data=(anchor.data, spec_data),
        )

    @property
    def anchor(self) -> Anchor:
        return Anchor(data=self.data[0])

    @property
    def spec(self) -> "Spec":
        return self

    @property
    def specialization(self) -> dom.Const | None:
        if self.data[1] is not None:
            return dom.Const(type=self.type.spec, data=self.data[1])

    def __invariants__(self) -> None:
        pass


def ref_segments(ref: Ref) -> AnchorSegments:
    return ref.anchor.data
