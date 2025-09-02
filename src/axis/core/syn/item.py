from typing import ClassVar, Generator, Iterable, Self
from .block import Block
from axis.core import val

class Item(Block, abstract=True):
    '''
    Represents a module item, such as a function, class, or variable declaration.
    '''
    grammar_context_infix: ClassVar[str] = 'Item'
    @property
    def name(self) -> str:
        raise NotImplementedError(
            f"{type(self).__qualname__} does not implement 'name' property"
        )


    def generate_content_manifest_entries(self, base_ref: val.Ref)-> Generator[tuple[val.Ref, 'Item'], None, None]:
        raise NotImplementedError(
            f"{type(self).__qualname__} does not implement 'generate_globals' method"
        )    

    def split_subitems(self) -> tuple[Self, tuple['Item', ...]]:
        items = tuple(child for child in self.children if isinstance(child, Item))
        others = tuple(child for child in self.children if not isinstance(child, Item))
        return self.with_attr(children=others), items

    def bind(self, binder: 'sem.Binder') -> 'sem.Binding':
        raise NotImplementedError(
            f"{type(self).__qualname__} does not implement 'bind' method"
        )