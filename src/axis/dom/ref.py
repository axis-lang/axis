from __future__ import annotations

from protobase import _

from axis import dom
from .type_ import Type, Data, Missing, MissingType

__all__ = ["RefType", "Ref", "AnchorType", "Anchor", "SpecType", "Spec", "ref_segments"]

class RefType(Type, abstract=True): ...
    # NOTE: Podemos modelar Ref como un Tuple[...] Ref.Step
    


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
    @property
    def __type__(self) -> Type:
        return dom._nominal_type("dom.Ref.Anchor")

    def _axis_dir(
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

    anchor: AnchorType = AnchorType()
    spec: dom.StructType | None = None

    @property
    def __type__(self) -> Type:
        return dom._nominal_type(
            "dom.Ref.Spec.Type",
            dom._struct(
                anchor=self.anchor.as_val,
                spec=self.spec.as_val if self.spec else dom._literal(None),
            ),
        )

    def _axis_dir(self, data: Data | MissingType = Missing) -> dom.Struct[str, Type] | None:
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
