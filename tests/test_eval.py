import unittest
from decimal import Decimal

from axis import dom, syn, val


class EvalTest(unittest.TestCase):
    def eval(self, source: str, env=None) -> dom.Const:
        evaluator = val.Evaluator.from_env(env or {})
        return evaluator(syn.Expr.from_str(source))

    def test_eval_literal(self):
        result = self.eval("12")
        self.assertEqual(result.data, 12)
        self.assertTrue(isinstance(result.type, dom.NominalType))
        if isinstance(result.type, dom.NominalType):
            self.assertEqual(dom.ref_segments(result.type.ref), ("std", "Integer"))

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
        self.assertTrue(isinstance(result.type, dom.StructType))

    def test_eval_symbol_from_env(self):
        result = self.eval(
            "alpha",
            env={
                "alpha": dom.Const(
                    type=dom.NominalType.from_str("std.Natural"),
                    data=5,
                )
            },
        )
        self.assertEqual(result.data, 5)

    def test_eval_unbound_symbol(self):
        with self.assertRaises(Exception):
            self.eval("beta")

    def test_ref_from_str(self):
        ref = dom.Anchor.from_str("std.Array")
        self.assertEqual(dom.ref_segments(ref), ("std", "Array"))

    def test_type_var_helper(self):
        meta = dom.Var.Type(id="T")
        self.assertTrue(isinstance(meta, dom.Var.Type))
        if isinstance(meta, dom.Var.Type):
            self.assertEqual(meta.id, "T")

    def test_nominal_schema_opaque(self):
        meta = dom.NominalType.from_str("std.Text")
        if isinstance(meta, dom.NominalType):
            self.assertTrue(isinstance(meta.ref, dom.Ref))

    def test_nominal_params_with_var_encoding(self):
        param = dom.Const.from_literal(3)
        fields = dom.Struct.new(size=param.type)
        spec = dom.Const(type=dom.StructType(fields=fields), data=(param.data,))
        base = dom.Anchor.from_str("std.Array")
        ref = base.specialize(spec)
        meta = dom.NominalType.from_ref(ref)
        if isinstance(meta, dom.NominalType):
            self.assertTrue(isinstance(meta.ref, dom.Ref))
