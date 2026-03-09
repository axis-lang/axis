import unittest
from decimal import Decimal

from axis import dom, syn, val


class _Contrib(dom.ContributionBase):
    """Concrete ContributionBase for testing."""
    pass


class EvalTest(unittest.TestCase):
    def eval(self, source: str, env=None) -> dom.Const:
        evaluator = val.Evaluator.from_env(env or {})
        return evaluator(syn.Expr.from_str(source))

    def test_eval_literal(self):
        result = self.eval("12")
        self.assertEqual(result.data, 12)
        self.assertTrue(isinstance(result.type, dom.NominalType))
        if isinstance(result.type, dom.NominalType):
            self.assertEqual(dom.ref_segments(result.type.spec_ref), ("std", "Decimal"))

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
        self.assertTrue(issubclass(dom.VarSpecType, dom.VarType))
        self.assertTrue(issubclass(dom.VarParamType, dom.VarType))

    def test_nominal_schema_opaque(self):
        meta = dom.NominalType.from_str("std.Text")
        if isinstance(meta, dom.NominalType):
            self.assertTrue(isinstance(meta.spec, dom.Ref))

    def test_nominal_params_with_var_encoding(self):
        param = dom.Const.new_literal(3)
        fields = dom.Struct.new(size=param.type)
        spec = dom.Const(type=dom.StructType(fields=fields), data=(param.data,))
        base = dom.Anchor.from_str("std.Array")
        ref = base.specialize(spec)
        meta = dom.NominalType.from_ref(ref)
        if isinstance(meta, dom.NominalType):
            self.assertTrue(isinstance(meta.spec, dom.Ref))

    def test_new_struct_with_vars(self):
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)
        result = dom.Const.new_struct(K, V)
        self.assertIsInstance(result.type, dom.StructType)
        self.assertEqual(result.data, ("K", "V"))
        self.assertEqual(result.type.fields[0], dom.VarSpecType(contribution=contrib))
        self.assertEqual(result.type.fields[1], dom.VarSpecType(contribution=contrib))

    def test_new_qual_simple(self):
        """Mapping[K] V — single qualifier with spec vars."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)

        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(K)
        )
        result = dom.Const.new_qual(spec_ref=mapping_spec, underlying=V)

        # type side: NominalQualifier with SpecType and VarSpecType
        self.assertIsInstance(result.type, dom.NominalQualifier)
        self.assertIsInstance(result.type.spec_ref, dom.SpecType)
        self.assertEqual(result.type.underlying, dom.VarSpecType(contribution=contrib))

        # data side: (underlying.data, spec_ref.data)
        self.assertEqual(result.data[0], "V")
        self.assertEqual(result.data[1], (("std", "Mapping"), ("K",)))

    def test_new_qual_chained(self):
        """Array[2,2] Mapping[K] V — chained qualifiers."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)
        two = dom.Const.new_literal(2)

        # inner: Mapping[K] V
        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(K)
        )
        inner = dom.Const.new_qual(spec_ref=mapping_spec, underlying=V)

        # outer: Array[2,2] (Mapping[K] V)
        array_spec = dom.Anchor.from_str("std.Array").specialize(
            dom.Const.new_struct(two, two)
        )
        outer = dom.Const.new_qual(spec_ref=array_spec, underlying=inner)

        # type side: nested NominalQualifiers
        self.assertIsInstance(outer.type, dom.NominalQualifier)
        self.assertIsInstance(outer.type.underlying, dom.NominalQualifier)
        self.assertEqual(outer.type.underlying.underlying, dom.VarSpecType(contribution=contrib))

        # data side: (inner.data, array_spec.data)
        inner_data = outer.data[0]
        array_data = outer.data[1]
        self.assertEqual(inner_data, ("V", (("std", "Mapping"), ("K",))))
        self.assertEqual(array_data, (("std", "Array"), (2, 2)))
