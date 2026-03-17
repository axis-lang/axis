# %%
import unittest
from decimal import Decimal

from axis import expr
from axis import items, syn
from tests.helpers import StdPackageTestCase

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

        match_test = syn.Matcher.from_str("$ctx.$name($a, ..$b, $c)")
        #print(match_test.patterns[0])

        match = match_test("Natural.alpha(1,2,3,4,5)")
        assert match is not None

        self.assertEqualExpr(match["ctx"], "Natural")
        #self.assertEqualExpr(match["$name"], "Natural.alpha")
        self.assertEqualExpr(match["name"].as_(expr.Sym), "alpha")
        self.assertEqualExpr(match["a"], "1")
        self.assertEqualExpr(match["b"], "(2, 3, 4)")
        self.assertEqualExpr(match["c"], "5")



class ProjectionMatchTest(unittest.TestCase):
    def assertEqualExpr(self, expr: syn.Expr, expected: syn.Expr | str):
        if isinstance(expected, str):
            expected = syn.Expr.from_str(expected)
        self.assertEqual(expr, expected)

    class MemberNameStr(syn.ClassMatcher):
        match_patterns = (syn.Expr.from_str("$ctx.$name"),)
        ctx: expr.Sym
        name: str

    class MemberNameUnion(syn.ClassMatcher):
        match_patterns = (syn.Expr.from_str("$ctx.$name"),)
        ctx: expr.Sym
        name: str | expr.Sym

    class SymNameStr(syn.ClassMatcher):
        match_patterns = (syn.Expr.from_str("$sym"),)
        sym: str

    def test_member_name_str_projection(self):
        result = self.MemberNameStr.match("Natural.alpha")
        assert result is not None
        self.assertEqual(result.name, "alpha")
        self.assertEqualExpr(result.ctx, "Natural")

    def test_member_name_union_projection(self):
        result = self.MemberNameUnion.match("Natural.alpha")
        assert result is not None
        self.assertIsInstance(result.name, str)
        self.assertEqual(result.name, "alpha")

    def test_sym_name_str_projection(self):
        result = self.SymNameStr.match("Natural")
        assert result is not None
        self.assertEqual(result.sym, "Natural")








# def test_parser(self):
#     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
#     print(unit)
# ol = std.Unit.build_ouline_spec()
# file = src.File.from_path(SOURCE_UNIT_PATH)
# unit = ol.parse_outline(file)

# scoping = sem.ScopingPass(None, std.Sym.ROOT)
# scoping.process_item(unit)


class DatabaseSmokeTest(StdPackageTestCase):
    def test_database_build(self):
        entities = self.pkg.entities_by_anchor
        members = self.pkg.namespaces_by_anchor
        self.assertGreater(len(entities), 0)
        self.assertGreater(len(members), 0)

    def test_database_is_cached(self):
        entities_1 = self.pkg.entities_by_anchor
        entities_2 = self.pkg.entities_by_anchor
        self.assertIs(entities_1, entities_2)


# def test_parser(self):
#     unit = self.parser.parse_unit(SOURCE_UNIT_PATH)
#     print(unit)
# ol = std.Unit.build_ouline_spec()
# file = src.File.from_path(SOURCE_UNIT_PATH)
# unit = ol.parse_outline(file)

# scoping = sem.ScopingPass(None, std.Sym.ROOT)
# scoping.process_item(unit)
