#%%
from pathlib import Path
from typing import TypedDict
import unittest
from axis.parsing import Parser
from rich import print

SRCBLOCK_SPEC_PATH = Path("src/axis/codebase/grammar/srcblock-spec.yaml")
SOURCE_UNIT_PATH = Path("src/std.base.tests.src/test.ax")

UNIT_PATH = Path('test.ax')

class GrammarTest(unittest.TestCase):
    parser = Parser()

    def test_parser(self):

        unit = self.parser.parse_unit(UNIT_PATH, "def Vector()")
        print(unit)
