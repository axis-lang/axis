from __future__ import annotations
from typing import Any, cast

from protobase import flux as protobase_flux

from .abstract import contract

# ── Layer 0: Foundation ──────────────────────────────────────────
from .foundation import (
    Id,
    Anchor,
    Builtin,
    Datum,
)

from .constraint import Constraint

# ── Layer 1: Type ────────────────────────────────────────────────
from .abstract.contract import Item

from .type_ import (
    Field,
    Type,
    Placeholder,
    PlaceholderMetatype,
    Var,
    Mark,
    WildcardMark,
    EllipsisMark,
    SelfMark,
    SimpleVar,
    WILDCARD,
    ELLIPSIS,
    SELF,
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
    Some,
    None_,
    Result,
    Option,
    ResultUnwrapError,
    OptionUnwrapError,
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

from .matching import (
    MatchNode,
    MatchBinding,
    MatchEnv,
    MatchDefaultPlan,
    MatchSolution,
    MatchResult,
    MatchPathStep,
    MatchPath,
    MatchBucket,
    MatchAmbiguity,
    MatchShapeSummary,
    MatchCaseSummary,
    MatchCase,
    MatchDispatch,
    MatchLeaf,
    MatchMany,
    MatchGuardShape,
    MatchSwitchDescriptors,
    MatchSwitchFieldDescriptors,
    MatchSwitchNominalDescriptors,
    MatchTree,
    MatchWalker,
    match,
    compile,
    diagnose,
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


def _make_carrier(tp: Type, dt: Any) -> Carrier:
    if isinstance(tp, (Placeholder, UnionType)):
        return LeafCarrier(tp, dt)
    if isinstance(tp, Qual):
        qualifier = tp.last_qualifier
        if qualifier is not None and qualifier.anchor == Anchor("std.qualifiers.Result"):
            if not isinstance(dt, (Ok, Err)):
                raise TypeError("Result-qualified types require explicit Ok(...) or Err(...)")
            return Result(tp, dt)
        if qualifier is not None and qualifier.anchor == Anchor("std.qualifiers.Optional"):
            if not isinstance(dt, (Some, None_)):
                raise TypeError("Optional-qualified types require explicit Some(...) or None_()")
            return Option(tp, dt)
        return _make_carrier(tp.underlying, dt)
    if isinstance(tp, UniformType):
        return Index(tp, dt) if tp.unique else Tuple(tp, dt)
    if isinstance(tp, (IndexedType, VaryingType)):
        return Tuple(cast(TupleLikeType, tp), dt)
    if isinstance(tp, Spec):
        if REALM.get().schema_for(tp) is None:
            return LeafCarrier(tp, dt)
        return NativeObjectCarrier(tp, dt)
    raise NotImplementedError(f"No carrier factory for type {type(tp).__name__}")

_bootstrap_defaults()
