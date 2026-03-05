from .map import *
from .struct import *

from .core import *
from .type_ import *
from .const import *
from .ref import *
from .var import *
from .err import *


# NATIVE_TYPE_MAP = {
#     int: NominalType.from_str("std.Integer"),
#     float: NominalType.from_str("std.Decimal"),
#     Decimal: NominalType.from_str("std.Decimal"),
#     str: NominalType.from_str("std.Text"),
#     bool: NominalType.from_str("std.Boolean"),
#     type(None): NominalType.from_str("std.Null"),
# }


# def type_of_native(tp: type) -> Type:
#     if tp in NATIVE_TYPE_MAP:
#         return NATIVE_TYPE_MAP[tp]
#     else:
#         raise TypeError(f"Unsupported native type: {tp}")


def type_of_literal(value: Literal) -> Type:
    if isinstance(value, bool):
        return STD_BOOLEAN
    elif isinstance(value, int):
        if value > 0:
            return STD_NATURAL
        elif value == 0:
            return STD_WHOLE
        else:
            return STD_INTEGER
    elif isinstance(value, float):
        return STD_DECIMAL
    elif isinstance(value, Decimal):
        if value == value.to_integral_value():
            return STD_INTEGER
        else:
            return STD_DECIMAL
    elif isinstance(value, str):
        return STD_TEXT
    elif value is None:
        return STD_NULL
    else:
        raise TypeError(f"Unsupported literal type: {type(value)}")


NOMINAL_TYPE = NominalType.new("std.NominalType")
META_NOMINAL_TYPE = Const(type=NOMINAL_TYPE, data=NOMINAL_TYPE)

STD_BOOLEAN = NominalType.new("std.Boolean")
STD_NATURAL = NominalType.new("std.Natural")
STD_WHOLE = NominalType.new("std.Whole")
STD_INTEGER = NominalType.new("std.Integer")
STD_DECIMAL = NominalType.new("std.Decimal")
STD_TEXT = NominalType.new("std.Text")
STD_NULL = NominalType.new("std.Optional") # Permite (/) como valor literal Optional X



