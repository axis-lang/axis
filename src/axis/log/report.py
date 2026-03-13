from __future__ import annotations

from enum import Enum, auto

from typing import NoReturn, Optional, Self, Iterable, TYPE_CHECKING

from protobase import Inmutable, Metadata, Record, flux, mutate
import protomorph as pm
from rich import print
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style

from axis import syn, src


class Report(Metadata[pm.Val]):
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
        def span(self) -> src.Source.Span | None:
            return getattr(self.ast, "span", None)

        @property
        def source(self) -> src.Source | None:
            span = self.span
            if span is None:
                return None
            return span.source

    class Builder(Record):
        _severity: "Report.Severity"
        _message: str
        _code_value: Optional[str] = None
        _labels: list["Report.Label"] | None = None
        _notes: list[str] | None = None
        _suggestion: Optional[str] = None

        def code(self, value: str) -> "Report.Builder":
            self._code_value = value
            return self

        def labels(
            self,
            nodes: Iterable[syn.Node],
            message: Optional[str] = None,
            style: Optional["Report.LabelStyle"] = None,
        ) -> "Report.Builder":
            for node in nodes:
                self.label(node, message=message, style=style)
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
            if self._labels is None:
                self._labels = []
            self._labels.append(
                Report.Label(ast=ast, message=message, style=label_style)
            )
            return self

        def note(self, message: str) -> "Report.Builder":
            if self._notes is None:
                self._notes = []
            self._notes.append(message)
            return self

        def suggest(self, message: str) -> "Report.Builder":
            self._suggestion = message
            return self

        def build(self) -> Report:
            labels = tuple(self._labels) if self._labels is not None else ()
            notes = tuple(self._notes) if self._notes is not None else ()
            return Report(
                severity=self._severity,
                message=self._message,
                code=self._code_value,
                labels=labels,
                notes=notes,
                suggestion=self._suggestion,
            )

        def tag[V: dom.Val](self, val: V, *args, **kwargs) -> V:
            return self.build().tag(val, *args, **kwargs)

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
        try:
            self.throw(and_show=False)
        except Report.Exception as e:
            raise RuntimeError(
                "Report emitted without being in a query context. "
            ) from e

    def throw(self, cls: type[Exception] = Exception, and_show=True) -> NoReturn:
        if and_show:
            self.show()
        raise cls(self).with_traceback(None)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        from axis.tui.report_render import render_report

        return render_report(self, console, options)


def fatal(message: str) -> Report.Builder:
    return Report.Builder(_severity=Report.Severity.ERROR, _message=message)

def error(message: str) -> Report.Builder:
    return Report.Builder(_severity=Report.Severity.ERROR, _message=message)


def warn(message: str) -> Report.Builder:
    return Report.Builder(_severity=Report.Severity.WARNING, _message=message)


def info(message: str) -> Report.Builder:
    return Report.Builder(_severity=Report.Severity.INFO, _message=message)
