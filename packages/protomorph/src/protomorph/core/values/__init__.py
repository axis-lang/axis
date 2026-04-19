from typing import Any as _Any, Callable as _Callable

from protobase import frozendict
import protomorph.core as _pm

from .base import *
from .map_ import *
from .set_ import *
from .tuple_ import *
from .result import *
from .option import *


def make_value(tp: _pm.Type, dt: _Any) -> Val:
    """Build the canonical carrier for `dt` under descriptor `tp`.

    Dispatch stays shallow and systematic:

    1. Existing carriers pass through unchanged.
    2. Placeholder payloads remain leaf values.
    3. Other runtime type-values dispatch through `make_type_value()`.
    4. Descriptor dispatch is by family: placeholder/union, qualifier,
       tuple-like, then spec.
    5. This function only performs canonical coercions such as
       `set -> frozenset` and `dict -> frozendict`.
    6. Carrier-specific validity belongs to local `__invariants__` methods.
    """

    if isinstance(dt, Val):
        return dt

    if isinstance(dt, _pm.Placeholder):
        return _make_leaf_value(tp, dt)

    if isinstance(dt, _pm.Type):
        return make_type_value(dt)

    match tp:
        case _pm.types.Placeholder() | _pm.types.Union():
            return _make_leaf_value(tp, dt)
        case _pm.types.Qual() as qual:
            return _make_qualified_value(qual, dt)
        case _pm.types.Uniform() | _pm.types.Varying() | _pm.types.Indexed():
            return _make_tuple_value(tp, dt)
        case _pm.types.Spec() as spec:
            return _make_spec_value(spec, dt)
        case _:
            raise NotImplementedError(
                f"No carrier factory for type {type(tp).__name__}"
            )


def make_type_value(dt: _pm.Type) -> Val:
    """Build the canonical carrier for a runtime type-value payload.

    `make_value()` keeps embedded type-values shallow and lets their metatype
    describe them. Direct `val(spec)` / `val(qual)` still use the richer native
    object wrapping path in `core.native.val()`.
    """

    return _make_leaf_value(dt.metatype(), dt)


def _make_qualified_value(tp: _pm.Qual, dt: _Any) -> Val:
    qualifier = tp.qualifier
    if qualifier is None:
        return make_value(tp.qualified, dt)

    builder = _QUALIFIER_BUILDERS.get(qualifier.anchor)
    if builder is not None:
        return builder(tp, dt)
    return make_value(tp.qualified, dt)


def _make_tuple_value(
    tp: _pm.Uniform | _pm.Varying | _pm.Indexed,
    dt: _Any,
) -> Val:
    match tp:
        case _pm.Uniform() as uniform:
            return Index(uniform, dt) if uniform.unique else Tuple(uniform, dt)
        case _pm.Varying() | _pm.Indexed():
            return Tuple(tp, dt)
    raise TypeError(f"Unsupported tuple-like descriptor: {type(tp).__name__}")


def _make_spec_value(tp: _pm.Spec, dt: _Any) -> Val:
    if tp.schema is None:
        return _make_leaf_value(tp, dt)
    return _make_native_object_value(tp, dt)


def _make_result_value(tp: _pm.Qual, dt: _Any) -> Val:
    return Result(tp, dt)


def _make_option_value(tp: _pm.Qual, dt: _Any) -> Val:
    return Option(tp, dt)


def _make_set_value(tp: _pm.Qual, dt: _Any) -> Val:
    return Set(tp, _coerce_set_content(dt))


def _make_map_value(tp: _pm.Qual, dt: _Any) -> Val:
    return Map(tp, _coerce_map_content(dt))


def _make_leaf_value(tp: _pm.Type, dt: _Any) -> Val:
    return LeafCarrier(tp, dt)


def _make_native_object_value(tp: _pm.Type, dt: _Any) -> Val:
    return NativeObjectCarrier(tp, dt)


def _coerce_set_content(dt: _Any) -> _Any:
    if isinstance(dt, set):
        return frozenset(dt)
    return dt


def _coerce_map_content(dt: _Any) -> _Any:
    if isinstance(dt, dict):
        return frozendict(dt)
    return dt


_QUALIFIER_BUILDERS: dict[_pm.Anchor, _Callable[[_pm.Qual, _Any], Val]] = {
    _pm.anchors.result: _make_result_value,
    _pm.anchors.optional: _make_option_value,
    _pm.anchors.set: _make_set_value,
    _pm.anchors.map: _make_map_value,
}
