from types import NoneType

from .map import *
from .struct import *

from .core import *
from .type_ import *
from .const import *
from .ref import *
from .var import *
from .err import *


def _new_nominal_type(name: str):
    return NominalType(
        ref=Spec(
            type=SpecType(spec=None),
            data=(tuple(name.split(".")), None),
        ),
    )


NOMINAL_TYPE = _new_nominal_type("std.Nominal")
EMPTY_TYPE = _new_nominal_type("std.Empty")
BOOLEAN_TYPE = _new_nominal_type("std.Boolean")
NATURAL_TYPE = _new_nominal_type("std.Natural")
WHOLE_TYPE = _new_nominal_type("std.Whole")
INTEGER_TYPE = _new_nominal_type("std.Integer")
DECIMAL_TYPE = _new_nominal_type("std.Decimal")
TEXT_TYPE = _new_nominal_type("std.Text")

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


def type_of_native(native: type[Literal] | None) -> Type:
    if (result := TYPE_BY_NATIVE.get(native)) is not None:
        return result
    raise TypeError(f"Unsupported native type: {native}")


def type_of_literal(literal: Literal) -> Type:
    return type_of_native(type(literal))
