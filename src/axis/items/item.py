from __future__ import annotations

from typing import Any

import protomorph

from axis import syn, sem
from protobase import Consed, slot_cached_property, _



class Item(sem.Context['Item'], abstract=True):
    package: Consed = _

    @slot_cached_property 
    def anchor(self) -> protomorph.Anchor:
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
