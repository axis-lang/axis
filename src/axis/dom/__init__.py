from .map import *
from .struct import Struct

from .core import *
from .type_ import *
from .const import *
from .ref import *
from .var import *
from .err import *



NATIVE_TYPE_MAP = {
    int: NominalType.from_str("std.Integer"),
    float: NominalType.from_str("std.Decimal"),
    Decimal: NominalType.from_str("std.Decimal"),
    str: NominalType.from_str("std.Text"),
    bool: NominalType.from_str("std.Boolean"),
    type(None): NominalType.from_str("std.Null"),
}


def type_of_native(tp: type) -> Type:
    if tp in NATIVE_TYPE_MAP:
        return NATIVE_TYPE_MAP[tp]
    else:
        raise TypeError(f"Unsupported native type: {tp}")


def type_of_literal(value: Literal) -> Type:
    if isinstance(value, bool):
        return NominalType.from_str("std.Boolean")
    elif isinstance(value, int):
        return NominalType.from_str("std.Integer")
    elif isinstance(value, float):
        return NominalType.from_str("std.Decimal")
    elif isinstance(value, Decimal):
        if value == value.to_integral_value():
            return NominalType.from_str("std.Integer")
        else:
            return NominalType.from_str("std.Decimal")
    elif isinstance(value, str):
        return NominalType.from_str("std.Text")
    elif value is None:
        return NominalType.from_str("std.Null")
    else:
        raise TypeError(f"Unsupported literal type: {type(value)}")
