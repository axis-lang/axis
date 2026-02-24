from typing import ClassVar
from protobase import Inmutable
from .mod import Mod

class Unit(Mod, Inmutable):
    outline_keyword: ClassVar[str] = "unit"

    def contribute(self, collector) -> None:
        if self.path is None:
            return
        collector.namespace(self.path, origin=self.path, ctx=self)
        collector.member(self.path, origin=self, ctx=self)
