from textwrap import dedent
from typing import Self
from axis.core import syn, src

class Doc(syn.Block):
    keyword: str = ("---", '')
    content: str    
    
    @classmethod
    def parse_block(cls, tree: src.Outline.Tree, children: tuple[syn.Block]) -> Self:
        """
        Parse the tree and return a Doc instance.
        """
        return cls(
            children=children,
            content=dedent(tree.content)
        )

syn.Item.register_child_block_type(Doc, must_be_indented=None)