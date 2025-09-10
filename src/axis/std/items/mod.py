from __future__ import annotations

from typing import ClassVar, Optional

from axis.core import src, syn, log, sem, val
from axis.std.blocks import Use
from axis.std import expr
from .def_ import Def
from .val import Val
from protobase import cached_property, frozendict

class Mod(syn.Item):
    """
    Cometido: agrupar semanticamente un conjunto de sub-items.

    el modulo representa un espacio de nombres

    Example:
        mod axis.items:
            ...
    """

    keyword: ClassVar[str] = "mod"
    grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    path: expr.Member | expr.Sym

    @property
    def name(self) -> str:
        if isinstance(self.path, expr.Member):
            return self.path.as_sym()
        elif isinstance(self.path, expr.Sym):
            return self.path

        raise TypeError(f"Unexpected path type: {type(self.path)}")

    @classmethod
    def build(cls, kw, path: syn.Expr, *, children=tuple[syn.Block, ...]):
        return cls(path=path, children=children)

    class Binding(syn.Item.Binding):
        item: Mod

        @cached_property
        def ref(self):
            return val.Ref.from_expr(self.item.path, base_ref=self.parent.ref)

Mod.add_child_block(Mod, must_be_indented=True)
Mod.add_child_block(Use, must_be_indented=True)
Mod.add_child_block(Val, must_be_indented=True)
Mod.add_child_block(Def, must_be_indented=True)
