from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union

from protobase import frozendict

from . import api
from .interop import _PY_TO_AX_TRANSFORMS, _spec_from_types, _tuple_transform, register_py_to_ax
from .struct import Struct


def _bootstrap() -> None:
    api.STRUCT_TYPE = api.nominal_type("dom.Struct.Type")
    api.NOMINAL_TYPE = api.nominal_type("dom.Nominal.Type")

    api.EMPTY_TYPE = api.nominal_type("std.Empty")
    api.BOOLEAN_TYPE = api.nominal_type("std.Boolean")
    api.NATURAL_TYPE = api.nominal_type("std.Natural")
    api.WHOLE_TYPE = api.nominal_type("std.Whole")
    api.INTEGER_TYPE = api.nominal_type("std.Integer")
    api.DECIMAL_TYPE = api.nominal_type("std.Decimal")
    api.TEXT_TYPE = api.nominal_type("std.Text")

    api.ANY_TYPE = api.nominal_type("std.Any")
    api.MAP_TYPE = api.nominal_type("std.Map")
    api.SET_TYPE = api.nominal_type("std.Set")
    api.LIST_TYPE = api.nominal_type("std.List")

    api.TYPE_BY_NATIVE.clear()
    api.TYPE_BY_NATIVE.update(
        {
            bool: api.BOOLEAN_TYPE,
            int: api.INTEGER_TYPE,
            float: api.DECIMAL_TYPE,
            Decimal: api.DECIMAL_TYPE,
            str: api.TEXT_TYPE,
            NoneType: api.EMPTY_TYPE,
        }
    )

    _PY_TO_AX_TRANSFORMS.clear()

    set_transform = lambda V: api.nominal_qual("std.Set", _spec_from_types(), underlying=V)
    map_transform = lambda K, V: api.nominal_qual("std.Map", _spec_from_types(K=K), underlying=V)
    list_transform = lambda T: api.nominal_qual("std.List", _spec_from_types(), underlying=T)

    register_py_to_ax(Struct, lambda K, V: api.nominal_qual("Struct", _spec_from_types(K=K), underlying=V))
    register_py_to_ax(frozendict, map_transform)
    register_py_to_ax(dict, map_transform)
    register_py_to_ax(list, list_transform)
    register_py_to_ax(set, set_transform)
    register_py_to_ax(frozenset, set_transform)
    register_py_to_ax(tuple, _tuple_transform)
    register_py_to_ax(PEP604Union, lambda *args: api.union_type(*args))
