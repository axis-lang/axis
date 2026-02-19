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

    def test_ref_from_str(self):
        ref = dom.Ref.from_str("std.Array")
        self.assertEqual(ref.segments, ("std", "Array"))

    def test_type_var_helper(self):
        meta = dom.Type.Var("T")
        self.assertTrue(isinstance(meta.form, dom.TypeVar))
        if isinstance(meta.form, dom.TypeVar):
            self.assertEqual(meta.form.id, "T")

    def test_nominal_schema_opaque(self):
        meta = dom.Type(
            form=dom.Nominal(
                ref=dom.Ref.from_str("std.Text"),
                params=dom.Const(meta=dom.Type(form=dom.Struct(fields=dom.Tuple.EMPTY)), data=()),
                schema=None,
            )
        )
        if isinstance(meta.form, dom.Nominal):
            self.assertIsNone(meta.form.schema)

    def test_nominal_params_with_var_encoding(self):
        params = dom.Const(
            meta=dom.Type(form=dom.Struct(fields=dom.Tuple.new("T"))),
            data=(("var", "T"),),
        )
        meta = dom.Type(
            form=dom.Nominal(
                ref=dom.Ref.from_str("std.Array"),
                params=params,
                schema=None,
            )
        )
        if isinstance(meta.form, dom.Nominal):
            self.assertEqual(meta.form.params.data, (("var", "T"),))

    def test_ref_to_val(self):
        ref = dom.Ref.from_str("std.Array")
        value = ref.to_val()
        self.assertEqual(value.data, ("std", "Array"))
        self.assertTrue(isinstance(value.meta, dom.Type))

    def test_type_to_val_literal(self):
        meta = dom.Type(form=dom.Literal(3))
        value = meta.to_val()
        self.assertEqual(value.data[0], "type")
        qualifiers_data, form_data = value.data[1]
        self.assertEqual(qualifiers_data, ())
        tag_data, payload = form_data
        self.assertEqual(tag_data, ("std", "Type", "Literal"))
        self.assertEqual(payload, 3)

    def test_type_to_val_nominal(self):
        meta = dom.Type(
            form=dom.Nominal(
                ref=dom.Ref.from_str("std.Text"),
                params=dom.Const(meta=dom.Type(form=dom.Struct(fields=dom.Tuple.EMPTY)), data=()),
                schema=None,
            )
        )
        value = meta.to_val()
        qualifiers_data, form_data = value.data[1]
        self.assertEqual(qualifiers_data, ())
        tag_data, payload = form_data
        self.assertEqual(tag_data, ("std", "Type", "Nominal"))
        ref_data, params_data, schema_data = payload
        self.assertEqual(ref_data, ("std", "Text"))
        self.assertEqual(params_data, ())
        self.assertIsNone(schema_data)

    def test_type_to_val_struct(self):
        fields = dom.Tuple.new(dom.Type.Var("T"))
        meta = dom.Type(form=dom.Struct(fields=fields))
        value = meta.to_val()
        tag_data, payload = value.data[1][1]
        self.assertEqual(tag_data, ("std", "Type", "Struct"))
        index_data, fields_data = payload
        self.assertEqual(index_data, (None,))
        field_tag, field_payload = fields_data[0]
        self.assertEqual(field_tag, "type")
        field_qualifiers, field_form = field_payload
        self.assertEqual(field_qualifiers, ())
        field_form_tag, field_form_payload = field_form
        self.assertEqual(field_form_tag, ("std", "Type", "Var"))
        self.assertEqual(field_form_payload, "T")

    def test_type_to_val_function_union(self):
        t_nat = dom.Type(form=dom.Nominal(ref=dom.Ref.from_str("std.Natural"), params=dom.Const(meta=dom.Type(form=dom.Struct(fields=dom.Tuple.EMPTY)), data=()), schema=None))
        t_txt = dom.Type(form=dom.Nominal(ref=dom.Ref.from_str("std.Text"), params=dom.Const(meta=dom.Type(form=dom.Struct(fields=dom.Tuple.EMPTY)), data=()), schema=None))
        fn_meta = dom.Type(form=dom.Function(args=(t_nat,), ret=t_txt))
        fn_val = fn_meta.to_val()
        fn_tag, fn_payload = fn_val.data[1][1]
        self.assertEqual(fn_tag, ("std", "Type", "Function"))
        args_data, ret_data = fn_payload
        self.assertEqual(len(args_data), 1)
        ret_tag, ret_payload = ret_data
        self.assertEqual(ret_tag, "type")
        ret_qualifiers, ret_form = ret_payload
        self.assertEqual(ret_qualifiers, ())
        ret_form_tag, ret_form_payload = ret_form
        self.assertEqual(ret_form_tag, ("std", "Type", "Nominal"))
        self.assertEqual(ret_form_payload[0], ("std", "Text"))

        union_meta = dom.Type(form=dom.Union(members=(t_nat, t_txt)))
        union_val = union_meta.to_val()
        union_tag, union_payload = union_val.data[1][1]
        self.assertEqual(union_tag, ("std", "Type", "Union"))
        self.assertEqual(len(union_payload[0]), 2)
