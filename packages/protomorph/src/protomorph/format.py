from __future__ import annotations

import protomorph as pm


def _anchor_path(segments: tuple[str, ...]) -> str:
    return ".".join(segments)


def _format_attrs(attrs: pm.Struct[str | None, pm.Val]) -> str:
    parts: list[str] = []
    for key, value in zip(attrs.index.keys, attrs.values):
        rendered = format_morph(value)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_named_attrs(attrs: pm.Struct[str, pm.Val]) -> str:
    parts: list[str] = []
    for key, value in zip(attrs.index.keys, attrs.values):
        rendered = format_morph(value)
        parts.append(rendered if key is None else f"{key}={rendered}")
    return ", ".join(parts)


def _format_type_attrs(type: pm.StructType) -> str:
    parts: list[str] = []
    for key, field_type in zip(type.meta_attrs.index.keys, type.meta_attrs.values):
        rendered = _format_type(field_type)
        parts.append(f"{key}={rendered}" if key is not None else rendered)
    return ", ".join(parts)


def _format_spec(spec: pm.Spec) -> str:
    rendered = spec.path
    args = spec.args
    if args is None or args.index.is_empty:
        return rendered
    return f"{rendered}[{_format_attrs(args)}]"


def _format_type(type: pm.Type) -> str:
    if isinstance(type, pm.NominalType):
        return _format_spec(type.spec_ref)
    if isinstance(type, pm.StructType):
        return f"({_format_type_attrs(type)})"
    if isinstance(type, pm.UnionType):
        return " | ".join(_format_type(member) for member in type.types)
    if isinstance(type, pm.NominalQualifier):
        return f"{_format_spec(type.spec_ref)} {_format_type(type.underlying)}"
    if isinstance(type, pm.Var):
        return f"${type.__data__}"
    if isinstance(type, pm.VarType):
        return "$?"
    if isinstance(type, pm.ErrType):
        return "ErrType"
    return type.__class__.__name__


def _format_std_literal(kind: str, data: pm.Data) -> str:
    if kind == "Empty":
        return "none"
    if kind == "Boolean":
        return "true" if data else "false"
    if kind == "Text":
        return repr(data)
    return str(data)


def _format_const(value: pm.Const) -> str:
    type = value.__type__

    if isinstance(value.__data__, pm.Type):
        return _format_type(value.__data__)

    if isinstance(type, pm.NominalQualifier):
        return f"<{_format_type(type)} value>"

    if isinstance(type, pm.UnionType) and isinstance(value.__data__, tuple):
        discriminator, active_data = value.__data__
        if not isinstance(discriminator, pm.Type):
            return repr(active_data)
        return format_morph(discriminator._wrap(active_data))

    attrs = value.attrs
    if isinstance(type, pm.StructType) and attrs is not None:
        return f"({_format_named_attrs(attrs)})"

    if isinstance(type, pm.VarType):
        return f"${value.__data__}"

    if isinstance(type, pm.NominalType):
        anchor = tuple(type.spec_ref.path.split("."))
        if len(anchor) == 2 and anchor[0] == "std":
            return _format_std_literal(anchor[1], value.__data__)

        if attrs is None:
            return _format_spec(type.spec_ref)
        return f"{_format_spec(type.spec_ref)}({_format_named_attrs(attrs)})"

    return f"Const(type={_format_type(type)}, data={value.__data__!r})"


def format_morph(value: pm.Val) -> str:
    if isinstance(value, pm.Err):
        return "Err" if value.__data__ is None else f"Err({value.__data__!r})"
    if isinstance(value, pm.Var):
        return f"${value.__data__}"
    if isinstance(value, pm.Anchor):
        return _anchor_path(value.segments)
    if isinstance(value, pm.Spec):
        return _format_spec(value)
    if isinstance(value, pm.Const):
        return _format_const(value)
    return f"<{type(value).__name__}>"
