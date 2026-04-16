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
from .foundation import Builtin
from .types import Op

_SPEC_PREFIXES = ["std.qualifiers.", "std.", "std.metas.", "std.types."]


# ── Public entry point ─────────────────────────────────────────────


def repr_any(obj: Any) -> str:
    """Single dispatch repr for any core object (Type, Val, Builtin)."""
    from .types import Placeholder
    from .types import UniformType, UnionType, VaryingType, IndexedType, Spec, Qual
    from .foundation import Spread
    from ..canonical import Morph, Fuse, Proj
    from ..logic.match import Match
    from .values import Val, LeafCarrier, Tuple, NativeObjectCarrier, Index, Result, Option

    if isinstance(obj, Fuse):
        return _repr_fuse(obj)
    if isinstance(obj, Proj):
        return _repr_proj(obj)
    if isinstance(obj, Match):
        return _repr_match(obj)

    # ── Hosted (check before Val and Type) ──
    if isinstance(obj, Qual):
        return _repr_qual(obj)
    if isinstance(obj, Spec):
        return _repr_spec(obj)

    # ── Concrete Types (check before generic Type) ──
    if isinstance(obj, Placeholder):
        label = obj.display_label()
        if isinstance(label, str):
            return label
        ident = getattr(obj, "id", None)
        if isinstance(ident, str):
            return ident
        slot = getattr(obj, "slot", None)
        if isinstance(slot, int):
            return str(slot)
        return type(obj).__name__
    if isinstance(obj, VaryingType):
        return _repr_varying(obj)
    if isinstance(obj, IndexedType):
        return _repr_indexed(obj)
    if isinstance(obj, UniformType):
        return _repr_uniform(obj)
    if isinstance(obj, UnionType):
        return _repr_union(obj)

    # ── Carriers (check before generic fallback) ──
    if isinstance(obj, Morph):
        return _repr_morph(obj)
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
    if isinstance(obj, Val):
        return f"{type(obj).__name__}(...)"

    # ── Spread ──
    if isinstance(obj, Spread):
        return f"..({', '.join(_format(v) for v in obj.values)})"

    # ── Builtin (must check before Consed fallback to avoid wrong class name) ──
    if isinstance(obj, Builtin):
        return _repr_builtin(obj)

    return repr(obj)


# ── Helpers ────────────────────────────────────────────────────────


def _format(value: Any) -> str:
    """Universal formatter — delegates to repr_any for core objects."""
    from .values import Val

    if isinstance(value, (Builtin, Val)):
        return repr_any(value)
    return repr(value)


def _repr_builtin(value: Any) -> str:
    attrs = []
    for key, attr in value.__class__.__annotations__.items():
        attrs.append(f"{key}={_format(getattr(value, key))}")
    return f"{type(value).__name__}({', '.join(attrs)})"


def _repr_morph(morph) -> str:
    import protomorph.core as _pm

    reified = _pm.walk_subst(morph.descriptor.pattern, {
        slot: binding
        for slot, binding in morph.binding_items()
        if _is_simple_morph_binding(binding)
    })
    rendered = repr_any(reified)

    expanded = [
        f"{repr_any(slot)}={repr_any(binding)}"
        for slot, binding in morph.binding_items()
        if not _is_simple_morph_binding(binding)
    ]
    if not expanded:
        return rendered

    return f"<{rendered}; {', '.join(expanded)}>"


def _repr_match(match) -> str:
    return (
        f"{repr_any(match.left.pattern)} ==[{repr_any(match.fw_template)} | {repr_any(match.bw_template)}]== "
        f"{repr_any(match.right.pattern)}"
    )


def _repr_fuse(fuse) -> str:
    parts = sorted((repr_any(part) for part in fuse.parts))
    if not parts:
        return f"{{ -> {repr_any(fuse.known)} }}"
    return f"{{ {' | '.join(parts)} -> {repr_any(fuse.known)} }}"


def _repr_proj(proj) -> str:
    return f"{repr_any(proj.value)}[{repr_any(proj.target)}]"


def _is_simple_morph_binding(binding) -> bool:
    return len(binding.children) == 0 and not isinstance(binding.fetch(), Op)


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
    from .types import Spec
    
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
    schema = it.schema
    assert schema is not None
    for offset in range(len(schema)):
        item = schema.payload_item_at(offset)
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
            item = carrier.payload_item_at(i)
            if item.key is not None:
                formatted = f"{item.key}={formatted}"
        except (IndexError, TypeError):
            pass
        parts.append(formatted)
    return f"({', '.join(parts)})"


def _repr_native_carrier(carrier) -> str:
    cls_name = type(carrier.content).__name__
    parts = []
    structure = carrier.descriptor.schema
    if structure is None:
        return f"{cls_name}()"
    for i in range(len(carrier)):
        child = carrier[i]
        item = structure.payload_item_at(i)
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
