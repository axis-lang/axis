from __future__ import annotations
from typing import Any, Callable, cast

from protobase import flux as protobase_flux

from .abstract import contract

# ── Layer 0: Foundation ──────────────────────────────────────────
from .foundation import (
    Id,
    Anchor,
    Builtin,
)

# ── Layer 1: Type ────────────────────────────────────────────────
from .abstract.contract import Item

from .type_ import (
    Field,
    Type,
    Placeholder,
    Var,
    SimpleVar,
    placeholder,
    placeholder_name,
    placeholder_context,
    placeholder_slot,
    placeholder_label,
)

from .realm import (
    Realm,
    OverlayRealm,
    current_realm,
)

# ── Layer 4: Concrete types ──────────────────────────────────────
from .domain import (
    TupleLikeType,
    UniformType,
    UnionType,
    VaryingType,
    IndexedType,
    Spread,
    Spec,
    Qual,
)

# ── Layer 2: Val ─────────────────────────────────────────────
from .carrier import (
    Carrier,
    NativeObjectCarrier,
    LeafCarrier,
    Tuple,
    Index,
    Ok,
    Err,
    Result,
)

# ── Layer 3: Spreads ──────────────────────────────────────────────


# ── Layer 5: Traversal & Unification ─────────────────────────────
from .traversal import (
    deep_zip,
    ZipWalker,
)

from .unification import (
    UnionFind,
    unify,
)

# ── Layer 7: Native host ───────────────────────────────────────
from .native import (
    spec_name,
    NativeVar,
    NativeRealm,
    register_native_spec,
    register_python_transform,
    _project_type,
    wrap,
    _bootstrap_defaults,
)


assert issubclass(Type, contract.Descriptor)





NATIVE_REALM = NativeRealm()
REALM = cast(Any, protobase_flux.contextvar("pm.REALM", default=NATIVE_REALM))

Host = Realm
current_host = current_realm
NATIVE_HOST = NATIVE_REALM
HOST = REALM
NativeHost = NativeRealm


def carrier_factory_for(tp: Type) -> Callable[[Type, Any], Carrier] | None:
    for cls in type(tp).__mro__:
        provider = _CARRIER_FACTORIES.get(cast(type[Type], cls), None)
        if provider is not None:
            return provider
    return None


def _spec_carrier(tp: Type, dt: Any) -> Carrier:
    spec = cast(Spec, tp)
    if REALM.get().schema_for(spec) is None:
        return LeafCarrier(tp, dt)
    return NativeObjectCarrier(tp, dt)


def _tuple_carrier(tp: Type, dt: Any) -> Carrier:
    return Tuple(cast(TupleLikeType, tp), dt)


def _index_carrier(tp: Type, dt: Any) -> Carrier:
    return Index(cast(UniformType, tp), dt)


def _qual_carrier(tp: Type, dt: Any) -> Carrier:
    qual = cast(Qual, tp)
    qualifiers = tuple(cast(Spec, child.fetch()) for child in qual.qualifiers)
    if qualifiers and qualifiers[-1].anchor == Anchor("std.qualifiers.Result"):
        if not isinstance(dt, (Ok, Err)):
            raise TypeError("Result-qualified types require explicit Ok(...) or Err(...)")
        return Result(qual, dt)
    return qual.underlying.make(dt)


_CARRIER_FACTORIES: dict[type[Type], Callable[[Type, Any], Carrier]] = {
    Placeholder: LeafCarrier,
    UnionType: LeafCarrier,
    VaryingType: _tuple_carrier,
    UniformType: lambda tp, dt: _index_carrier(tp, dt) if cast(UniformType, tp).unique else _tuple_carrier(tp, dt),
    IndexedType: _tuple_carrier,
    Spec: _spec_carrier,
    Qual: _qual_carrier,
}

_bootstrap_defaults()
