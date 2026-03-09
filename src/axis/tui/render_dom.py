"""Dom value rendering — text and Rich.

Replaces the old dom_render.py with a recursive renderer based on
cremallera decomposition (dir/get) and direct type-structure access
for qualifiers.

Exports:
    format_dom(val)         → str   (used by Val.__repr__)
    render_dom(val)         → Text  (used by Val.__rich__)
    rich_console_dom(...)   → yield (used by Val.__rich_console__)
"""
from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.text import Text

from axis import dom
from axis.log.report import Report


# ── Style constants ──────────────────────────────────────────────────

_ANCHOR_STYLE = "cyan"
_NUMBER_STYLE = "yellow"
_TEXT_STYLE = "green"
_VAR_STYLE = "magenta bold"
_NONE_BOOL_STYLE = "italic yellow"
_PUNCT_STYLE = "dim"
_ERR_STYLE = "red bold"


# ── Helpers ──────────────────────────────────────────────────────────

def _is_std_literal(t: dom.Type) -> bool:
    """Check if type is a std.* literal nominal (Integer, Text, etc.)."""
    if not isinstance(t, dom.NominalType):
        return False
    anchor = t.spec_ref.anchor.data
    return len(anchor) == 2 and anchor[0] == "std"


def _is_dom_nominal(t: dom.Type) -> bool:
    """Check if type is a dom.* nominal type (internal structural)."""
    if not isinstance(t, dom.NominalType):
        return False
    anchor = t.spec_ref.anchor.data
    return len(anchor) >= 2 and anchor[0] == "dom"


def _anchor_path(segments: tuple[str, ...]) -> str:
    return ".".join(segments)


def _spec_text(spec: dom.SpecType) -> str:
    """Render a SpecType as 'a.b.c' or 'a.b.c[x, y=z]'."""
    anchor_str = _anchor_path(spec.anchor.as_val.data)
    if spec.spec is None:
        return anchor_str
    # Has specialization — render the struct fields
    parts: list[str] = []
    for i, key in enumerate(spec.spec.fields.index.keys):
        field_type = spec.spec.fields[i]
        field_str = _format_type(field_type)
        if key is not None:
            parts.append(f"{key}={field_str}")
        else:
            parts.append(field_str)
    return f"{anchor_str}[{', '.join(parts)}]"


def _format_type(t: dom.Type) -> str:
    """Quick text representation of a Type (for spec params, etc.)."""
    if isinstance(t, dom.NominalType):
        return _anchor_path(t.spec_ref.anchor.data)
    elif isinstance(t, dom.StructType):
        parts: list[str] = []
        for i, key in enumerate(t.fields.index.keys):
            field_str = _format_type(t.fields[i])
            if key is not None:
                parts.append(f"{key}={field_str}")
            else:
                parts.append(field_str)
        return f"({', '.join(parts)})"
    elif isinstance(t, dom.UnionType):
        return " | ".join(_format_type(m) for m in t.types)
    elif isinstance(t, dom.NominalQualifier):
        ref_str = _spec_text(t.spec_ref.type)
        under_str = _format_type(t.underlying)
        return f"{ref_str} {under_str}"
    elif isinstance(t, dom.VarSpecType):
        return f"${t.name}"
    elif isinstance(t, dom.VarParamType):
        return f"${t.name}"
    return type(t).__name__


# ── format_dom (plain text) ─────────────────────────────────────────

def format_dom(val: dom.Val) -> str:
    """Render a dom Val as plain text (used by __repr__)."""
    if isinstance(val, dom.Err):
        return _format_err(val)
    if isinstance(val, dom.Var):
        return _format_var(val)
    if isinstance(val, dom.Spec):
        return _format_spec(val)
    if isinstance(val, dom.Anchor):
        return _format_anchor(val)
    if isinstance(val, dom.Const):
        return _format_const(val)
    return f"<{type(val).__name__}>"


def _format_err(val: dom.Err) -> str:
    report = Report.of(val)
    if report is not None:
        return f"Err({report.message})"
    return "Err"


def _format_var(val: dom.Var) -> str:
    return f"${val.data}"


def _format_anchor(val: dom.Anchor) -> str:
    return _anchor_path(val.data)


def _format_spec(val: dom.Spec) -> str:
    anchor_str = _anchor_path(val.anchor.data)
    spec = val.specialization
    if spec is None:
        return anchor_str
    # Render specialization struct fields
    parts: list[str] = []
    assert isinstance(spec.type, dom.StructType)
    assert isinstance(spec.data, tuple)
    for i, key in enumerate(spec.type.fields.index.keys):
        field_val = dom.Const(type=spec.type.fields[i], data=spec.data[i])
        field_str = format_dom(field_val)
        if key is not None:
            parts.append(f"{key}={field_str}")
        else:
            parts.append(field_str)
    return f"{anchor_str}[{', '.join(parts)}]"


def _format_const(val: dom.Const) -> str:
    t = val.type

    # Union: transparent — show the active value
    if isinstance(t, dom.UnionType) and isinstance(val.data, tuple):
        discriminator, value_data = val.data
        active = dom.Const(type=discriminator, data=value_data)
        return format_dom(active)

    # Qualifier: juxtaposition — spec_ref[params] underlying
    if isinstance(t, dom.NominalQualifier) and isinstance(val.data, tuple):
        return _format_qualifier(val)

    # Struct: (field1, key=field2)
    if isinstance(t, dom.StructType) and isinstance(val.data, tuple):
        return _format_struct(val)

    # VarType: render as $name (Const wrapping a type variable)
    if isinstance(t, dom.VarType):
        return f"${val.data}"

    # Nominal: std.* literals or dom.* wrapped
    if isinstance(t, dom.NominalType):
        return _format_nominal(val)

    return f"Const(type={t}, data={val.data!r})"


def _format_qualifier(val: dom.Const) -> str:
    """Format NominalQualifier: spec_ref[params] underlying."""
    t = val.type
    assert isinstance(t, dom.NominalQualifier)
    assert isinstance(val.data, tuple)

    # Build the Spec value from type.spec_ref and data[1]
    spec_ref = dom.Spec(type=t.spec_ref.type, data=val.data[1])
    ref_str = _format_spec(spec_ref)

    # Build the underlying value
    underlying = dom.Const(type=t.underlying, data=val.data[0])
    under_str = format_dom(underlying)

    return f"{ref_str} {under_str}"


def _format_struct(val: dom.Const) -> str:
    """Format StructType: (field1, key=field2)."""
    t = val.type
    assert isinstance(t, dom.StructType)
    assert isinstance(val.data, tuple)
    parts: list[str] = []
    for i, key in enumerate(t.fields.index.keys):
        field_val = dom.Const(type=t.fields[i], data=val.data[i])
        field_str = format_dom(field_val)
        if key is not None:
            parts.append(f"{key}={field_str}")
        else:
            parts.append(field_str)
    return f"({', '.join(parts)})"


def _format_nominal(val: dom.Const) -> str:
    """Format NominalType: std.* literal or dom.* spec_ref(data)."""
    t = val.type
    assert isinstance(t, dom.NominalType)
    anchor = t.spec_ref.anchor.data

    # std.* literals: direct representation
    if _is_std_literal(t):
        return _format_std_literal(anchor[1], val.data)

    # dom.* and others: show spec path + data repr via dir/get
    anchor_str = _anchor_path(anchor)
    fields = dom.dir(val)
    if fields is not None:
        parts: list[str] = []
        for i, key in enumerate(fields.index.keys):
            member = dom.get(val, key if key is not None else i)
            member_str = format_dom(member)
            if key is not None:
                parts.append(f"{key}={member_str}")
            else:
                parts.append(member_str)
        return f"{anchor_str}({', '.join(parts)})"
    return anchor_str


def _format_std_literal(kind: str, data: dom.Data) -> str:
    """Format a std.* literal value directly."""
    if kind == "Empty":
        return "none"
    elif kind == "Boolean":
        return "true" if data else "false"
    elif kind == "Text":
        return repr(data)  # "hello" with quotes
    elif kind in ("Integer", "Natural", "Whole", "Decimal"):
        return str(data)
    return str(data)


# ── render_dom (Rich Text) ──────────────────────────────────────────

def render_dom(val: dom.Val) -> RenderableType:
    """Render a dom Val as a Rich Text object (used by __rich__)."""
    if isinstance(val, dom.Err):
        return _render_err(val)
    if isinstance(val, dom.Var):
        return _render_var(val)
    if isinstance(val, dom.Spec):
        return _render_spec(val)
    if isinstance(val, dom.Anchor):
        return _render_anchor(val)
    if isinstance(val, dom.Const):
        return _render_const(val)
    return Text(f"<{type(val).__name__}>")


def _render_err(val: dom.Err) -> RenderableType:
    report = Report.of(val)
    if report is not None:
        return report
    return Text("Err", style=_ERR_STYLE)


def _render_var(val: dom.Var) -> Text:
    t = Text()
    t.append(f"${val.data}", style=_VAR_STYLE)
    return t


def _render_anchor(val: dom.Anchor) -> Text:
    return Text(_anchor_path(val.data), style=_ANCHOR_STYLE)


def _render_spec(val: dom.Spec) -> Text:
    t = Text()
    t.append(_anchor_path(val.anchor.data), style=_ANCHOR_STYLE)
    spec = val.specialization
    if spec is not None:
        assert isinstance(spec.type, dom.StructType)
        assert isinstance(spec.data, tuple)
        t.append("[", style=_PUNCT_STYLE)
        for i, key in enumerate(spec.type.fields.index.keys):
            if i > 0:
                t.append(", ", style=_PUNCT_STYLE)
            if key is not None:
                t.append(f"{key}", style=_ANCHOR_STYLE)
                t.append("=", style=_PUNCT_STYLE)
            field_val = dom.Const(type=spec.type.fields[i], data=spec.data[i])
            t.append_text(_as_rich_text(render_dom(field_val)))
        t.append("]", style=_PUNCT_STYLE)
    return t


def _render_const(val: dom.Const) -> Text:
    t_type = val.type

    # Union: transparent
    if isinstance(t_type, dom.UnionType) and isinstance(val.data, tuple):
        discriminator, value_data = val.data
        active = dom.Const(type=discriminator, data=value_data)
        return _as_rich_text(render_dom(active))

    # Qualifier: juxtaposition
    if isinstance(t_type, dom.NominalQualifier) and isinstance(val.data, tuple):
        return _render_qualifier(val)

    # Struct: (field1, key=field2)
    if isinstance(t_type, dom.StructType) and isinstance(val.data, tuple):
        return _render_struct(val)

    # VarType: render as $name
    if isinstance(t_type, dom.VarType):
        t = Text()
        t.append(f"${val.data}", style=_VAR_STYLE)
        return t

    # Nominal: std.* or dom.*
    if isinstance(t_type, dom.NominalType):
        return _render_nominal(val)

    return Text(f"Const(type={t_type}, data={val.data!r})")


def _render_qualifier(val: dom.Const) -> Text:
    """Render NominalQualifier: spec_ref[params] underlying."""
    t_type = val.type
    assert isinstance(t_type, dom.NominalQualifier)
    assert isinstance(val.data, tuple)

    t = Text()
    spec_ref = dom.Spec(type=t_type.spec_ref.type, data=val.data[1])
    t.append_text(_render_spec(spec_ref))
    t.append(" ")
    underlying = dom.Const(type=t_type.underlying, data=val.data[0])
    t.append_text(_as_rich_text(render_dom(underlying)))
    return t


def _render_struct(val: dom.Const) -> Text:
    """Render StructType: (field1, key=field2)."""
    t_type = val.type
    assert isinstance(t_type, dom.StructType)
    assert isinstance(val.data, tuple)

    t = Text()
    t.append("(", style=_PUNCT_STYLE)
    for i, key in enumerate(t_type.fields.index.keys):
        if i > 0:
            t.append(", ", style=_PUNCT_STYLE)
        if key is not None:
            t.append(f"{key}", style=_ANCHOR_STYLE)
            t.append("=", style=_PUNCT_STYLE)
        field_val = dom.Const(type=t_type.fields[i], data=val.data[i])
        t.append_text(_as_rich_text(render_dom(field_val)))
    t.append(")", style=_PUNCT_STYLE)
    return t


def _render_nominal(val: dom.Const) -> Text:
    """Render NominalType: std.* literal or dom.* with fields."""
    t_type = val.type
    assert isinstance(t_type, dom.NominalType)
    anchor = t_type.spec_ref.anchor.data

    # std.* literals: styled direct
    if _is_std_literal(t_type):
        return _render_std_literal(anchor[1], val.data)

    # dom.* and others: spec path + data via dir/get
    t = Text()
    anchor_str = _anchor_path(anchor)
    t.append(anchor_str, style=_ANCHOR_STYLE)
    fields = dom.dir(val)
    if fields is not None:
        t.append("(", style=_PUNCT_STYLE)
        for i, key in enumerate(fields.index.keys):
            if i > 0:
                t.append(", ", style=_PUNCT_STYLE)
            member = dom.get(val, key if key is not None else i)
            if key is not None:
                t.append(f"{key}", style=_ANCHOR_STYLE)
                t.append("=", style=_PUNCT_STYLE)
            t.append_text(_as_rich_text(render_dom(member)))
        t.append(")", style=_PUNCT_STYLE)
    return t


def _render_std_literal(kind: str, data: dom.Data) -> Text:
    """Render a std.* literal with appropriate Rich styling."""
    if kind == "Empty":
        return Text("none", style=_NONE_BOOL_STYLE)
    elif kind == "Boolean":
        return Text("true" if data else "false", style=_NONE_BOOL_STYLE)
    elif kind == "Text":
        return Text(repr(data), style=_TEXT_STYLE)
    elif kind in ("Integer", "Natural", "Whole", "Decimal"):
        return Text(str(data), style=_NUMBER_STYLE)
    return Text(str(data))


# ── rich_console_dom ────────────────────────────────────────────────

def rich_console_dom(
    val: dom.Val, console: Console, options: ConsoleOptions
) -> RenderResult:
    """Yield Rich renderables for console output (used by __rich_console__)."""
    yield render_dom(val)


# ── Utilities ───────────────────────────────────────────────────────

def _as_rich_text(renderable: RenderableType) -> Text:
    """Coerce a RenderableType to a Text object for appending."""
    if isinstance(renderable, Text):
        return renderable
    return Text(str(renderable))
