from pathlib import Path
from typing import ClassVar

from axis.core import sem, syn
from axis.std.blocks import Use

from .def_ import Def
from .mod import Mod
from .val import Val


class Unit(Mod):
    """ """

    keyword: ClassVar = "unit"
    grammar: ClassVar = "unit: 'unit' expression ':' EOF;"

    @classmethod
    def build(cls, kw, path: syn.Expr, *, children=tuple[syn.Block]):
        return cls(path=path, children=children)



Unit.add_child_block(Mod, must_be_indented=False)
Unit.add_child_block(Use, must_be_indented=False)
Unit.add_child_block(Val, must_be_indented=False)
Unit.add_child_block(Def, must_be_indented=False)
