from __future__ import annotations
from functools import singledispatch
from typing import Annotated, Optional, Self
from typing_extensions import Doc
from protobase import Record, frozendict, Object
from axis.dom import syn, Id, ref


class Scoping(Record, frozen=True):  # EntityScoping
    """
    Semantic scoping.

    esta clase actua como protoentidad, en el paso previo al
    binding.

    Interfaces de una entidad semantica:
    - `entity.member` una entidad puede ser accedida como namespace.
    - `entity[hyperparameters]` indexada con hiperparametros.
    - `entity(args...)`  llamada con argumentos
    - `val value: T = entity` o resuelta como valor
    """

    class Builder(Object):
        """
        Builder para crear un scoping.
        """

        name: Optional[str] = None
        parent: Optional[Scoping] = None
        symbols: dict[str, set[tuple[ref.Ref, syn.Item]]] = {}

        def add_item(self, ref: ref.Ref, item: syn.Item, with_name: Optional[str] = None) -> Self:
            self.symbols.setdefault(with_name or item.name, set()).add((ref, item))

        def build(self) -> Scoping:
            ...


    symbols: dict[str, ref.Ref]
    

    members: Annotated[
        Optional[frozendict[str, frozenset[Scoping]]],
        Doc(""" """),
    ]

    ast: Annotated[
        syn.Item, 
        Doc(""" 
        """),
    ]

    @classmethod
    def for_item(cls, mod_ast: syn.Mod) -> Self:
        return _make_scoping_for_item(cls, mod_ast)


def _make_scoping_for_item(
    cls: type[Scoping],
    ast: syn.Item,
) -> Scoping:
    """
    crea un item a partir de un ast
    """
    members: dict[str, set[Scoping]] = {}

    for member in ast.members():
        # TODO: Handle multiple names for a member (e.g., `val (a, b): (a: Real, b: Real)`).
        # where multiple names (members) share the same AST (and scoping?)
        member_scoping = _make_scoping_for_item(cls, member)
        members.setdefault(member.name, set()).add(member_scoping)

    return cls(
        ast=ast,
        members=frozendict(
            {name: frozenset(members) for name, members in members.items()}
        ),
    )
