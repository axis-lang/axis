from __future__ import annotations
from typing import Any, Callable, cast

from contextvars import ContextVar

from .abstract import contract

# ── Layer 0: Foundation ──────────────────────────────────────────
from .foundation import (
    Id,
    Anchor,
    _RECONSTRUCT,
    Builtin,
)

# ── Layer 1: Type ────────────────────────────────────────────────
from .abstract.contract import Item

from .type_ import (
    Field,
    Type,
    Placeholder,
    placeholder,
)

# ── Layer 2: Val ─────────────────────────────────────────────
from .carrier import (
    Carrier,
    NativeObjectCarrier,
    LeafCarrier,
    TupleCarrier,
)

# ── Layer 3: Index & Tuple ───────────────────────────────────────
from .index import (
    Index,
    Spread,
    Tuple,
)

# ── Layer 4: Concrete types ──────────────────────────────────────
from .domain import (
    UniformType,
    UnionType,
    VaryingType,
    NativeType,
)

# ── Layer 5: Traversal & Unification ─────────────────────────────
from .traversal import (
    deep_zip,
    ZipWalker,
)

from .unification import (
    unify,
)

# ── Layer 6: Hosted types ────────────────────────────────────────
from .hosted import (
    Host,
    AnchorType,
    Spec,
    Qual,
    ANCHOR_TYPE,
)

# ── Layer 7: Native host ───────────────────────────────────────
from .native import (
    spec_name,
    NativeHost,
    register,
    register_native_spec,
    register_python_transform,
    type_from_annotation,
    native_type,
    wrap,
    _bootstrap_defaults,
)

assert issubclass(Type, contract.Descriptor)
#assert issubclass(Val, contract.Carrier)



NATIVE_HOST = NativeHost()
HOST: ContextVar[Host] = ContextVar("HOST", default=NATIVE_HOST)


def _spec_carrier(tp: Type, dt: Any) -> Carrier:
    spec = cast(Spec, tp)
    if HOST.get().schema_for(spec) is None:
        return LeafCarrier(tp, dt)
    return NativeObjectCarrier(tp, dt)


_CARRIER_FACTORIES: dict[type[Type], Callable[[Type, Any], Carrier]] = {
    AnchorType: LeafCarrier,
    Placeholder: LeafCarrier,
    UnionType: LeafCarrier,
    VaryingType: TupleCarrier,
    UniformType: TupleCarrier,
    NativeType: NativeObjectCarrier,
    Spec: _spec_carrier,
    Qual: lambda tp, dt: tp.underlying.carrier(dt),
}

_bootstrap_defaults()
