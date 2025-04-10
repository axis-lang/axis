# %%
from pathlib import Path

from axis.codebase.filesystem import FileSystemLayer
from axis.parser.grammar import parse_item
from axis.parser.srcblock import Parser as SrcBlockParser
from axis.parser.srcblock import SrcBlock
from axis.std import core, syn
from axis.std.core import Id

SRC_BLOCK_SPEC_FILE = Path("src/axis/codebase/grammar/srcblock-spec.yaml")


class ASTLayer(FileSystemLayer, abstract=True):

    @property
    def ast_srcblock_parser(self) -> SrcBlockParser:
        return SrcBlockParser.from_yaml(SRC_BLOCK_SPEC_FILE)

    def ast_unit(self, unit_id: core.Id):
        unit_path = self.fs_unit_paths.get(unit_id, None)
        if not unit_path:
            raise ValueError(f"Unit {unit_id} not found")

        unit_content = unit_path.read_text()  # fs_unit_source(unit_id)

        block_tree = self.ast_srcblock_parser.parse("unit", unit_content)

        return block_tree.transform(_process_block)

    @property
    def ast_index(self) -> dict[syn.Item]:
        ...


def _process_block(block: SrcBlock, children: list):
    match block.type:
        case "unit":
            return children

        case "def":
            (id,) = parse_item("defBlock", block.content)
            # block.content
            # parse def block
            # parse where sub-blocks
            return syn.Def(
                doc=(),
                id=id,
                takes=syn.Def.Takes(values=()),
                where=syn.Def.Where(bounds=()),
                as_=syn.Def.As(expr=None),
            )
        case 'takes':
            return None

        case "var":
            def_ast = parse_item("varBlock", block.content)
            block.content
            # parse def block
            # parse where sub-blocks
            return block

        case _:
            return None


def _parse_def_content(content): ...
