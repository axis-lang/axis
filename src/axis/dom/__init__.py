from typing import cast

from protobase import attrs_of
from types import NoneType
from decimal import Decimal
from .map import *
from .struct import *

from .core import *
from .type_ import *
from .const import *
from .ref import *
from .var import *
from .err import *
from .inspect import INTROSPECTOR


def _anchor(path: str) -> Anchor:
    return Anchor(data=tuple(path.split(".")))


def _spec_ref(anchor: str | Anchor, spec: Const | None = None) -> Spec:
    if isinstance(anchor, str):
        anchor = _anchor(anchor)

    if spec:
        assert isinstance(spec.type, StructType)
        assert isinstance(spec.data, tuple)

        return Spec(
            type=SpecType(anchor=anchor.type, spec=spec.type),
            data=(anchor.data, spec.data),
        )
    else:
        return Spec(
            type=SpecType(anchor=anchor.type, spec=None),
            data=(anchor.data, None),
        )


def _struct(
    *positional: Pure | Var,
    **nominal: Pure | Var,
) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal)
    return Const(
        type=StructType(
            fields=fields.map(lambda x: x.type),
        ),
        data=fields.map(lambda x: x.data).values,
    )


def _literal_struct(
    *positional: Literal,
    **nominal: Literal,
) -> Const[StructType]:
    fields = Struct.new(*positional, **nominal).map(_literal)

    return Const(
        type=StructType(
            fields=fields.map(lambda x: x.type),
        ),
        data=fields.map(lambda x: x.data).values,
    )


def _union_type(*types: Type) -> UnionType:
    """Create a UnionType, flattening any nested UnionTypes.

    (A | B) | C → UnionType(types={A, B, C})
    """
    flat: set[Type] = set()
    for t in types:
        if isinstance(t, UnionType):
            flat.update(t.types)
        else:
            flat.add(t)
    return UnionType(types=frozenset(flat))


def _union(types: frozenset[Type], active: Pure | Var) -> Const[UnionType]:
    """Create a union value with a specific active variant.

    Args:
        types: The full set of types this union can hold (may contain
               nested UnionTypes — they will be flattened).
        active: The currently inhabited variant (its type must be in
                the flattened type set).

    The data is (discriminator, value_data) where discriminator is the
    active member's type — identifying which variant is inhabited.
    """
    union_type = _union_type(*types)
    if active.type not in union_type.types:
        raise TypeError(
            f"Active variant type {active.type} is not in the union types"
        )
    return Const(
        type=union_type,
        data=(active.type, active.data),
    )


def _nominal_type(anchor: str | Anchor, struct: Const | None = None) -> NominalType:
    if isinstance(anchor, str):
        anchor = _anchor(anchor)

    return NominalType(spec_ref=_spec_ref(anchor, struct))


def _literal(value: Literal | None) -> Const:
    t = TYPE_BY_NATIVE.get(type(value), None)
    if t is None:
        raise TypeError(f"Unsupported literal type: {type(value).__name__}")
    return Const(type=t, data=value)


# --- Metatype constants ---
# dom.* for internal structural types
# std.* for user-facing generic types

STRUCT_TYPE = _nominal_type("dom.Type.Struct")
NOMINAL_TYPE = _nominal_type("dom.Type.Nominal")

EMPTY_TYPE = _nominal_type("std.Empty")
BOOLEAN_TYPE = _nominal_type("std.Boolean")
NATURAL_TYPE = _nominal_type("std.Natural")
WHOLE_TYPE = _nominal_type("std.Whole")
INTEGER_TYPE = _nominal_type("std.Integer")
DECIMAL_TYPE = _nominal_type("std.Decimal")
TEXT_TYPE = _nominal_type("std.Text")

TYPE_BY_NATIVE = {
    bool: BOOLEAN_TYPE,
    int: INTEGER_TYPE,
    float: DECIMAL_TYPE,
    Decimal: DECIMAL_TYPE,
    str: TEXT_TYPE,
    type(None): EMPTY_TYPE,
}


def type_of(val: Val) -> Const:
    if not isinstance(val, Pure):
        raise TypeError(f"Cannot determine type of non-Pure value: {val}")
    return val.type.as_val


# --- Encoding: Builtin-rich → raw (JSON-like) ---

def _encode(v: Data) -> Data:
    """Encode dom data to raw (JSON-like) form by stripping Builtins."""
    if isinstance(v, Struct):
        return _encode(cast(Data, v.values))
    if isinstance(v, Builtin):
        return tuple(_encode(attr) for attr in attrs_of(v).values())
    elif isinstance(v, Pure):
        return _encode(v.data)
    elif isinstance(v, tuple):
        return tuple(_encode(item) for item in v)
    elif isinstance(v, frozenset):
        return frozenset(_encode(item) for item in v)
    return v


# --- Introspection: _dir / _get ---

def _dir(val: Val) -> tuple[str | int, ...]:
    """List accessible member keys of a value (cremallera decomposition)."""
    if not isinstance(val, Pure):
        return ()
    t = val.type
    if isinstance(t, StructType):
        return tuple(
            k if k is not None else i
            for i, k in enumerate(t.fields.index.keys)
        )
    elif isinstance(t, NominalQualifier):
        # Qualifier _dir is disabled — rendering accesses type structure directly
        return ()
    elif isinstance(t, UnionType):
        return ('discriminator', 'value')
    elif isinstance(t, NominalType):
        introspector = INTROSPECTOR.get(None)
        if introspector is not None:
            fields = introspector.fields(t)
            if fields is not None:
                return tuple(
                    k if k is not None else i
                    for i, k in enumerate(fields.index.keys)
                )
    return ()


def _get(val: Val, key: str | int) -> Val:
    """Access a sub-value by key (cremallera decomposition).

    The type side tells us how to split the data side into sub-values.
    """
    if not isinstance(val, Pure):
        raise TypeError(f"Cannot access member on {type(val).__name__}")
    t, d = val.type, val.data
    if isinstance(t, StructType) and isinstance(d, tuple):
        if isinstance(key, str):
            offset = t.fields.index.get(key)
        elif isinstance(key, int):
            offset = key
        else:
            raise TypeError(f"Unsupported key type: {type(key)}")
        return Const(type=t.fields[offset], data=d[offset])
    elif isinstance(t, NominalQualifier):
        # Qualifier _get is disabled — return empty sentinel
        return Const(type=EMPTY_TYPE, data=None)
    elif isinstance(t, UnionType) and isinstance(d, tuple):
        discriminator, value_data = d
        if key == 'discriminator':
            return discriminator.as_val
        elif key == 'value':
            return Const(type=discriminator, data=value_data)
    elif isinstance(t, NominalType) and isinstance(d, tuple):
        introspector = INTROSPECTOR.get(None)
        if introspector is not None:
            fields = introspector.fields(t)
            if fields is not None:
                if isinstance(key, str):
                    offset = fields.index.get(key)
                elif isinstance(key, int):
                    offset = key
                else:
                    raise TypeError(f"Unsupported key type: {type(key)}")
                return Const(type=fields[offset], data=d[offset])
    raise KeyError(f"No member {key!r} on {type(t).__name__}")
