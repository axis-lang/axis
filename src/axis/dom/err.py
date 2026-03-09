from __future__ import annotations
from axis import dom



class Err(dom.Val):
    #diagnostic: "Diagnostic | Report | None" = None

    def __repr__(self) -> str:
        from axis.tui import render_dom
        return render_dom.format_dom(self)

    def __rich__(self):
        from axis.tui import render_dom
        return render_dom.render_dom(self)

    def __rich_console__(self, console, options):
        from axis.tui import render_dom
        yield from render_dom.rich_console_dom(self, console, options)
