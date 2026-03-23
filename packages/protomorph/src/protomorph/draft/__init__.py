from __future__ import annotations

# ── Layer 0: Foundation ──────────────────────────────────────────
from .foundation import (
    Id,
    Anchor,
    _RECONSTRUCT,
    Builtin,
)

# ── Layer 1: Type ────────────────────────────────────────────────
from .type_ import (
    Field,
    Type,
    Omega,
    OMEGA,
    Placeholder,
    placeholder,
)

# ── Layer 2: Carrier ─────────────────────────────────────────────
from .carrier import (
    Carrier,
    NativeObjectCarrier,
    LeafCarrier,
    TupleCarrier,
)

# ── Layer 3: Index & Tuple ───────────────────────────────────────
from .index import (
    Index,
    EMPTY_INDEX,
    Spread,
    Tuple,
)

# ── Layer 4: Concrete types ──────────────────────────────────────
from .concrete import (
    ScalarType,
    INT_TYPE,
    STR_TYPE,
    FLOAT_TYPE,
    BOOL_TYPE,
    NONE_TYPE,
    _SCALAR_TYPES,
    UniformType,
    UnionType,
    VaryingType,
    NativeType,
)

# ── Layer 5: Native bridge ───────────────────────────────────────
from .bridge import (
    type_from_annotation,
    native_type,
    wrap,
)
