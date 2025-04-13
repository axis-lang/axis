# %%
from pathlib import Path

from axis.codebase.fs import FileSystemLayer
from axis.parsing import Parser
from axis.std import Id


class SyntacticLayer(FileSystemLayer, abstract=True):
    @property
    def syn_parser(self) -> Parser:
        return Parser()
    
    def ast_of_unit(self, unit_id: Id):
        unit_path = self.fs_units.get(unit_id, None)
        if not unit_path:
            raise ValueError(f"Unit {unit_id} not found")
        return self.syn_parser.parse_unit(unit_path)
