from typing import ClassVar, cast

from protobase import flux

from axis import dom, expr
from axis.sem import Entity

from .mod import Mod

class Unit(Mod):
    outline_keyword: ClassVar[str] = "unit"

    @flux.property
    def ref(self) -> dom.Anchor:
        if self.path is None:
            raise ValueError("Unit requires a path to build its ref")
        ref = expr.to_spec_ref(self.path, None)
        if ref is None:
            raise ValueError("Unit requires a path to build its ref")
        if isinstance(ref, dom.Spec):
            raise ValueError("Unit ref cannot be specialized")
        return cast(dom.Anchor, ref)

    @flux.property
    def contributions(self) -> frozenset[Entity.Contribution]:
        return frozenset()
