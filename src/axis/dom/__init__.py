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
        raise TypeError(f"Active variant type {active.type} is not in the union types")
    return Const(
        type=union_type,
        data=(active.type, active.data),
    )


def _nominal_type(anchor: str | Anchor, struct: Const | None = None) -> NominalType:
    if isinstance(anchor, str):
        anchor = _anchor(anchor)

    return NominalType(spec_ref=_spec_ref(anchor, struct))

def _nominal_qual(anchor: str | Anchor, struct: Const | None = None, *, underlying: Type) -> NominalQualifier:
    if isinstance(anchor, str):
        anchor = _anchor(anchor)

    return NominalQualifier(spec_ref=_spec_ref(anchor, struct), underlying=underlying)



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

TYPE_BY_NATIVE: dict[type[Literal] | None, Type] = {
    bool: BOOLEAN_TYPE,
    int: INTEGER_TYPE,
    float: DECIMAL_TYPE,
    Decimal: DECIMAL_TYPE,
    str: TEXT_TYPE,
    type(None): EMPTY_TYPE,
    None: EMPTY_TYPE,
}


def type_of(val: Val) -> Const:
    if not isinstance(val, Pure):
        raise TypeError(f"Cannot determine type of non-Pure value: {val}")
    return val.type.as_val


def native_type(t: type[Literal] | None) -> Type:
    if t is None:
        t = type(None)
    if t not in TYPE_BY_NATIVE:
        raise TypeError(f"No dom type mapping for native type {t.__name__}")
    return TYPE_BY_NATIVE[t]


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


# --- Introspection: dir / get ---


def dir(val: Val) -> Struct[str, Type] | None:
    """Return the field map of a value, or Missing if opaque."""
    if not isinstance(val, Pure):
        return None
    return val.type.dir(val.data)


def get(val: Val, key: str | int) -> Val:
    """Access a sub-value by key (cremallera decomposition)."""
    if not isinstance(val, Pure):
        raise TypeError(f"Cannot access member on {type(val).__name__}")
    return val.type.get(val.data, key)
