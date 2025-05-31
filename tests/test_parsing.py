# %%
from decimal import Decimal
from pathlib import Path
from typing import TypedDict
import unittest
from rich import print
from axis.core import syn, src, sem
from axis import std


SRCBLOCK_SPEC_PATH = Path("src/axis/codebase/grammar/srcblock-spec.yaml")
SOURCE_UNIT_PATH = Path("src/std.base.tests.src/test.ax")


class GrammarTest(unittest.TestCase):
    # parser = Parser()

    def test_parse_expr(self):
        self.assertEqual(
            syn.Expr.parse("1 + 2"),
            std.BinOp(
                lhs=std.Lit(Decimal(1)),
                rhs=std.Lit(Decimal(2)),
                op=std.BinOp.Operator('+'),
            ),
        )

    def test_parse_tuple(self):
        e = syn.Expr.parse(
            """(
            a, 
            a:b, 
            a=b, 
            a:b=c,
            ..alpha,
            )"""
        )
        #print(e)


# a: -1..1 = 0


# def test_parser(self):
#     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
#     print(unit)
# ol = std.Unit.build_ouline_spec()
# file = src.File.from_path(SOURCE_UNIT_PATH)
# unit = ol.parse_outline(file)

# scoping = sem.ScopingPass(None, std.Sym.ROOT)
# scoping.process_item(unit)
