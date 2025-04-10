#%%
from pathlib import Path
from typing import TypedDict
import unittest
from axis.parsing import Parser
from rich import print

SRCBLOCK_SPEC_PATH = Path("src/axis/codebase/grammar/srcblock-spec.yaml")
SOURCE_UNIT_PATH = Path("src/std.base.tests.src/test.ax")

class GrammarTest(unittest.TestCase):
    parser = Parser()

    def test_parser(self):

        unit = self.parser.parse_unit(Path('test.ax'), "def Vector(a+b)")
        print(unit)

    def test_parser(self):

        unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
        print(unit)

