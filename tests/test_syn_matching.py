# %%
from functools import singledispatchmethod
from pathlib import Path
from typing import TypedDict
import unittest
from rich import print
from axis.core import syn, src, sem
from axis import std

class ExprMatchingTest(unittest.TestCase):
    # parser = Parser()

    def test_unify(self):
        match_test = syn.Match.expr("$ctx.$name($a, ..$b, $c)")
        match_expr = syn.Expr.parse("Natural.alpha(1,2,5,5,3)")
        print(match_test.pattern)
        print(match_expr)
        print(match_test(match_expr))




    # def test_parser(self):
    #     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
    #     print(unit)
        # ol = std.Unit.build_ouline_spec()
        # file = src.File.from_path(SOURCE_UNIT_PATH)
        # unit = ol.parse_outline(file)

        # scoping = sem.ScopingPass(None, std.Sym.ROOT)
        # scoping.process_item(unit)
