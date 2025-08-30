from typing import ClassVar, Generator
from .block import Block
from axis.core import ref

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


    def generate_content_manifest_entries(self, base_ref: ref.Ref)-> Generator[tuple[ref.Ref, 'Item'], None, None]:
        raise NotImplementedError(
            f"{type(self).__qualname__} does not implement 'generate_globals' method"
        )