from __future__ import annotations

import protomorph as morph


def _anchor_path(segments: tuple[str, ...]) -> str:
    return ".".join(segments)


def _format_attrs(attrs: morph.Struct[str | None, morph.Val]) -> str:
    parts: list[str] = []
    for key, value in zip(attrs.index.keys, attrs.values):
        rendered = format_morph(value)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_type_attrs(type: morph.StructType) -> str:
    parts: list[str] = []
    for key, field_type in zip(type.meta_attrs.index.keys, type.meta_attrs.values):
        rendered = _format_type(field_type)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_spec(spec: morph.Spec) -> str:
    rendered = spec.path
    args = spec.args
    if args is None:
        return rendered
    return f"{rendered}[{_format_attrs(args)}]"


def _format_type(type: morph.Type) -> str:
    if isinstance(type, morph.NominalType):
        return _format_spec(type.spec_ref)
    if isinstance(type, morph.StructType):
        return f"({_format_type_attrs(type)})"
    if isinstance(type, morph.UnionType):
        return " | ".join(_format_type(member) for member in type.types)
    if isinstance(type, morph.NominalQualifier):
        return f"{_format_spec(type.spec_ref)} {_format_type(type.underlying)}"
    if isinstance(type, morph.Var):
        return f"${type.data}"
    if isinstance(type, morph.VarType):
        return "$?"
    if isinstance(type, morph.ErrType):
        return "ErrType"
    return type.__class__.__name__


def _format_std_literal(kind: str, data: morph.Data) -> str:
    if kind == "Empty":
        return "none"
    if kind == "Boolean":
        return "true" if data else "false"
    if kind == "Text":
        return repr(data)
    return str(data)


def _format_const(value: morph.Const) -> str:
    type = value.type

    if isinstance(value.data, morph.Type):
        return _format_type(value.data)

    if isinstance(type, morph.NominalQualifier):
        return f"<{_format_type(type)} value>"

    if isinstance(type, morph.UnionType) and isinstance(value.data, tuple):
        discriminator, active_data = value.data
        if not isinstance(discriminator, morph.Type):
            return repr(active_data)
        return format_morph(discriminator.wrap(active_data))

    attrs = value.attrs
    if isinstance(type, morph.StructType) and attrs is not None:
        return f"({_format_attrs(attrs)})"

    if isinstance(type, morph.VarType):
        return f"${value.data}"

    if isinstance(type, morph.NominalType):
        anchor = tuple(type.spec_ref.path.split("."))
        if len(anchor) == 2 and anchor[0] == "std":
            return _format_std_literal(anchor[1], value.data)

        if attrs is None:
            return _format_spec(type.spec_ref)
        return f"{_format_spec(type.spec_ref)}({_format_attrs(attrs)})"

    return f"Const(type={_format_type(type)}, data={value.data!r})"


def format_morph(value: morph.Val) -> str:
    if isinstance(value, morph.Err):
        return "Err" if value.data is None else f"Err({value.data!r})"
    if isinstance(value, morph.Var):
        return f"${value.data}"
    if isinstance(value, morph.Anchor):
        return _anchor_path(value.segments)
    if isinstance(value, morph.Spec):
        return _format_spec(value)
    if isinstance(value, morph.Const):
        return _format_const(value)
    return f"<{type(value).__name__}>"
