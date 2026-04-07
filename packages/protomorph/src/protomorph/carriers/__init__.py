from .base import *
from .tuple_ import *
from .result import *
from .option import *


def carrier(tp, dt):
    import protomorph as pm

    if isinstance(tp, (pm.Placeholder, pm.UnionType)):
        return LeafCarrier(tp, dt)
    if isinstance(tp, pm.Qual):
        qualifier = tp.last_qualifier
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Result"):
            if not isinstance(dt, (Ok, Err)):
                raise TypeError("Result-qualified types require explicit Ok(...) or Err(...)")
            return Result(tp, dt)
        if qualifier is not None and qualifier.anchor == pm.Anchor("std.qualifiers.Optional"):
            if not isinstance(dt, (Some, None_)):
                raise TypeError("Optional-qualified types require explicit Some(...) or None_()")
            return Option(tp, dt)
        return carrier(tp.underlying, dt)
    if isinstance(tp, pm.UniformType):
        return Index(tp, dt) if tp.unique else Tuple(tp, dt)
    if isinstance(tp, (pm.IndexedType, pm.VaryingType)):
        return Tuple(tp, dt)
    if isinstance(tp, pm.Spec):
        if pm.REALM.get().schema_for(tp) is None:
            return LeafCarrier(tp, dt)
        return NativeObjectCarrier(tp, dt)
    raise NotImplementedError(f"No carrier factory for type {type(tp).__name__}")
