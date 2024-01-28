import unittest
from axis.syn import Parser, Infix, Prefix, Lit, Id


class TestSyn(unittest.TestCase):
    def setUp(self):
        self.expr_parser = Parser()

    def test_operator_precedence(self):
        ast = self.expr_parser.expr("1 + 2 * 3")
        self.assertEqual(
            repr(ast),
            "Infix(Lit(value=1), Infix(Lit(value=2), Lit(value=3), Op('mul')), Op('add'))",
        )


if __name__ == "__main__":
    unittest.main()
