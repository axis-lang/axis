from __future__ import annotations

from enum import Enum, auto

from typing import NoReturn, Optional, Self

from protobase import Inmutable, Metadata, Record, flux, mutate
from rich import print
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style

from axis import syn, dom
from axis.src.source import Source


class Report(Inmutable, Metadata[dom.Val]):
    class Exception(Exception):
        def __init__(self, report: "Report"):
            self.report = report
            super().__init__(report.message)

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
        ast: syn.Node
        message: Optional[str] = None
        style: Optional["Report.LabelStyle"] = None

        @property
        def span(self) -> Source.Span | None:
            return getattr(self.ast, "span", None)

        @property
        def source(self) -> Source | None:
            span = self.span
            if span is None:
                return None
            return span.source

    class Builder(Record):
        severity: "Report.Severity"
        message: str
        code_value: Optional[str] = None
        labels: list["Report.Label"] | None = None
        notes: list[str] | None = None
        suggestion: Optional[str] = None

        def code(self, value: str) -> "Report.Builder":
            self.code_value = value
            return self

        def label(
            self,
            ast: syn.Node | None,
            message: Optional[str] = None,
            style: Optional["Report.LabelStyle"] = None,
        ) -> "Report.Builder":
            if ast is None:
                return self
            label_style = style if style is not None else Report.LabelStyle.PRIMARY
            if self.labels is None:
                self.labels = []
            self.labels.append(
                Report.Label(ast=ast, message=message, style=label_style)
            )
            return self

        def note(self, message: str) -> "Report.Builder":
            if self.notes is None:
                self.notes = []
            self.notes.append(message)
            return self

        def suggest(self, message: str) -> "Report.Builder":
            self.suggestion = message
            return self

        def build(self) -> Report:
            labels = tuple(self.labels) if self.labels is not None else ()
            notes = tuple(self.notes) if self.notes is not None else ()
            return Report(
                severity=self.severity,
                message=self.message,
                code=self.code_value,
                labels=labels,
                notes=notes,
                suggestion=self.suggestion,
            )

        def tag[N: syn.Node](self, ast: N, *args, **kwargs) -> N:
            return self.build().tag(ast, *args, **kwargs)

        def show(self, *args, **kwargs):
            return self.build().show(*args, **kwargs)

        def emit(self, *args, **kwargs):
            return self.build().emit(*args, **kwargs)

        def throw(self, *args, **kwargs) -> NoReturn:
            return self.build().throw(*args, **kwargs)

    severity: Severity
    message: str
    code: Optional[str] = None
    labels: tuple[Label, ...] = ()
    notes: tuple[str, ...] = ()
    suggestion: Optional[str] = None

    def show(self) -> Self:
        print(self)
        return self

    def emit(self, or_show=True) -> Self:
        if flux.in_query():
            return flux.emit(self)
        if or_show:
            return self.show()
        raise RuntimeError("Report emitted without being in a query context. ")

    def throw(self, and_show=True) -> NoReturn:
        if and_show:
            self.show()
        raise Report.Exception(self).with_traceback(None)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        from axis.tui.report_render import render_report

        return render_report(self, console, options)


def error(message: str) -> Report.Builder:
    return Report.Builder(severity=Report.Severity.ERROR, message=message)


def warn(message: str) -> Report.Builder:
    return Report.Builder(severity=Report.Severity.WARNING, message=message)


def info(message: str) -> Report.Builder:
    return Report.Builder(severity=Report.Severity.INFO, message=message)
