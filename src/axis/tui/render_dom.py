"""DOM rendering helpers.

Keep the rendering model intentionally small:
- plain text formatting is the source of truth
- Rich rendering adapts that text, except for reports
"""

from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.text import Text

from axis import dom
from axis.log.report import Report


def _anchor_path(segments: tuple[str, ...]) -> str:
    return ".".join(segments)


def _format_attrs(attrs: dom.Struct[str | None, dom.Val]) -> str:
    parts: list[str] = []
    for key, value in zip(attrs.index.keys, attrs.values):
        rendered = format_dom(value)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_type_attrs(type_: dom.StructType) -> str:
    parts: list[str] = []
    for key, field_type in zip(type_.meta_attrs.index.keys, type_.meta_attrs.values):
        rendered = _format_type(field_type)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_spec(spec: dom.Spec) -> str:
    rendered = spec.path
    args = spec.args
    if args is None:
        return rendered
    return f"{rendered}[{_format_attrs(args)}]"


def _format_type(type_: dom.Type) -> str:
    if isinstance(type_, dom.NominalType):
        return _format_spec(type_.spec_ref)
    if isinstance(type_, dom.StructType):
        return f"({_format_type_attrs(type_)})"
    if isinstance(type_, dom.UnionType):
        return " | ".join(_format_type(member) for member in type_.types)
    if isinstance(type_, dom.NominalQualifier):
        return f"{_format_spec(type_.spec_ref)} {_format_type(type_.underlying)}"
    if isinstance(type_, dom.Var):
        return f"${type_.data}"
    if isinstance(type_, dom.VarType):
        return "$?"
    if isinstance(type_, dom.ErrType):
        return "ErrType"
    return type(type_).__name__


def _format_std_literal(kind: str, data: dom.Data) -> str:
    if kind == "Empty":
        return "none"
    if kind == "Boolean":
        return "true" if data else "false"
    if kind == "Text":
        return repr(data)
    return str(data)


def _format_const(value: dom.Const) -> str:
    type_ = value.type

    if isinstance(value.data, dom.Type):
        return _format_type(value.data)

    if isinstance(type_, dom.NominalQualifier):
        return f"<{_format_type(type_)} value>"

    if isinstance(type_, dom.UnionType) and isinstance(value.data, tuple):
        discriminator, active_data = value.data
        if not isinstance(discriminator, dom.Type):
            return repr(active_data)
        return format_dom(discriminator.wrap(active_data))

    attrs = value.attrs
    if isinstance(type_, dom.StructType) and attrs is not None:
        return f"({_format_attrs(attrs)})"

    if isinstance(type_, dom.VarType):
        return f"${value.data}"

    if isinstance(type_, dom.NominalType):
        anchor = tuple(type_.spec_ref.path.split("."))
        if len(anchor) == 2 and anchor[0] == "std":
            return _format_std_literal(anchor[1], value.data)

        if attrs is None:
            return _format_spec(type_.spec_ref)
        return f"{_format_spec(type_.spec_ref)}({_format_attrs(attrs)})"

    return f"Const(type={_format_type(type_)}, data={value.data!r})"


def format_dom(value: dom.Val) -> str:
    if isinstance(value, dom.Err):
        report = Report.of(value)
        return f"Err({report.message})" if report is not None else "Err"
    if isinstance(value, dom.Var):
        return f"${value.data}"
    if isinstance(value, dom.Anchor):
        return _anchor_path(value.data)
    if isinstance(value, dom.Spec):
        return _format_spec(value)
    if isinstance(value, dom.Const):
        return _format_const(value)
    return f"<{type(value).__name__}>"


def render_dom(value: dom.Val) -> RenderableType:
    if isinstance(value, dom.Err):
        report = Report.of(value)
        if report is not None:
            return report
    return Text(format_dom(value))


def rich_console_dom(
    value: dom.Val, console: Console, options: ConsoleOptions
) -> RenderResult:
    _ = (console, options)
    yield render_dom(value)
