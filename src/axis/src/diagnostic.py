from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import NoReturn, Optional, cast

from protobase import Inmutable, flux, mutate
from rich import print
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from .source import Source, SourceBuffer


class DiagnosticException(Exception):
    def __init__(self, diagnostic: Diagnostic):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.message)


class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()


class LabelStyle(Enum):
    PRIMARY = auto()
    SECONDARY = auto()


_SEVERITY_STYLE = {
    Severity.ERROR: Style(color="red", bold=True),
    Severity.WARNING: Style(color="yellow", bold=True),
    Severity.INFO: Style(color="cyan", bold=True),
}

_LABEL_STYLE = {
    LabelStyle.PRIMARY: Style(color="white", bgcolor="red"),
    LabelStyle.SECONDARY: Style(color="white", bgcolor="blue"),
}


class Label(Inmutable):
    span: Source.Span
    message: Optional[str] = None
    style: LabelStyle = LabelStyle.PRIMARY

    @property
    def source(self):
        return self.span.source


class Diagnostic(Inmutable):
    severity: Severity
    message: str
    code: Optional[str] = None
    labels: tuple[Label, ...] = ()
    notes: tuple[str, ...] = ()
    suggestion: Optional[str] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.emit()

    def with_label(self, *labels: Label) -> Diagnostic:
        return mutate(self, labels=self.labels + labels)

    def with_note(self, message: str) -> Diagnostic:
        return mutate(self, notes=self.notes + (message,))

    def with_suggest(self, message: str) -> Diagnostic:
        return mutate(self, suggestion=message)

    def throw(self) -> NoReturn:
        self.emit()
        raise DiagnosticException(self).with_traceback(None)

    def emit(self) -> None:
        if flux.in_query():
            flux.emit(self)
            return
        print(self)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        from axis.tui.diagnostics import DiagnosticRenderer

        renderer = DiagnosticRenderer()
        text_lines: list[Text] = []
        for renderable in renderer.render(self):
            if isinstance(renderable, Text):
                text_lines.append(cast(Text, renderable))
                continue
            if text_lines:
                yield Text("\n").join(text_lines)
                text_lines = []
            yield renderable
        if text_lines:
            yield Text("\n").join(text_lines)


def error(message: str):
    return Diagnostic(severity=Severity.ERROR, message=message)


def warning(message: str):
    return Diagnostic(severity=Severity.WARNING, message=message)


def info(message: str):
    return Diagnostic(severity=Severity.INFO, message=message)


# ===== Example / Test =====
if __name__ == "__main__":
    content = (
        "pub fn process(data: &[i32]) -> i32 {\n"
        "    // sum the values\n"
        "    let sum = data.iter().sum();\n"
        "    // multiply if sum is positive\n"
        "    if sum > 0 {\n"
        "        let prod = data.iter()\n"
        "            .map(|v| v * sum)\n"
        "            .fold(1, |acc, x| acc * x);\n"
        "        prod\n"
        "    } else {\n"
        "        0\n"
        "    }\n"
        "}\n"
    )
    f2 = SourceBuffer(Path("example2.rs"), content)
    start_fold = content.find(".map(|v| v * sum)\n")
    end_fold = start_fold + 10
    span = Source.Span(source=f2, start=start_fold, end=end_fold)
    lbl_fold = Label(span, "use checked_mul here", LabelStyle.PRIMARY)

    print(
        Diagnostic(
            severity=Severity.ERROR,
            code="W200",
            message="Potential overflow",
            labels=(lbl_fold,),
            notes=("Operations on large data slices may overflow.",),
            suggestion="Switch to checked operations as needed.",
        )
    )
