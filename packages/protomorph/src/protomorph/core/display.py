from __future__ import annotations

from typing import Any


SPEC_PATH_PREFIXES: list[str] = [
    "std.",
    "std.qualifiers.",
]


def repr_value(value: Any) -> str:
    from .foundation import Ground, OMEGA, Val
    from .hosted import Hosted, Qual, Spec
    from .index import Index, IndexKeyMeta
    from .placeholder import Placeholder, Var
    from .schema import UniformSchema, VaryingSchema
    from .tuple_ import Tuple
    from .variant import Union, Variant

    if value is OMEGA:
        return "<Omega>"
    if isinstance(value, Spec):
        return repr_spec(value)
    if isinstance(value, Qual):
        return repr_qual(value)
    if isinstance(value, Tuple):
        return repr_tuple(value)
    if isinstance(value, Index):
        return repr_index(value)
    if isinstance(value, IndexKeyMeta):
        return f"IndexKey[{repr_value(value.index_key_meta)}]"
    if isinstance(value, UniformSchema):
        return repr_uniform_schema(value)
    if isinstance(value, VaryingSchema):
        return repr_varying_schema(value)
    if isinstance(value, Union):
        return repr_union(value)
    if isinstance(value, Variant):
        return repr_variant(value)
    if isinstance(value, Placeholder):
        return repr_placeholder(value)
    if isinstance(value, Var):
        return repr_var(value)
    if isinstance(value, Ground):
        return repr_ground(value)
    if isinstance(value, Hosted):
        return repr_hosted(value)
    if isinstance(value, Val):
        return repr_plain_val(value)
    return repr(value)


def repr_tuple(value) -> str:
    parts: list[str] = []
    for key, item in _tuple_entries(value):
        rendered = repr_value(item)
        if key is None:
            parts.append(rendered)
        else:
            parts.append(f"{key}={rendered}")
    return f"({', '.join(parts)})"


def repr_spec(value) -> str:
    args = _repr_spec_args(value.args)
    path = trim_spec_path(value.path)
    return path if not args else f"{path}[{args}]"


def repr_qual(value) -> str:
    raw_items = value.__data__.__data__
    if not raw_items:
        return "Qual()"
    return " ".join(repr_value(item) for item in reversed(raw_items))


def repr_index(value) -> str:
    parts = ["_" if item is None else repr(item) for item in value]
    return f"Index({', '.join(parts)})"


def repr_uniform_schema(value) -> str:
    if value.index is None:
        return f"Schema[{repr_value(value.__data__)}]"
    return f"Schema{repr_index(value.index)}[{repr_value(value.__data__)}]"


def repr_varying_schema(value) -> str:
    parts = ", ".join(repr_value(item) for item in value.__data__)
    if value.index is None:
        return f"Schema[{parts}]"
    return f"Schema{repr_index(value.index)}[{parts}]"


def repr_union(value) -> str:
    return " | ".join(sorted(repr_value(item) for item in value.variants))


def repr_variant(value) -> str:
    return repr_value(value.active)


def repr_placeholder(value) -> str:
    return f"${value.__data__}"


def repr_var(value) -> str:
    return f"?{value.__data__!r}"


def repr_ground(value) -> str:
    carrier = value.__data__
    name = getattr(carrier, "__name__", repr(carrier))
    return f"Ground({name})"


def repr_hosted(value) -> str:
    meta = value.__meta__
    if getattr(meta, "path", None) in {"std.Integer", "std.Float", "std.Bool", "std.Text"}:
        return repr(value.__data__)
    if getattr(meta, "path", None) == "std.Id":
        return repr(value.__data__)
    return f"{repr_value(meta)}({value.__data__!r})"


def repr_plain_val(value) -> str:
    return f"{type(value).__name__}({repr_value(value.__meta__)}, {value.__data__!r})"


def _repr_spec_args(value) -> str:
    parts: list[str] = []
    for key, item in _tuple_entries(value):
        rendered = repr_value(item)
        if key is None:
            parts.append(rendered)
        else:
            parts.append(f"{key}={rendered}")
    return ", ".join(parts)


def trim_spec_path(path: str) -> str:
    for prefix in sorted(SPEC_PATH_PREFIXES, key=len, reverse=True):
        if path.startswith(prefix):
            return path[len(prefix) :]
    return path


def _tuple_entries(value) -> list[tuple[Any, Any]]:
    from .foundation import Val

    entries: list[tuple[Any, Any]] = []
    raw_keys = value.index.__data__ if value.index is not None else (None,) * value.arity
    for i, raw in enumerate(value.__data__):
        item = raw if isinstance(raw, Val) else value.schema.at(i).wrap(raw)
        entries.append((raw_keys[i], item))
    return entries
