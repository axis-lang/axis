from __future__ import annotations

from collections.abc import Callable, Iterable

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import RichLog, Static, TabbedContent, TabPane

from axis.src.diagnostic import Diagnostic
from axis.tui.diagnostics import DiagnosticRenderer


class MainView(App[None]):
    CSS = """
    #repl-tabs {
        width: 1fr;
    }

    #diagnostics-tabs {
        width: 1fr;
    }
    """

    def __init__(
        self,
        collect_diagnostics: Callable[[], Iterable[Diagnostic]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._collect_diagnostics = collect_diagnostics

    def compose(self) -> ComposeResult:
        with Horizontal():
            with TabbedContent(id="repl-tabs"):
                with TabPane("REPL"):
                    yield Static("REPL (todo)", id="repl-placeholder")
            with TabbedContent(id="diagnostics-tabs"):
                with TabPane("Diagnostics"):
                    yield RichLog(
                        id="diagnostics-log",
                        highlight=False,
                        markup=False,
                        wrap=True,
                    )

    def on_mount(self) -> None:
        if self._collect_diagnostics is None:
            return
        try:
            diagnostics = self._collect_diagnostics()
        except Exception:
            return
        self.show_diagnostics(diagnostics)

    def show_diagnostics(self, diagnostics: Iterable[object]) -> None:
        log = self.query_one("#diagnostics-log", RichLog)
        log.clear()
        renderer = DiagnosticRenderer()
        for diag in diagnostics:
            if not isinstance(diag, Diagnostic):
                continue
            for renderable in renderer.render(diag):
                log.write(renderable)
            log.write("")
