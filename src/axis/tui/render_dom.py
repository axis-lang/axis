"""DOM rendering helpers.

Keep the rendering model intentionally small:
- plain text formatting is the source of truth
- Rich rendering adapts that text, except for reports
"""

from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.text import Text

from axis import dom, log


def _anchor_path(segments: tuple[str, ...]) -> str:
    return ".".join(segments)


def _format_attrs(attrs: std.Struct[str | None, std.Val]) -> str:
    parts: list[str] = []
    for key, value in zip(attrs.index.keys, attrs.values):
        rendered = format_dom(value)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_type_attrs(type_: std.StructType) -> str:
    parts: list[str] = []
    for key, field_type in zip(type_.meta_attrs.index.keys, type_.meta_attrs.values):
        rendered = _format_type(field_type)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_spec(spec: std.Spec) -> str:
    rendered = spec.path
    args = spec.args
    if args is None:
        return rendered
    return f"{rendered}[{_format_attrs(args)}]"


def _format_type(type_: std.Type) -> str:
    if isinstance(type_, std.NominalType):
        return _format_spec(type_.spec_ref)
    if isinstance(type_, std.StructType):
        return f"({_format_type_attrs(type_)})"
    if isinstance(type_, std.UnionType):
        return " | ".join(_format_type(member) for member in type_.types)
    if isinstance(type_, std.NominalQualifier):
        return f"{_format_spec(type_.spec_ref)} {_format_type(type_.underlying)}"
    if isinstance(type_, std.Var):
        return f"${type_.data}"
    if isinstance(type_, std.VarType):
        return "$?"
    if isinstance(type_, std.ErrType):
        return "ErrType"
    return type(type_).__name__


def _format_std_literal(kind: str, data: std.Data) -> str:
    if kind == "Empty":
        return "none"
    if kind == "Boolean":
        return "true" if data else "false"
    if kind == "Text":
        return repr(data)
    return str(data)


def _format_const(value: std.Const) -> str:
    type_ = value.type

    if isinstance(value.data, std.Type):
        return _format_type(value.data)

    if isinstance(type_, std.NominalQualifier):
        return f"<{_format_type(type_)} value>"

    if isinstance(type_, std.UnionType) and isinstance(value.data, tuple):
        discriminator, active_data = value.data
        if not isinstance(discriminator, std.Type):
            return repr(active_data)
        return format_dom(discriminator.wrap(active_data))

    attrs = value.attrs
    if isinstance(type_, std.StructType) and attrs is not None:
        return f"({_format_attrs(attrs)})"

    if isinstance(type_, std.VarType):
        return f"${value.data}"

    if isinstance(type_, std.NominalType):
        anchor = tuple(type_.spec_ref.path.split("."))
        if len(anchor) == 2 and anchor[0] == "std":
            return _format_std_literal(anchor[1], value.data)

        if attrs is None:
            return _format_spec(type_.spec_ref)
        return f"{_format_spec(type_.spec_ref)}({_format_attrs(attrs)})"

    return f"Const(type={_format_type(type_)}, data={value.data!r})"


def format_dom(value: std.Val) -> str:
    if isinstance(value, std.Err):
        report = log.Report.of(value)
        return f"Err({report.message})" if report is not None else "Err"
    if isinstance(value, std.Var):
        return f"${value.data}"
    if isinstance(value, std.Anchor):
        return _anchor_path(value.data)
    if isinstance(value, std.Spec):
        return _format_spec(value)
    if isinstance(value, std.Const):
        return _format_const(value)
    return f"<{type(value).__name__}>"


def render_dom(value: std.Val) -> RenderableType:
    if isinstance(value, std.Err):
        report = log.Report.of(value)
        if report is not None:
            return report
    return Text(format_dom(value))


def rich_console_dom(
    value: std.Val, console: Console, options: ConsoleOptions
) -> RenderResult:
    _ = (console, options)
    yield render_dom(value)
