from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, Id, OMEGA,
    Placeholder, placeholder, Field,
    LeafCarrier, TupleCarrier, NativeObjectCarrier,
    ScalarType, UniformType, UnionType, VaryingType, NativeType,
    INT_TYPE, STR_TYPE, FLOAT_TYPE, BOOL_TYPE, NONE_TYPE,
    native_type, wrap,
)


class TestScalarType(unittest.TestCase):

    def test_arity_zero(self):
        self.assertEqual(INT_TYPE.arity, 0)

    def test_metatype_omega(self):
        self.assertIs(INT_TYPE.metatype(), OMEGA)

    def test_carrier_is_leaf(self):
        c = INT_TYPE.carrier(42)
        self.assertIsInstance(c, LeafCarrier)
        self.assertEqual(c.fetch(), 42)

    def test_consing(self):
        self.assertIs(ScalarType(int), INT_TYPE)

    def test_constants(self):
        self.assertEqual(INT_TYPE.python_type, int)
        self.assertEqual(STR_TYPE.python_type, str)
        self.assertEqual(FLOAT_TYPE.python_type, float)
        self.assertEqual(BOOL_TYPE.python_type, bool)
        self.assertEqual(NONE_TYPE.python_type, type(None))


class TestUniformType(unittest.TestCase):

    def test_arity_none(self):
        ut = UniformType(INT_TYPE)
        self.assertIsNone(ut.arity)

    def test_field_at(self):
        ut = UniformType(STR_TYPE)
        f = ut.field_at(5)
        self.assertEqual(f.offset, 5)
        self.assertIsNone(f.key)
        self.assertIs(f.type, STR_TYPE)

    def test_field_raises(self):
        ut = UniformType(INT_TYPE)
        with self.assertRaises(KeyError):
            ut.field(Id("x"))

    def test_carrier(self):
        ut = UniformType(INT_TYPE)
        c = ut.carrier((1, 2))
        self.assertIsInstance(c, TupleCarrier)

    def test_consing(self):
        self.assertIs(UniformType(INT_TYPE), UniformType(INT_TYPE))


class TestUnionType(unittest.TestCase):

    def test_of_single_returns_type(self):
        result = UnionType.of(INT_TYPE)
        self.assertIs(result, INT_TYPE)

    def test_of_multiple(self):
        u = UnionType.of(INT_TYPE, STR_TYPE)
        self.assertIsInstance(u, UnionType)
        self.assertEqual(u.variants, frozenset({INT_TYPE, STR_TYPE}))

    def test_of_flattens(self):
        inner = UnionType.of(INT_TYPE, STR_TYPE)
        outer = UnionType.of(inner, FLOAT_TYPE)
        self.assertIsInstance(outer, UnionType)
        self.assertEqual(outer.variants, frozenset({INT_TYPE, STR_TYPE, FLOAT_TYPE}))

    def test_arity_zero(self):
        u = UnionType.of(INT_TYPE, STR_TYPE)
        self.assertEqual(u.arity, 0)

    def test_carrier_is_leaf(self):
        u = UnionType.of(INT_TYPE, STR_TYPE)
        c = u.carrier(42)
        self.assertIsInstance(c, LeafCarrier)


class TestVaryingType(unittest.TestCase):

    def test_make_positional(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE, FLOAT_TYPE)
        self.assertEqual(vt.arity, 3)
        self.assertEqual(vt.values, (INT_TYPE, STR_TYPE, FLOAT_TYPE))

    def test_make_keyword(self):
        vt = VaryingType.make(x=INT_TYPE, y=STR_TYPE)
        self.assertEqual(vt.arity, 2)
        f = vt.field(Id("x"))
        self.assertIs(f.type, INT_TYPE)

    def test_make_mixed(self):
        vt = VaryingType.make(INT_TYPE, z=STR_TYPE)
        self.assertEqual(vt.arity, 2)
        self.assertIs(vt.field_at(0).type, INT_TYPE)
        self.assertIs(vt.field(Id("z")).type, STR_TYPE)

    def test_field_at(self):
        vt = VaryingType.make(INT_TYPE, STR_TYPE)
        f = vt.field_at(1)
        self.assertEqual(f.offset, 1)
        self.assertIs(f.type, STR_TYPE)

    def test_is_tuple(self):
        """VaryingType IS a Tuple[Id, Type]."""
        from protomorph.core import Tuple
        vt = VaryingType.make(INT_TYPE)
        self.assertIsInstance(vt, Tuple)

    def test_carrier(self):
        vt = VaryingType.make(INT_TYPE)
        c = vt.carrier((42,))
        self.assertIsInstance(c, TupleCarrier)

    def test_consing(self):
        a = VaryingType.make(INT_TYPE, STR_TYPE)
        b = VaryingType.make(INT_TYPE, STR_TYPE)
        self.assertIs(a, b)


class TestNativeType(unittest.TestCase):

    def test_reflects_fields(self):
        class Pt(Builtin):
            x: int
            y: str

        nt = native_type(Pt)
        self.assertEqual(nt.arity, 2)
        self.assertEqual(nt.field_at(0).key, Id("x"))
        self.assertIs(nt.field_at(0).type, INT_TYPE)
        self.assertEqual(nt.field_at(1).key, Id("y"))
        self.assertIs(nt.field_at(1).type, STR_TYPE)

    def test_field_by_name(self):
        class Pt(Builtin):
            x: int

        nt = native_type(Pt)
        f = nt.field(Id("x"))
        self.assertIs(f.type, INT_TYPE)

    def test_carrier(self):
        class Pt(Builtin):
            x: int

        nt = native_type(Pt)
        c = nt.carrier(Pt(1))
        self.assertIsInstance(c, NativeObjectCarrier)

    def test_generic_has_placeholders(self):
        class G[T](Builtin):
            value: tuple[T, ...]

        gt = native_type(G)
        ft = gt.field_at(0).type
        self.assertIsInstance(ft, UniformType)
        self.assertIsInstance(ft.element_type, Placeholder)
        self.assertEqual(ft.element_type.id, "T")

    def test_specialize_simple(self):
        class G[T](Builtin):
            value: tuple[T, ...]

        gt = native_type(G)
        g_int = gt.specialize({placeholder("T"): INT_TYPE})
        ft = g_int.field_at(0).type
        self.assertIsInstance(ft, UniformType)
        self.assertIs(ft.element_type, INT_TYPE)

    def test_specialize_spread(self):
        class S[*T](Builtin):
            elements: tuple[int, *T, float]

        st = native_type(S)
        concrete = st.specialize({
            placeholder("*T"): VaryingType.make(STR_TYPE, BOOL_TYPE),
        })
        ft = concrete.field_at(0).type
        self.assertIsInstance(ft, VaryingType)
        self.assertEqual(ft.arity, 4)
        self.assertIs(ft.values[0], INT_TYPE)
        self.assertIs(ft.values[1], STR_TYPE)
        self.assertIs(ft.values[2], BOOL_TYPE)
        self.assertIs(ft.values[3], FLOAT_TYPE)

    def test_no_fields(self):
        class Empty(Builtin): ...

        nt = native_type(Empty)
        self.assertEqual(nt.arity, 0)


if __name__ == "__main__":
    unittest.main()
