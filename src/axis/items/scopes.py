from __future__ import annotations

from axis import syn
from axis.sem import Context, Scope


def parent_scope(item: syn.Item) -> Scope | None:
    parent = getattr(item, "parent", None)
    while isinstance(parent, syn.Item):
        if isinstance(parent, Context):
            try:
                return parent.scope
            except NotImplementedError:
                pass
        parent = getattr(parent, "parent", None)
    return None
