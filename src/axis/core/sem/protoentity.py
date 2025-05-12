"""
Como resultado del procesamiento de un modulo se obtendra un dict[ref, Entity]
con entidades completamente desacompladas entre si.

las entidades retornan (injectan) el valor del item cuando son resueltas a valor,
por ejemplo:

def mod
takes:
    val ref: ref.Mod
    val members: Mapping[Symbol] Ref.Member

estos valores son evaluables desde el propio codigo axis ;)

las entidades de segundo y tercen orden (generics y overloads respectivamente)
seran chequeadas para:
    - colision (si sus referencias son iguales no pueden ser emitidas)
    - ambiguedad (algunas resoluciones pueden hacer referencia a varias entidades)
    - alcanzabilidad (si no existe ninguna resolucion posible para alcanzar la entidad)
"""

from __future__ import annotations
from typing import Optional, Self
from protobase import Record, frozendict
from axis.core import ref, syn


class Context[T = ref.Ref](Record, frozen=True):
    ref: ref.Ref # referencia a la entidad del contexto
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
    

class ProtoEntity(Record, frozen=True):
    ref: ref.Ref
    context: Context
    ast: Optional[syn.Item]

    # first order sub entities (members)
    members: frozendict[str, ProtoEntity]

    # second order sub entities (generics and overloads)
    class GenericIndex(Record, frozen=True):
        entries: tuple[syn.Item]

    generics: GenericIndex

    class OverloadIndex(Record, frozen=True):
        entries: tuple[syn.Item]

    overloads: OverloadIndex



def collect_first_order_entities(
    cls: type[ProtoEntity],
    ref: ref.Ref,
    item: Optional[syn.Item],
    parent_context: Context,
) -> ProtoEntity:
    """
    crea una protoentidad a partir de un ast
    """
    assert item.if_first_order, f"{item} must be first order"

    def recursion(
        ref: ref.Ref,
        item: Optional[syn.Item],
        parent_context: Context,
    ):

        # agrupa los miembros por nombre
        members: dict[str, set[syn.Item]] = {}
        for member in item.members():
            members.setdefault(member.name, set()).add(member)

        # genera la referencia para esta entidad

        # crea el contexto de resolucion
        ctx = Context(
            name=item.name,
            parent=parent_context,
            symbols=frozenset({name: ref.member(name) for name in members}),
        )

        

        # # build the resolution context
        # ctx = Context.Builder(name=item.name)
        # # TODO: using
        # #for using in item.usings(): ...
        #     ctx.add_item(ref.member(member.name), member)
        # ctx = ctx.build()

    recursion(ref, item, parent_context)
