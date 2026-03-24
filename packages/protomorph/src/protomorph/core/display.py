"""Concise, readable repr for core Types and Carriers.

Convention:
- Type tuple-like (whose carriers are tuples) → square brackets [A, B]
- Tuple data values → parentheses (1, 'hello')
- Spec → trimmed anchor + args: List[int], Integer
- Qual → qualifiers then underlying: List Integer
- Placeholder → $T, $*T
- Union → int | str
"""

from __future__ import annotations

from typing import Any


_SPEC_PREFIXES = ["std.qualifiers.", "std.", "std.metas.", "std.types."]


# ── Public entry point ─────────────────────────────────────────────


def repr_any(obj: Any) -> str:
    """Single dispatch repr for any core object (Type, Carrier, Builtin)."""
    from .type_ import Placeholder
    from .domain import UniformType, UnionType, VaryingType, NativeType
    from .index import Index, Spread, Tuple
    from .hosted import Spec, Qual
    from .carrier import Carrier, LeafCarrier, TupleCarrier, NativeObjectCarrier

    # ── Hosted (check before Carrier and Type) ──
    if isinstance(obj, Qual):
        return _repr_qual(obj)
    if isinstance(obj, Spec):
        return _repr_spec(obj)

    # ── Concrete Types (check before generic Type) ──
    if isinstance(obj, Placeholder):
        return f"${obj.id}"
    if isinstance(obj, VaryingType):
        return _repr_varying(obj)
    if isinstance(obj, UniformType):
        return _repr_uniform(obj)
    if isinstance(obj, UnionType):
        return _repr_union(obj)
    if isinstance(obj, NativeType):
        return _repr_native_type(obj)

    # ── Carriers (check before generic fallback) ──
    if isinstance(obj, LeafCarrier):
        return _repr_leaf(obj)
    if isinstance(obj, NativeObjectCarrier):
        return _repr_native_carrier(obj)
    if isinstance(obj, TupleCarrier):
        return _repr_tuple_carrier(obj)
    if isinstance(obj, Carrier):
        return f"{type(obj).__name__}(...)"

    # ── Index / Tuple ──
    if isinstance(obj, Index):
        return _repr_index(obj)
    if isinstance(obj, Spread):
        return f"*({', '.join(_format(v) for v in obj.values)})"
    if isinstance(obj, Tuple):
        return _repr_tuple_data(obj)

    # ── Fallback: Consed default ──
    from protobase import Consed

    if isinstance(obj, Consed):
        return Consed.__repr__(obj)
    return repr(obj)


# ── Helpers ────────────────────────────────────────────────────────


def _format(value: Any) -> str:
    """Universal formatter — delegates to repr_any for core objects."""
    from .foundation import Builtin
    from .carrier import Carrier

    if isinstance(value, (Builtin, Carrier)):
        return repr_any(value)
    return repr(value)


def _trim_anchor(anchor: str) -> str:
    for prefix in sorted(_SPEC_PREFIXES, key=len, reverse=True):
        if anchor.startswith(prefix):
            return anchor[len(prefix) :]
    return anchor


# ── Type reprs ─────────────────────────────────────────────────────


def _repr_spec(spec) -> str:
    anchor = _trim_anchor(str(spec.anchor))
    args = spec.content[1:]
    if not args:
        return anchor
    parts = ", ".join(_format(a) for a in args)
    return f"{anchor}[{parts}]"


def _repr_qual(qual) -> str:
    specs = qual.content
    if not specs:
        return "Qual()"
    if len(specs) == 1:
        return repr_any(specs[0])
    # qualifiers (reversed) then underlying
    parts = [repr_any(q) for q in reversed(specs[1:])]
    parts.append(repr_any(specs[0]))
    return " ".join(parts)


def _repr_varying(vt) -> str:
    parts = []
    for item in vt.items():
        formatted = _format(item.value)
        if item.key is not None:
            parts.append(f"{item.key}: {formatted}")
        else:
            parts.append(formatted)
    return f"[{', '.join(parts)}]"


def _repr_uniform(ut) -> str:
    from .index import Index

    elem = _format(ut.element_type)
    if ut.index is Index.Empty:
        return f"[...: {elem}]"
    keys = ", ".join("_" if k is None else str(k) for k in ut.index)
    return f"[..({keys}): {elem}]"


def _repr_union(ut) -> str:
    return " | ".join(sorted(_format(v) for v in ut.variants))


def _repr_native_type(nt) -> str:
    name = nt.builtin_cls.__name__
    if nt.schema.arity == 0:
        return name
    parts = []
    for item in nt.schema.items():
        formatted = _format(item.value)
        if item.key is not None:
            parts.append(f"{item.key}: {formatted}")
        else:
            parts.append(formatted)
    return f"{name}[{', '.join(parts)}]"


def _repr_index(idx) -> str:
    from .index import Index

    if idx is Index.Empty:
        return "Index()"
    parts = ["_" if k is None else repr(k) for k in idx.keys]
    return f"Index({', '.join(parts)})"


# ── Carrier reprs ──────────────────────────────────────────────────


def _repr_leaf(carrier) -> str:
    return _format(carrier.content)


def _repr_tuple_carrier(carrier) -> str:
    parts = []
    for i in range(len(carrier)):
        child = carrier[i]
        formatted = repr_any(child)
        try:
            item = carrier.descriptor.item_at(i)
            if item.key is not None:
                formatted = f"{item.key}={formatted}"
        except (IndexError, TypeError):
            pass
        parts.append(formatted)
    return f"({', '.join(parts)})"


def _repr_native_carrier(carrier) -> str:
    cls_name = type(carrier.content).__name__
    parts = []
    for i in range(len(carrier)):
        child = carrier[i]
        item = carrier.descriptor.item_at(i)
        parts.append(f"{item.key}={repr_any(child)}")
    return f"{cls_name}({', '.join(parts)})"


# ── Tuple data repr (parentheses) ──────────────────────────────────


def _repr_tuple_data(t) -> str:
    parts = []
    for item in t.items():
        formatted = _format(item.value)
        if item.key is not None:
            parts.append(f"{item.key}={formatted}")
        else:
            parts.append(formatted)
    return f"({', '.join(parts)})"
