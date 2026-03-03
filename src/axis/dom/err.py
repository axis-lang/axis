from __future__ import annotations

from typing import TYPE_CHECKING

from axis import dom, src

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult


class Err(dom.Val):
    diagnostic: src.Diagnostic | None = None

    def __repr__(self) -> str:
        from axis.tui import dom_render as render

        return render.format_dom(self)

    def __rich__(self):
        from axis.tui import dom_render as render

        return render.render_dom(self)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        from axis.tui import dom_render as render

        yield from render.rich_console_dom(self, console, options)
