from __future__ import annotations

import protomorph as pm

from axis import syn, sem
from protobase import slot_cached_property, cached_property



class Item(sem.Context['Item'], abstract=True):

    @slot_cached_property 
    def anchor(self) -> pm.Anchor:
        raise NotImplementedError("Item subclasses must implement anchor property")

    # @property
    # def anchor(self) -> std.Anchor | None:
    #     parent = self.parent
    #     #parent = getattr(self, "parent", None)
    #     while isinstance(parent, syn.Item):
    #         ref = getattr(parent, "ref", None)
    #         if isinstance(ref, std.Ref):
    #             return ref.anchor
    #         if isinstance(ref, std.Anchor):
    #             return ref
    #         parent = getattr(parent, "parent", None)
    #     return None
