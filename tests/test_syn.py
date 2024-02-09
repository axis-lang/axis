import unittest
from axis.front.syn.ast import Parser, Infix, Prefix, Lit, Id
from rich import print


class TestOperators(unittest.TestCase):
    def setUp(self):
        self.expr_parser = Parser()

    def test_op(self):
        ast = self.expr_parser.expr("a + b * c ** d")
        print(ast)


class TestExpr(unittest.TestCase):
    def setUp(self):
        self.expr_parser = Parser()

    # def test_operator_precedence(self):
    #     ast = self.expr_parser.expr("1 + 2 * 3")
    #     self.assertEqual(
    #         repr(ast),
    #         "Infix(Lit(value=1), Infix(Lit(value=2), Lit(value=3), Op('mul')), Op('add'))",
    #     )

    def test_tuple(self):
        ast = self.expr_parser.expr("(a: 1, 2, ..4)")
        print(ast)


if __name__ == "__main__":
    unittest.main()
