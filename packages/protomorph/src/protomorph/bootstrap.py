from __future__ import annotations

from . import api, refs
from .native import _bootstrap_defaults
from .types import register_meta_type_paths


def _bootstrap() -> None:
    refs.ANCHOR_TYPE_INSTANCE = refs.AnchorType()

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

    _bootstrap_defaults()

    register_meta_type_paths(
        "dom.Struct.Type",
        "dom.Nominal.Type",
        "dom.Qual.Nominal",
        "dom.Union.Type",
        "dom.Ref.Spec.Type",
        "dom.Ref.Anchor",
        "dom.Err.Type",
        "dom.Var.Type",
    )
