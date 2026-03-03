from __future__ import annotations

from decimal import Decimal
from typing import Any, TYPE_CHECKING, Union

from protobase import Consed, frozendict

if TYPE_CHECKING:
    from axis import dom
    from rich.console import Console, ConsoleOptions, RenderResult


LITERAL_TYPES = (int, float, Decimal, str, bool, type(None))
type Literal = Union[int, float, Decimal, str, bool, None]


class Builtin(Consed, abstract=True): ...


type Atom = Union[int, float, Decimal, str, bool, None]
type Data = Union[
    Atom, Builtin, tuple["Data", ...], frozenset["Data"], frozendict["Data", "Data"]
]


class Val(Consed, abstract=True):
    pass


class Pure[T: "dom.Type" = Any, D: Data = Any](Val, abstract=True):
    type: T
    data: D

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
