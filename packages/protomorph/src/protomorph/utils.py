from __future__ import annotations

import protomorph as pm


def _collect_schema_vars(value: pm.Val | None) -> tuple[pm.Var, ...]:
    if value is None:
        return ()
    if isinstance(value, pm.Var):
        return (value,)

    attrs = value.attrs
    if attrs is not None:
        found: list[pm.Var] = []
        for attr in attrs.values:
            found.extend(_collect_schema_vars(attr))
        return tuple(dict.fromkeys(found))

    if isinstance(value, pm.Spec):
        args = value.args or pm.Struct.Empty
        found: list[pm.Var] = []
        for arg in args.values:
            found.extend(_collect_schema_vars(arg))
        return tuple(dict.fromkeys(found))

    return ()
