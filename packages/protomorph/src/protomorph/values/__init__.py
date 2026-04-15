from protobase import frozendict

from .base import *
from .map_ import *
from .set_ import *
from .tuple_ import *
from .result import *
from .option import *


def make_value(tp, dt):
    import protomorph as pm

    if isinstance(dt, pm.Placeholder):
        return LeafCarrier(tp, dt)
    if isinstance(tp, (pm.Placeholder, pm.UnionType)):
        return LeafCarrier(tp, dt)
    if isinstance(tp, pm.Qual):
        qualifier = tp.qualifier
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Result"):
            if not isinstance(dt, (Ok, Err)):
                raise TypeError("Result-qualified types require explicit Ok(...) or Err(...)")
            return Result(tp, dt)
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Optional"):
            return Option(tp, dt)
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Set"):
            if isinstance(dt, set):
                dt = frozenset(dt)
            if not isinstance(dt, frozenset):
                raise TypeError("Set-qualified values require set(...) or frozenset(...)")
            return Set(tp, dt)
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Map"):
            if isinstance(dt, dict):
                dt = frozendict(dt)
            if not isinstance(dt, frozendict):
                raise TypeError("Map-qualified values require dict(...) or frozendict(...)")
            return Map(tp, dt)
        return make_value(tp.qualified, dt)
    if isinstance(tp, pm.UniformType):
        return Index(tp, dt) if tp.unique else Tuple(tp, dt)
    if isinstance(tp, (pm.IndexedType, pm.VaryingType)):
        return Tuple(tp, dt)
    if isinstance(tp, pm.Spec):
        if tp.schema is None:
            return LeafCarrier(tp, dt)
        return NativeObjectCarrier(tp, dt)
    raise NotImplementedError(f"No carrier factory for type {type(tp).__name__}")
