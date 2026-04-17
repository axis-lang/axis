from protobase import frozendict
import protomorph.core as _pm

from .base import *
from .map_ import *
from .set_ import *
from .tuple_ import *
from .result import *
from .option import *


def make_value(tp, dt) -> Val:
    if isinstance(dt, Val):
        return dt
    if isinstance(dt, _pm.Var | _pm.Mark):
        if not isinstance(tp, _pm.Spec):
            return LeafCarrier(tp, dt)
        if tp.schema is None:
            return LeafCarrier(tp, dt)
    if isinstance(dt, (_pm.UniformType, _pm.VaryingType, _pm.IndexedType)):
        return LeafCarrier(dt.metatype(), dt)
    if isinstance(dt, _pm.Type):
        tp = dt.metatype()
    if isinstance(dt, _pm.Placeholder):
        return LeafCarrier(tp, dt)
    if isinstance(tp, (_pm.Placeholder, _pm.UnionType)):
        return LeafCarrier(tp, dt)
    if isinstance(tp, _pm.Qual):
        qualifier = tp.qualifier
        if qualifier is not None and qualifier.anchor == _pm.Anchor("std.qualifiers.Result"):
            return Result(tp, dt)
        if qualifier is not None and qualifier.anchor == _pm.Anchor("std.qualifiers.Optional"):
            return Option(tp, dt)
        if qualifier is not None and qualifier.anchor == _pm.Anchor("std.qualifiers.Set"):
            if isinstance(dt, set):
                dt = frozenset(dt)
            if not isinstance(dt, frozenset):
                raise TypeError("Set-qualified values require set(...) or frozenset(...)")
            return Set(tp, dt)
        if qualifier is not None and qualifier.anchor == _pm.Anchor("std.qualifiers.Map"):
            if isinstance(dt, dict):
                dt = frozendict(dt)
            if not isinstance(dt, frozendict):
                raise TypeError("Map-qualified values require dict(...) or frozendict(...)")
            return Map(tp, dt)
        return make_value(tp.qualified, dt)
    if isinstance(tp, _pm.UniformType):
        if not isinstance(dt, tuple):
            raise TypeError(f"{type(tp).__name__} values require tuple content")
        return Index(tp, dt) if tp.unique else Tuple(tp, dt)
    if isinstance(tp, (_pm.IndexedType, _pm.VaryingType)):
        if not isinstance(dt, tuple):
            raise TypeError(f"{type(tp).__name__} values require tuple content")
        return Tuple(tp, dt)
    if isinstance(tp, _pm.Spec):
        if tp.schema is None:
            return LeafCarrier(tp, dt)
        return NativeObjectCarrier(tp, dt)
    raise NotImplementedError(f"No carrier factory for type {type(tp).__name__}")
