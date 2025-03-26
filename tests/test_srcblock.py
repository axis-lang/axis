#%%
from pathlib import Path
from typing import TypedDict
import unittest
from srcblock import Parser
from rich import print

SRCBLOCK_SPEC_PATH = Path("src/axis/srcbase/srcblock-spec.yaml")
SOURCE_UNIT_PATH = Path("src/testsuite.src/test.ax")

class SrcBlockTest(unittest.TestCase):
    def test_parser(self):
        parser = Parser.from_yaml(SRCBLOCK_SPEC_PATH)
        content = SOURCE_UNIT_PATH.read_text()
        block = parser.parse("unit", content)
        

parser = Parser.from_yaml(SRCBLOCK_SPEC_PATH)
content = SOURCE_UNIT_PATH.read_text()
block = parser.parse("unit", content)



print(block)