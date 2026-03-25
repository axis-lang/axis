from __future__ import annotations

import unittest
from typing import cast

from pm import (
    Builtin, Id, Index,
    Placeholder, placeholder,
    LeafCarrier, TupleCarrier, NativeObjectCarrier,
    UniformType, UnionType, VaryingType, NativeType, Spec,
    native_type, wrap,
)



INT = wrap(int)
STR = wrap(str)
FLOAT = wrap(float)
BOOL = wrap(bool)
NONE = wrap(type(None))


class TestAtomicSpecs(unittest.TestCase):
    def test_int_is_spec(self):
        self.assertEqual(INT.arity, 0)
        self.assertEqual(INT.metatype(), Spec.of("std.metas.Specialization"))

    def test_make_leaf_carrier(self):
        c = INT.make(42)
        self.assertIsInstance(c, LeafCarrier)
        self.assertEqual(c.fetch(), 42)


class TestUniformType(unittest.TestCase):
    def test_arity_none(self):
        ut = UniformType(INT, Index.Empty)
        self.assertIsNone(ut.arity)

    def test_item_at(self):
        ut = UniformType(STR, Index.Empty)
        f = ut.item_at(5)
        self.assertEqual(f.offset, 5)
        self.assertIsNone(f.key)
        self.assertIs(f.value, STR)

    def test_item_raises(self):
        ut = UniformType(INT, Index.Empty)
        with self.assertRaises(KeyError):
            ut.item(Id("x"))

    def test_make(self):
        ut = UniformType(INT, Index.Empty)
        c = ut.make((1, 2))
        self.assertIsInstance(c, TupleCarrier)


class TestUnionType(unittest.TestCase):
    def test_of_single_returns_type(self):
        result = UnionType.of(INT)
        self.assertIs(result, INT)

    def test_of_multiple(self):
        u = UnionType.of(INT, STR)
        self.assertIsInstance(u, UnionType)
        self.assertEqual(u.variants, frozenset({INT, STR}))

    def test_of_flattens(self):
        inner = UnionType.of(INT, STR)
        outer = UnionType.of(inner, FLOAT)
        self.assertIsInstance(outer, UnionType)
        self.assertEqual(outer.variants, frozenset({INT, STR, FLOAT}))

    def test_carrier_is_leaf(self):
        u = UnionType.of(INT, STR)
        c = u.make(42)
        self.assertIsInstance(c, LeafCarrier)


class TestVaryingType(unittest.TestCase):
    def test_make_positional(self):
        vt = cast(VaryingType, VaryingType.of(INT, STR, FLOAT))
        self.assertEqual(vt.arity, 3)
        self.assertEqual(vt.values, (INT, STR, FLOAT))

    def test_make_keyword(self):
        vt = cast(VaryingType, VaryingType.of(x=INT, y=STR))
        self.assertEqual(vt.arity, 2)
        f = vt.item(Id("x"))
        self.assertIs(f.value, INT)

    def test_make_mixed(self):
        vt = cast(VaryingType, VaryingType.of(INT, z=STR))
        self.assertEqual(vt.arity, 2)
        self.assertIs(vt.item_at(0).value, INT)
        self.assertIs(vt.item(Id("z")).value, STR)

    def test_carrier(self):
        vt = VaryingType.of(INT)
        c = vt.make((42,))
        self.assertIsInstance(c, TupleCarrier)


class TestNativeType(unittest.TestCase):
    def test_reflects_fields(self):
        class Pt(Builtin):
            x: int
            y: str

        nt = native_type(Pt)
        self.assertEqual(nt.arity, 2)
        self.assertEqual(nt.item_at(0).key, Id("x"))
        self.assertIs(nt.item_at(0).value, INT)
        self.assertEqual(nt.item_at(1).key, Id("y"))
        self.assertIs(nt.item_at(1).value, STR)

    def test_field_by_name(self):
        class Pt(Builtin):
            x: int

        nt = native_type(Pt)
        f = nt.item(Id("x"))
        self.assertIs(f.value, INT)

    def test_make(self):
        class Pt(Builtin):
            x: int

        nt = native_type(Pt)
        c = nt.make(Pt(1))
        self.assertIsInstance(c, NativeObjectCarrier)

    def test_generic_has_placeholders(self):
        class G[T](Builtin):
            value: tuple[T, ...]

        gt = native_type(G)
        ft = gt.item_at(0).value
        self.assertIsInstance(ft, UniformType)
        self.assertIsInstance(ft.element_type, Placeholder)
        self.assertEqual(ft.element_type.id, "T")

    def test_specialize_simple(self):
        class G[T](Builtin):
            value: tuple[T, ...]

        gt = native_type(G)
        g_int = gt.specialize({placeholder("T"): INT})
        ft = g_int.item_at(0).value
        self.assertIsInstance(ft, UniformType)
        self.assertIs(ft.element_type, INT)

    def test_specialize_spread(self):
        class S[*T](Builtin):
            elements: tuple[int, *T, float]

        st = native_type(S)
        concrete = st.specialize({
            placeholder("*T"): cast(VaryingType, VaryingType.of(STR, BOOL)),
        })
        ft = concrete.item_at(0).value
        self.assertIsInstance(ft, VaryingType)
        self.assertEqual(ft.arity, 4)
        self.assertIs(ft.values[0], INT)
        self.assertIs(ft.values[1], STR)
        self.assertIs(ft.values[2], BOOL)
        self.assertIs(ft.values[3], FLOAT)

    def test_no_fields(self):
        class Empty(Builtin): ...

        nt = native_type(Empty)
        self.assertEqual(nt.arity, 0)


if __name__ == "__main__":
    unittest.main()
