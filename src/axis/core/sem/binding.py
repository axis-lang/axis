from __future__ import annotations
from typing import Iterable, Optional, Self
from protobase import Record

from axis.core import syn, src, log, val

## binding va en syn.Item.Binding pues esta a medio camino del proceso sintactico / semantico
class Binding(Record, frozen=True):
    """
    multiples bindings compondran las entidades
    """

    parent: Optional[Binding]  # actua como scope
    ref: val.Ref
    item: syn.Item

    @classmethod
    def generate_from(
        cls,
        item: syn.Item,
        parent: Optional[Binding] = None,
    ) -> Iterable[Binding]:
        item, subitems = item.split_subitems()

        binding = item.bind(parent)

        yield binding

        for subitem in subitems:
            yield from cls.generate_from(subitem, parent=binding)
