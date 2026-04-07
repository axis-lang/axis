"""Concise, readable repr for core Types and Carriers.

Convention:
- Type tuple-like (whose carriers are tuples) → square brackets [A, B]
- Tuple carriers → parentheses (1, 'hello')
- Spec → trimmed anchor + args: List[int], Integer
- Qual → qualifiers then underlying: List Integer
- Placeholder → $T, $*T
- Union → int | str
"""

from __future__ import annotations

from typing import Any, cast
from .domain import Builtin

_SPEC_PREFIXES = ["std.qualifiers.", "std.", "std.metas.", "std.types."]


# ── Public entry point ─────────────────────────────────────────────


def repr_any(obj: Any) -> str:
    """Single dispatch repr for any core object (Type, Val, Builtin)."""
    from .domain import Placeholder, placeholder_label
    from .domain import UniformType, UnionType, VaryingType, IndexedType
    from .domain import Spread, Spec, Qual
    from .carriers import Carrier, LeafCarrier, Tuple, NativeObjectCarrier, Index, Result, Option

    # ── Hosted (check before Val and Type) ──
    if isinstance(obj, Qual):
        return _repr_qual(obj)
    if isinstance(obj, Spec):
        return _repr_spec(obj)

    # ── Concrete Types (check before generic Type) ──
    if isinstance(obj, Placeholder):
        return f"${placeholder_label(obj)}"
    if isinstance(obj, VaryingType):
        return _repr_varying(obj)
    if isinstance(obj, IndexedType):
        return _repr_indexed(obj)
    if isinstance(obj, UniformType):
        return _repr_uniform(obj)
    if isinstance(obj, UnionType):
        return _repr_union(obj)

    # ── Carriers (check before generic fallback) ──
    if isinstance(obj, Result):
        return _repr_result_carrier(obj)
    if isinstance(obj, Option):
        return _repr_option_carrier(obj)
    if isinstance(obj, LeafCarrier):
        return _repr_leaf(obj)
    if isinstance(obj, NativeObjectCarrier):
        return _repr_native_carrier(obj)
    if isinstance(obj, Index):
        return _repr_index(obj)
    if isinstance(obj, Tuple):
        return _repr_tuple_carrier(obj)
    if isinstance(obj, Carrier):
        return f"{type(obj).__name__}(...)"

    # ── Spread ──
    if isinstance(obj, Spread):
        return f"..({', '.join(_format(v) for v in obj.values)})"

    # ── Builtin (must check before Consed fallback to avoid wrong class name) ──

    if isinstance(obj, Builtin):
        return _repr_builtin(obj)

    # ── Fallback: Consed default ──
    from protobase import Consed

    if isinstance(obj, Consed):
        return Consed.__repr__(obj)
    return repr(obj)


# ── Helpers ────────────────────────────────────────────────────────


def _format(value: Any) -> str:
    """Universal formatter — delegates to repr_any for core objects."""
    from .carriers import Carrier

    if isinstance(value, (Builtin, Carrier)):
        return repr_any(value)
    return repr(value)


def _repr_builtin(value: Any) -> str:
    attrs = []
    for key, attr in value.__class__.__annotations__.items():
        attrs.append(f"{key}={_format(getattr(value, key))}")
    return f"{type(value).__name__}({', '.join(attrs)})"


def _trim_anchor(anchor: str) -> str:
    for prefix in sorted(_SPEC_PREFIXES, key=len, reverse=True):
        if anchor.startswith(prefix):
            return anchor[len(prefix) :]
    return anchor


# ── Type reprs ─────────────────────────────────────────────────────


def _repr_spec(spec) -> str:
    anchor = _trim_anchor(spec.anchor)
    if len(spec.args) == 0:
        return anchor
    parts = ", ".join(repr_any(child) for child in spec.args)
    return f"{anchor}[{parts}]"


def _repr_qual(qual) -> str:
    from .domain import Spec
    
    qualifiers = tuple(cast(Spec, child.fetch()) for child in qual.qualifiers)
    if not qualifiers:
        return repr_any(qual.underlying)
    parts = [repr_any(q) for q in reversed(qualifiers)]
    parts.append(repr_any(qual.underlying))
    return " ".join(parts)


def _repr_varying(vt) -> str:
    return f"[{', '.join(_format(value) for value in vt.values)}]"


def _repr_indexed(it) -> str:
    parts = []
    for offset in range(it.arity):
        item = it.item_at(offset)
        formatted = _format(item.value)
        if item.key is not None:
            parts.append(f"{item.key}: {formatted}")
        else:
            parts.append(formatted)
    return f"[{', '.join(parts)}]"


def _repr_uniform(ut) -> str:
    elem = _format(ut.element_type)
    return f"[...: {elem}]"


def _repr_union(ut) -> str:
    return " | ".join(sorted(_format(v) for v in ut.variants))


def _repr_index(idx) -> str:
    parts = ["_" if k is None else repr(k) for k in idx.keys]
    return f"Index({', '.join(parts)})"


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


def _repr_result_carrier(carrier) -> str:
    if carrier.is_ok:
        return f"Ok({repr_any(carrier.value_carrier())})"
    return f"Err({repr_any(carrier.error_carrier())})"


def _repr_option_carrier(carrier) -> str:
    if carrier.is_some:
        return f"Some({repr_any(carrier.value_carrier())})"
    return "None"
