from __future__ import annotations

from axis import dom, syn
from axis.sem import Entity


class Item(Entity.Context, abstract=True):
    @property
    def anchor(self) -> dom.Anchor | None:
        parent = getattr(self, "parent", None)
        while isinstance(parent, syn.Item):
            ref = getattr(parent, "ref", None)
            if isinstance(ref, dom.Ref):
                return ref.anchor
            if isinstance(ref, dom.Anchor):
                return ref
            parent = getattr(parent, "parent", None)
        return None
