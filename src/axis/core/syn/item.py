from __future__ import annotations
from typing import ClassVar, Generator, Iterable, Optional, Self
from warnings import warn
from .block import Block
from axis.core import val, sem
from protobase import Record


class Item(Block, abstract=True):
    """
    Represents a module item, such as a function, class, or variable declaration.
    """

    grammar_context_infix: ClassVar[str] = "Item"

    @property
    def name(self) -> Optional[str]:
        warn(f"{type(self).__qualname__} does not implement 'name' property")
        return None

    def split_subitems(self) -> tuple[Self, tuple["Item", ...]]:
        items = tuple(child for child in self.children if isinstance(child, Item))
        others = tuple(child for child in self.children if not isinstance(child, Item))
        return self.with_attr(children=others), items

    class Binding(Record, frozen=True, abstract=True):
        """
        multiples bindings compondran las entidades
        """
        #pkg: 'Package'
        parent: Optional[Item.Binding]  # actua como scope
        item: Item

        @classmethod
        def generate_from(
            cls,
            item: Item,
            parent: Optional[Item.Binding] = None,
        ) -> Iterable[Item.Binding]:
            item, subitems = item.split_subitems()

            binding = item.bind(parent)

            yield binding

            for subitem in subitems:
                yield from cls.generate_from(subitem, parent=binding)

        @property
        def ref(self) -> val.Ref:
            raise NotImplementedError(f"Binding.ref not implemented in {type(self)}")

        @property 
        def scope(self):
            scope_builder = sem.Scope.Builder(
                parent=self.parent.scope if self.parent else None,
                name=self.item.name,
            )

            for child in self.item.children:
                child.contribute_to_scope(scope_builder)

            return scope_builder.build()

    def bind(self, parent: Item.Binding) -> Item.Binding:
        return self.Binding(parent=parent, item=self)
