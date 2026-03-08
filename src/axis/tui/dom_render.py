from __future__ import annotations

from functools import singledispatch

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.text import Text

from axis import dom
from axis.log.report import Report


def format_ref(ref: dom.Ref) -> str:
    anchor = ref.anchor
    parts = list(anchor.data)
    if isinstance(ref, dom.Spec):
        suffix = "[]" if ref.specialization is None else "[...]"
        if parts:
            parts[-1] = f"{parts[-1]}{suffix}"
    return ".".join(parts)


def render_ref(ref: dom.Ref) -> Text:
    return Text(format_ref(ref))


def format_const(value: dom.Const) -> str:
    return f"Const(type={value.type}, data={value.data!r})"


def render_const(value: dom.Const) -> Text:
    return Text(format_const(value))


def format_err(value: dom.Err) -> str:
    report = Report.of(value)
    if report is not None:
        return f"Err({report.message})"
    return "Err"


def render_err(value: dom.Err) -> RenderableType:
    report = Report.of(value)
    if report is not None:
        return report
    return Text(format_err(value))


@singledispatch
def format_dom(value: object) -> str:
    return f"<{type(value).__name__}>"


@format_dom.register
def _(value: dom.Pure) -> str:
    return f"<{type(value).__name__}>"


@format_dom.register
def _(value: dom.Ref) -> str:
    return format_ref(value)


@format_dom.register
def _(value: dom.Const) -> str:
    return format_const(value)


@format_dom.register
def _(value: dom.Err) -> str:
    return format_err(value)


@singledispatch
def render_dom(value: object) -> RenderableType:
    return Text(format_dom(value))


@render_dom.register
def _(value: dom.Ref) -> RenderableType:
    return render_ref(value)


@render_dom.register
def _(value: dom.Const) -> RenderableType:
    return render_const(value)


@render_dom.register
def _(value: dom.Err) -> RenderableType:
    return render_err(value)


@singledispatch
def rich_console_dom(
    value: object, console: Console, options: ConsoleOptions
) -> RenderResult:
    yield render_dom(value)
