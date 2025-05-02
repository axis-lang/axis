"""
el proceso semantico reduce todo a referencias y entidades, donde una entidad
es constituida por (una referencia) un ast y un contexto.

def Entity
takes: 
    val ref: Ref Item
    val ast: Ast Item
    val context: Context
returns Item
where:
    val Item: Type 

Entity[Mod] -> Mod
Ref[Mod]

"""

from __future__ import annotations
from functools import singledispatch
from typing import Optional, Self
from axis.dom import ref, syn
from protobase import Record

class Context[T = ref.Ref](Record, frozen=True):
    '''
    contexto semantico
    '''
    class Builder[T = ref.Ref](Record):
        name: Optional[str] = None
        parent: Optional[Context] = None
        symbols: dict[str, set[tuple[ref.Ref, syn.Item]]] = {}

        def add_item(self, ref: ref.Ref, item: syn.Item, with_name: Optional[str] = None) -> Self:
            self.symbols.setdefault(with_name or item.name, set()).add((ref, item))


        def build(self) -> Context[T]:
            # TODO: frozen and check duplicates..
            return Context(
                name=self.name,
                parent=self.parent,
                symbols=self.symbols,
            )

    symbols: dict[str, T]
    parent: Optional[Self] = None
    name: Optional[str] = None

    def lookup(self, name: str, at: Optional[str] = None) -> Optional[T]:

        if at is None or self.name == at:
            try: 
                return self.symbols[name]
            except KeyError:
                pass

        if self.parent is not None:
            return self.parent.lookup(name, at)

        return None
    



@singledispatch
def build_context(item: syn.Item, ref: ref.Ref, parent: Context) -> Context:
    raise NotImplementedError(f"sem.build_context not implemented for {type(item)}")




@build_context.register
def _build_context_mod(
    item: syn.Mod,
    ref: ref.Unit,
    parent: Context,
) -> Context:
    '''
    construye el contexto de un modulo
    '''
    ctx = Context.Builder('mod')
    ctx.add_symbol('self', ref)
    for member in item.members():
        ctx.add_symbol(member.name, ref.member(member.name))
    return ctx.build()

