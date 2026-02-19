# %%
import unittest
from decimal import Decimal

from axis import expr
from axis import items, syn

# SRCBLOCK_SPEC_PATH = Path("src/axis/codebase/grammar/srcblock-spec.yaml")
# SOURCE_UNIT_PATH = Path("src/std.base.tests.src/test.ax")


class GrammarTest(unittest.TestCase):
    # parser = Parser()

    def test_parse_expr(self):
        self.assertEqual(
            syn.Expr.from_str("1 + 2"),
            expr.Additive(
                lhs=expr.Lit(Decimal(1)),
                rhs=expr.Lit(Decimal(2)),
                op=expr.Additive.Op.from_str("+"),
            ),
        )

    def test_parse_tuple(self):
        e = syn.Expr.from_str(
            """(
            a, 
            a:b, 
            a=b, 
            a:b=c,
            ..alpha,
            )"""
        )
        # print(e)


class ExprMatchingTest(unittest.TestCase):
    # parser = Parser()

    def assertEqualExpr(self, expr: syn.Expr, expected: syn.Expr | str):
        if isinstance(expected, str):
            expected = syn.Expr.from_str(expected)
        self.assertEqual(expr, expected)

    def test_unify(self):

        match_test = syn.Match.from_expr("$ctx.$name($a, ..$b, $c)")
        #print(match_test.patterns[0])

        match = match_test("Natural.alpha(1,2,3,4,5)")
        assert match is not None

        self.assertEqualExpr(match["ctx"], "Natural")
        #self.assertEqualExpr(match["$name"], "Natural.alpha")
        self.assertEqualExpr(match["name"], "alpha")
        self.assertEqualExpr(match["a"], "1")
        self.assertEqualExpr(match["b"], "(2, 3, 4)")
        self.assertEqualExpr(match["c"], "5")



class ExprReificationTest(unittest.TestCase):
    # parser = Parser()

    def assertEqualExpr(self, expr: syn.Expr, expected: syn.Expr | str):
        if isinstance(expected, str):
            expected = syn.Expr.from_str(expected)
        self.assertEqual(expr, expected)

    def test_reify(self):
        match = syn.Match.from_expr("$m.$n($a, ..$etc, $b)")
        reify = syn.Reify.expr("$n.$m($b, ..$etc, $a)")

        vals = match("foo.bar(1, 2, 3, 4, 5)")
        #print(vals)


        #print(reify(vals))








# def test_parser(self):
#     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
#     print(unit)
# ol = std.Unit.build_ouline_spec()
# file = src.File.from_path(SOURCE_UNIT_PATH)
# unit = ol.parse_outline(file)

# scoping = sem.ScopingPass(None, std.Sym.ROOT)
# scoping.process_item(unit)


class DatabaseSmokeTest(unittest.TestCase):
    def test_database_build(self):
        pkg = items.Package.from_path("codebase/std-core")
        db = pkg.database
        self.assertGreater(len(db.entities_by_shape), 0)
        self.assertGreater(len(db.members_by_scope), 0)


# def test_parser(self):
#     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
#     print(unit)
# ol = std.Unit.build_ouline_spec()
# file = src.File.from_path(SOURCE_UNIT_PATH)
# unit = ol.parse_outline(file)

# scoping = sem.ScopingPass(None, std.Sym.ROOT)
# scoping.process_item(unit)
