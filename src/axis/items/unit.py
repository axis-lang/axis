
from typing import ClassVar

from axis import syn

from .mod import Mod


class Unit(Mod):
    """ """

    keyword: ClassVar = "unit"
    grammar: ClassVar = "unit: 'unit' expression ':' EOF;"

    @classmethod
    def build(cls, kw, path: syn.Expr, *, children=tuple[syn.Block]):
        return cls(path=path, children=children)


