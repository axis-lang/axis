from __future__ import annotations

from typing import cast

from protobase import _

from axis import dom
from .type_ import Type, Data, Missing, MissingType

__all__ = ["RefType", "Ref", "AnchorType", "Anchor", "SpecType", "Spec", "ref_segments"]

class RefType(Type, abstract=True): ...
    # NOTE: Podemos modelar Ref como un Tuple[...] Ref.Step
    


class Ref(dom.Pure, abstract=True):
    def _metaspec(self) -> dom.Const | None:
        return self.type._metaspec()

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
    ANCHOR = "dom.Ref.Anchor"

    def _decode(self, raw_data: Data) -> Data:
        if not isinstance(raw_data, tuple) or not all(
            isinstance(segment, str) for segment in raw_data
        ):
            return raw_data
        return cast(Data, Anchor(data=cast(AnchorSegments, raw_data)))

    def _dir(
        self, data: Data | MissingType = Missing
    ) -> dom.Struct[str, Type] | None:
        return None


type AnchorSegments = tuple[str, ...]


class Anchor(Ref):
    type: AnchorType = AnchorType()
    data: AnchorSegments = _

    def __repr__(self) -> str:
        from axis.tui import render_dom

        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom

        return render_dom.render_dom(self)

    def __rich_console__(self, console, options):
        from axis.tui import render_dom

        yield from render_dom.rich_console_dom(self, console, options)

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
        return dom._anchor(path)

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
    def anchor(self) -> Anchor:
        return self

    @property
    def segments(self) -> AnchorSegments:
        return self.data

    @property
    def spec(self) -> "Spec":
        return dom._spec_ref(self, None)

    def specialize(self, spec: dom.Const | None) -> "Spec":
        return dom._spec_ref(self, spec)


class SpecType(RefType):
    "dom.Ref.Spec.Type[..I]"

    ANCHOR = "dom.Ref.Spec.Type"

    anchor: AnchorType = AnchorType()
    spec: dom.StructType | None = None # TODO: renombrar como hparams

    def _metaspec(self) -> dom.Const | None:
        return self.spec._metaspec() if self.spec is not None else None



    def _decode(self, raw_data: Data) -> Data:
        if not isinstance(raw_data, tuple) or len(raw_data) != 2:
            return raw_data

        raw_anchor, raw_spec = raw_data
        anchor = self.anchor._decode(raw_anchor)
        if not isinstance(anchor, Anchor):
            return raw_data

        if self.spec is None or raw_spec is None:
            return cast(Data, dom._spec_ref(anchor, None))

        spec_data = self.spec._decode(raw_spec)
        return cast(
            Data,
            dom._spec_ref(anchor, dom.Const(type=self.spec, data=cast(tuple[Data, ...], spec_data))),
        )



    def _dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
        return dom.Struct.new(
            anchor=self.anchor,
            spec=self.spec or dom.native_type(None),
        )


type SpecData = tuple[AnchorSegments, dom.Data]


class Spec(Ref):
    type: SpecType = _
    data: SpecData = _

    def __repr__(self) -> str:
        from axis.tui import render_dom

        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom

        return render_dom.render_dom(self)

    def __rich_console__(self, console, options):
        from axis.tui import render_dom

        yield from render_dom.rich_console_dom(self, console, options)

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
