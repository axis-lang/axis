from __future__ import annotations

from axis import dom, syn, sem
from protobase import slot_cached_property, cached_property



class Item(sem.Entity.Context['Item'], abstract=True):

    @slot_cached_property 
    def anchor(self) -> dom.Anchor:
        raise NotImplementedError("Item subclasses must implement anchor property")

    # @property
    # def anchor(self) -> dom.Anchor | None:
    #     parent = self.parent
    #     #parent = getattr(self, "parent", None)
    #     while isinstance(parent, syn.Item):
    #         ref = getattr(parent, "ref", None)
    #         if isinstance(ref, dom.Ref):
    #             return ref.anchor
    #         if isinstance(ref, dom.Anchor):
    #             return ref
    #         parent = getattr(parent, "parent", None)
    #     return None
