from __future__ import annotations
from typing import Iterable, Optional, Self
from protobase import Record
from axis import syn, dom, sem

from .scope import Scope

class Binding(Record, frozen=True, abstract=True):
    """
    multiples bindings compondran las entidades
    """
    pkg: sem.Package
    parent: Optional[Binding]  # actua como scope
    item: syn.Item

    @classmethod
    def generate_from(
        cls,
        item: syn.Item,
        pkg: sem.Package,
        parent: Optional[Binding] = None,
    ) -> Iterable[Binding]:
        item, subitems = item.split_subitems()

        binding = item.Binding(pkg=pkg, parent=parent, item=item)

        yield binding

        for subitem in subitems:
            yield from cls.generate_from(subitem, pkg=pkg, parent=binding)

    @property
    def ref(self) -> dom.Ref:
        raise NotImplementedError(f"Binding.ref not implemented in {type(self)}")

    @property 
    def scope(self):
        scope_builder = Scope.Builder(
            parent=self.parent.scope if self.parent else None,
            name=self.item.name,
        )

        for child in self.item.children:
            child.contribute_to_scope(scope_builder)

        return scope_builder.build()
