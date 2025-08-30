from __future__ import annotations
from functools import singledispatch
from typing import Annotated, ClassVar, Optional

from axis.core import src, syn, ref, log, sem
from axis.std.transcriptions.sym_to_member import sym_to_member_of


class Mod(syn.Item):
    """
    Represents a module item.

    un modulo contiene un espacio de nombres de primer orden (o global)
    de sub items.

    Example:
        mod axis.items:
            ...
    """

    keyword: ClassVar[str] = "mod"
    grammar: ClassVar[str] = "mod: 'mod' expression ':' EOF;"

    path: syn.Expr # mount path
    # las unidades tienen un montaje absoluto, los modulos son relativos, las funciones pueden ser relativas a la unidad o definidas en un 

    def generate_content_manifest_entries(self, base_ref: ref.Ref = ref.Ref.root):
        base = ref.eval(self.path, base=base_ref)
        for child in self.children:
            if isinstance(child, syn.Item):
                yield from child.generate_content_manifest_entries(base)

    @classmethod
    def build(cls, kw, path: syn.Expr, *, children=tuple[syn.Block]):
        return cls(path=path, children=children)

# @syn.AstBuilder.build.register(syn.AxisParser.ModItemContext)
# def build_ast(
#     self,
#     _,
#     path: syn.Expr,
#     children: tuple[syn.Block],
# ):
#     return Mod(path=path, children=children)


@sem.Binder.discover.register(Mod)
def discover_mod(parent: sem.Binder, mod: Mod):
    # eval_ref -> ref
    path = sym_to_member_of(mod.path, of=parent.path)

    mod_binder = parent.child(mod, path)

    for block in iter(mod):
        #if isinstance(block, syn.Item):
        mod_binder.discover(block)

    print(mod_binder.imports)
