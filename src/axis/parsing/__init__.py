from pathlib import Path
from typing import Optional

from protobase import Object
from rich import print

from axis.parsing.grammar import ast_parser_for
from axis.parsing.srcblock import Parser as OutlineParser
from axis.parsing.srcblock import SrcBlock
from axis.std import syn

SRC_BLOCK_SPEC_FILE = Path("src/axis/parsing/srcblock-spec.yaml")

IGNORE = object()


class Parser(Object):
    """
    Objeto utilizado en la capa AST para generar
    el AST a partir del codigo fuente.
    """

    @property
    def ouline_parser(self) -> OutlineParser:
        return OutlineParser.from_yaml(SRC_BLOCK_SPEC_FILE)
    
    def parse_unit(self, path: Path, content: Optional[str] = None) -> syn.Unit:
        """
        Parse a file and return the AST.
        """
        if content is None:
            content = path.read_text()

        outline = self.ouline_parser.parse("unit", content)

        return outline.transform(self.process_outline)

    KNOW_ITEMS = {
        'doc': (syn.Doc, lambda content: {'content': content}),
        'unit': (syn.Unit, None),
        'def': (syn.Def, ast_parser_for("defItem")),
        'val': (syn.Val, ast_parser_for("valItem")),
        'takes': (syn.Takes, None),
        'where': (syn.Where, None),
        'returns': (syn.Returns, ast_parser_for('returnsBlock')),
        'suite': (syn.Suite, ast_parser_for('suiteBlock')),
    }


    def process_outline(self, block: SrcBlock, children: list):
        #print("--")
        #print(block.content)
        block_cls, parser = self.KNOW_ITEMS.get(block.type, (None, None))
        if block_cls is None:
            raise TypeError(f"Unknown block type {block.type}")
        attrs = parser(block.content) if parser else {}
        return block_cls(tuple(children), **attrs)

