from functools import cached_property
from typing import Self, Sequence
from protobase import Record, frozendict

from axis import src, val, syn
from .binding import Binding

class GlobalIndex(Record, frozen=True):

    class Entry(Record, frozen=True):
        ref: val.Ref
        children: frozenset[val.Ref]
        bindings: tuple[Binding]

    @classmethod
    def from_bindings(cls, bindings: Sequence[Binding]) -> Self:
        entry_map: dict[val.Ref, tuple[list[Binding], list[val.Ref]]] = {}
        for binding in bindings:
            ref = binding.ref

            entry_map.setdefault(ref, ([], []))[0].append(binding)
            entry_map.setdefault(ref.parent, ([], []))[1].append(ref)

        return cls(
            entries=frozendict(
                (
                    ref,
                    cls.Entry(
                        ref=ref,
                        bindings=tuple(bindings),
                        children=frozenset(children),
                    ),
                )
                for ref, (bindings, children) in entry_map.items()
            )
        )

    entries: frozendict[val.Ref, Entry]


# # la tabla de bindings es para cada package (por sus dependencias y definiciones propias)
# bindings: dict[val.Ref, set[syn.Item.Binding]] = {}
# for binding in syn.Item.Binding.generate_from(unit, parent=root_binding):
#     bindings.setdefault(binding.ref, set()).add(binding)

# # establece el contexto de flujo en el que hacer consultas..
# for binding in bindings[val.Ref.from_expr("alpha.beta")]:
#     print(binding.item.name)
#     print(binding.scope)
