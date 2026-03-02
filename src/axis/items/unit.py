from typing import ClassVar, cast

from protobase import flux

from axis import dom
from axis.sem import Entity

from .mod import Mod
from .ref import ref_from_expr

class Unit(Mod):
    outline_keyword: ClassVar[str] = "unit"

    @flux.property
    def ref(self) -> dom.Anchor:
        if self.path is None:
            raise ValueError("Unit requires a path to build its ref")
        ref = ref_from_expr(self.path, None)
        if isinstance(ref, dom.Spec):
            raise ValueError("Unit ref cannot be specialized")
        return cast(dom.Anchor, ref)

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset()
