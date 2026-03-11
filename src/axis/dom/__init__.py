from typing import Any, cast, get_origin

from protobase import attrs_of, frozendict
from types import NoneType
from decimal import Decimal
from .map import *
from .struct import *

from .core import *
from .type_ import *
from .const import *
from .ref import *
from .var import *
from .introspect import *
from .err import *



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
            fields=fields.map(lambda x: x if isinstance(x, Var) else x.type),
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
    For Var active variants, the Var itself is the discriminator
    (since Var IS a Type).
    """
    union_type = _union_type(*types)
    # For a Var, the discriminator is the Var itself (it IS a Type)
    discriminator = active if isinstance(active, Var) else active.type
    if discriminator not in union_type.types:
        raise TypeError(f"Active variant type {discriminator} is not in the union types")
    return Const(
        type=union_type,
        data=(discriminator, active.data),
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


class _ValContext(ContextProto):
    def lookup_bound(self, name: str) -> Type | None:
        return None


_VAL_CTX = _ValContext()


def val(*positional, **nominal) -> Val:
    """Convert Python/dom values into a dom.Val.

    Invocation modes:
    - ``dom.val(x)``: coerce a single value
    - ``dom.val(*args, **kwargs)``: build a Struct Const from positional
      and named values

    Single-value coercion rules:
    - dom.Val -> returned as-is
    - Python type tokens in ``LITERAL_TYPES`` -> dom.val(mapped dom.Type)
    - Python/typing annotations -> project via introspect and re-normalize
    - dom.Builtin -> Const(type=value.__type__, data=value.__data__)
    - Python literals -> Const literal
    - dict[str, _] / protobase.frozendict[str, _] -> Struct Const
    - tuple/list -> positional Struct Const

    Raises ValueError for unsupported inputs or failed conversions.
    """

    def _as_pure(value, where: str) -> Pure | Var:
        coerced = val(value)
        if not isinstance(coerced, Pure):
            raise ValueError(
                f"dom.val expected Pure value for {where}, got {type(coerced).__name__}"
            )
        return coerced

    try:
        if not positional and not nominal:
            raise ValueError("dom.val requires at least one value")

        if len(positional) != 1 or nominal:
            args = [_as_pure(item, f"positional[{i}]") for i, item in enumerate(positional)]
            kwargs = {
                key: _as_pure(item, f"key {key!r}")
                for key, item in nominal.items()
            }
            return _struct(*args, **kwargs)

        value = positional[0]

        if isinstance(value, Val):
            return value

        try:
            literal_type_token = LITERAL_TYPES.get(value, None)
        except TypeError:
            literal_type_token = None
        if literal_type_token is not None:
            return val(literal_type_token)

        literal_type = TYPE_BY_NATIVE.get(type(value), None)
        if literal_type is not None:
            return Const(type=literal_type, data=value)

        origin = get_origin(value)
        if value is Any or isinstance(value, type) or origin is not None:
            from .introspect import _python_to_axis_type

            projected = _python_to_axis_type(value, ctx=_VAL_CTX)
            return val(projected)

        if isinstance(value, dict) or isinstance(value, frozendict):
            kwargs: dict[str, Pure | Var] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError(
                        "dom.val only supports dict/frozendict with string keys"
                    )
                kwargs[key] = _as_pure(item, f"key {key!r}")
            return _struct(**kwargs)

        if isinstance(value, tuple) or isinstance(value, list):
            args = [_as_pure(item, f"sequence[{i}]") for i, item in enumerate(value)]
            return _struct(*args)

        if isinstance(value, Builtin):
            return Const(type=value.__type__, data=value.__data__)

        raise ValueError(f"dom.val does not support value of type {type(value).__name__}")
    except ValueError:
        raise
    except Exception as exc:
        typename = type(positional[0]).__name__ if positional else "<struct>"
        raise ValueError(f"dom.val failed to convert {typename}") from exc


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

# Additional base types for introspection
ANY_TYPE = _nominal_type("std.Any")
MAP_TYPE = _nominal_type("std.Map")
SET_TYPE = _nominal_type("std.Set")
LIST_TYPE = _nominal_type("std.List")

TYPE_BY_NATIVE: dict[type[Literal] | None, Type] = {
    bool: BOOLEAN_TYPE,
    int: INTEGER_TYPE,
    float: DECIMAL_TYPE,
    Decimal: DECIMAL_TYPE,
    str: TEXT_TYPE,
    type(None): EMPTY_TYPE,
    None: EMPTY_TYPE,
}

# Mapping for Python literal *type tokens* used by dom.val(type_token)
LITERAL_TYPES: dict[object, Type] = {
    bool: BOOLEAN_TYPE,
    int: NATURAL_TYPE,
    float: DECIMAL_TYPE,
    Decimal: DECIMAL_TYPE,
    str: TEXT_TYPE,
    NoneType: EMPTY_TYPE,
}


def type_of(value: Val) -> Const:
    if not isinstance(value, Pure):
        raise TypeError(f"Cannot determine type of non-Pure value: {value}")
    return cast(Const, val(value.type))


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
    return val.type._axis_dir(val.data)


def get(val: Val, key: str | int) -> Val:
    """Access a sub-value by key (cremallera decomposition)."""
    if not isinstance(val, Pure):
        raise TypeError(f"Cannot access member on {type(val).__name__}")
    return val.type._axis_get(val.data, key)


# Bootstrap introspection when module loads
from .introspect import _bootstrap_introspection
_bootstrap_introspection()
