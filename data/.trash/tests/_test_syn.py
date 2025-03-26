import unittest
from axis.front.syn.ast import Parser, Infix, Prefix, Lit, Id
from rich import print


class TestParser(unittest.TestCase):
    def setUp(self):
        self.expr_parser = Parser()

    def print_expr_ast(self, expr: str):
        ast = self.expr_parser.expr(expr)
        print(expr)
        print(ast)

    def test_op(self):
        self.print_expr_ast("a + b * c ** d")

    def test_tuple(self):
        self.print_expr_ast("(a: 1, 2, ..4)")


if __name__ == "__main__":
    unittest.main()
