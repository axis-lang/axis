from typing import ClassVar

from protobase import flux

from axis import dom
from axis.sem import Database

from .mod import Mod
from .ref import ref_from_expr

class Unit(Mod):
    outline_keyword: ClassVar[str] = "unit"

    @flux.property
    def ref(self) -> dom.Ref:
        if self.path is None:
            raise ValueError("Unit requires a path to build its ref")
        return ref_from_expr(self.path, None)

    @flux.property
    def contributions(self) -> frozenset[Database.Contribution]:
        if self.path is None:
            return frozenset()
        return frozenset((Database.Namespace(anchor=self.ref, origin=self.path, ctx=self),))
