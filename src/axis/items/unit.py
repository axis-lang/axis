from typing import ClassVar, cast

from protobase import flux

from axis import expr
from .mod import Mod

class Unit(Mod):
    outline_keyword: ClassVar[str] = "unit"

    # @flux.property
    # def ref(self) -> std.Anchor:
    #     if self.path is None:
    #         raise ValueError("Unit requires a path to build its ref")
    #     ref = expr.to_spec_ref(self.path, None)
    #     if ref is None:
    #         raise ValueError("Unit requires a path to build its ref")
    #     if isinstance(ref, std.Spec):
    #         raise ValueError("Unit ref cannot be specialized")
    #     return cast(std.Anchor, ref)

    # @flux.property
    # def contributions(self) -> frozenset[Entity.Contribution]:
    #     return frozenset()
