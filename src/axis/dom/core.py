from __future__ import annotations

from decimal import Decimal
from typing import Any, Union, Self, cast, ClassVar, Iterable

from protobase import Inmutable, Consed, frozendict, attrs_of, is_abstract
from axis import dom
from rich.console import Console, ConsoleOptions, RenderResult


__all__ = [
    "Literal",
    "Builtin",
    "Data",
    "Val",
    "Pure",
]

_PENDING_CLASSES: list[type[dom.Builtin]] = []

class Builtin(Consed, abstract=True):
    ANCHOR: ClassVar[str]

    @classmethod
    def _anchor_path(cls) -> str:
        """Resolve the canonical anchor path for this Builtin class.

        Priority:
        1) Class-local ``ANCHOR`` when explicitly defined on the class
        2) ``<module>.<qualname>`` fallback when ANCHOR is not defined
        """
        anchor = cls.__dict__.get("ANCHOR", None)
        if isinstance(anchor, str):
            return anchor
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def __class_post_build__(cls):
        """Register concrete Builtin subclasses for lazy introspection."""
        if is_abstract(cls):
            return
        _PENDING_CLASSES.append(cls)

    @property
    def __type__(self) -> dom.Type:
        return dom._nominal_type(self.__class__._anchor_path())

    @property
    def __data__(self) -> Data:
        return cast(Data, self)


type Literal = Union[
    int,
    float,
    Decimal,
    str,
    bool,
    None,
]

type Data = Union[
    Literal,
    Builtin,
    tuple["Data", ...],
    frozenset["Data"],
    frozendict["Data", "Data"],
]


class Val(Inmutable, abstract=True):

    def __repr__(self) -> str:
        from axis.tui import render_dom

        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom

        return render_dom.render_dom(self)

    def __rich_console__(
        self,
        console: "Console",
        options: "ConsoleOptions",
    ) -> "RenderResult":
        from axis.tui import render_dom

        yield from render_dom.rich_console_dom(self, console, options)

    def get(self, key: int | str) -> Val:
        return dom.get(self, key)

    def dir(self) -> Iterable[str]:
        return (dom.dir(self) or dom.Struct.Empty).index._keyed_indices.keys


class Pure[T: "dom.Type" = Any, D: "dom.Data" = Any](Val, Consed, abstract=True):
    type: T
    data: D

    @property
    def encoded(self) -> Self:
        """Encode data side to raw (JSON-like) form; type side stays intact."""
        return self.__class__(type=self.type, data=cast(D, dom._encode(self.data)))
