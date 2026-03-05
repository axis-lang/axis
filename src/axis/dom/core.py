from __future__ import annotations

from decimal import Decimal
from typing import Any, Union

from protobase import Inmutable, Consed, frozendict

from axis import dom
from rich.console import Console, ConsoleOptions, RenderResult


__all__ = [
    "Literal",
    "Builtin",
    "Data",
    "Val",
    "Pure",
]


class Builtin(Consed, abstract=True):
    pass


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
        from axis.tui import dom_render

        return dom_render.format_dom(self)

    def __rich__(self):
        from axis.tui import dom_render

        return dom_render.render_dom(self)

    def __rich_console__(
        self,
        console: "Console",
        options: "ConsoleOptions",
    ) -> "RenderResult":
        from axis.tui import dom_render

        yield from dom_render.rich_console_dom(self, console, options)


class Pure[T: "dom.Type" = Any, D: Data = Any](Consed, abstract=True):
    type: T
    data: D
