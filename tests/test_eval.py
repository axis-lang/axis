import unittest
from decimal import Decimal

from axis import dom, syn, val


class EvalTest(unittest.TestCase):
    def eval(self, source: str, env=None) -> dom.Val:
        evaluator = val.Evaluator.from_env(env or {})
        return evaluator(syn.Expr.from_str(source))

    def test_eval_literal(self):
        result = self.eval("12")
        self.assertEqual(result.data, 12)
        self.assertTrue(isinstance(result.meta, dom.Type))

    def test_eval_additive(self):
        result = self.eval("1 + 2")
        self.assertEqual(result.data, 3)

    def test_eval_productive(self):
        result = self.eval("6 * 7")
        self.assertEqual(result.data, 42)

    def test_eval_decimal_division(self):
        result = self.eval("1 / 2")
        self.assertEqual(result.data, Decimal("0.5"))

    def test_eval_tuple(self):
        result = self.eval("(1, 2, 3)")
        self.assertEqual(result.data, (1, 2, 3))
        self.assertTrue(isinstance(result.meta.form, dom.Struct))

    def test_eval_symbol_from_env(self):
        result = self.eval("alpha", env={"alpha": (dom.Type(form=dom.Nominal(ref=dom.Ref.from_str("std.Natural"), params=dom.Const(meta=dom.Type(form=dom.Struct(fields=dom.Tuple.EMPTY)), data=()), schema=None)), 5)})
        self.assertEqual(result.data, 5)

    def test_eval_unbound_symbol(self):
        with self.assertRaises(Exception):
            self.eval("beta")
