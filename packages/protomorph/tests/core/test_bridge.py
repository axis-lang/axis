from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, Id, OMEGA,
    Placeholder, placeholder,
    NativeObjectCarrier,
    ScalarType, UniformType, UnionType, VaryingType, NativeType,
    INT_TYPE, STR_TYPE, FLOAT_TYPE, BOOL_TYPE, NONE_TYPE,
    type_from_annotation, native_type, wrap,
)


class TestTypeFromAnnotation(unittest.TestCase):

    def test_int(self):
        self.assertIs(type_from_annotation(int), INT_TYPE)

    def test_str(self):
        self.assertIs(type_from_annotation(str), STR_TYPE)

    def test_float(self):
        self.assertIs(type_from_annotation(float), FLOAT_TYPE)

    def test_bool(self):
        self.assertIs(type_from_annotation(bool), BOOL_TYPE)

    def test_none_type(self):
        self.assertIs(type_from_annotation(type(None)), NONE_TYPE)

    def test_type_passthrough(self):
        """If annotation is already a Type, return it."""
        self.assertIs(type_from_annotation(INT_TYPE), INT_TYPE)

    def test_tuple_uniform(self):
        result = type_from_annotation(tuple[int, ...])
        self.assertIsInstance(result, UniformType)
        self.assertIs(result.element_type, INT_TYPE)

    def test_tuple_varying(self):
        result = type_from_annotation(tuple[int, str, float])
        self.assertIsInstance(result, VaryingType)
        self.assertEqual(result.arity, 3)
        self.assertIs(result.values[0], INT_TYPE)
        self.assertIs(result.values[1], STR_TYPE)
        self.assertIs(result.values[2], FLOAT_TYPE)

    def test_union(self):
        result = type_from_annotation(int | str)
        self.assertIsInstance(result, UnionType)
        self.assertEqual(result.variants, frozenset({INT_TYPE, STR_TYPE}))

    def test_union_with_none(self):
        result = type_from_annotation(int | None)
        self.assertIsInstance(result, UnionType)
        self.assertIn(INT_TYPE, result.variants)
        self.assertIn(NONE_TYPE, result.variants)

    def test_builtin_class(self):
        class Pt(Builtin):
            x: int

        result = type_from_annotation(Pt)
        self.assertIsInstance(result, NativeType)
        self.assertIs(result.builtin_cls, Pt)

    def test_typevar(self):
        from typing import TypeVar
        T = TypeVar("T")
        result = type_from_annotation(T)
        self.assertIsInstance(result, Placeholder)
        self.assertEqual(result.id, "T")

    def test_typevar_with_template(self):
        from typing import TypeVar
        T = TypeVar("T")

        class G(Builtin):
            x: int

        template = native_type(G)
        result = type_from_annotation(T, template=template)
        self.assertIsInstance(result, Placeholder)
        self.assertIs(result.context, template)

    def test_unknown_falls_to_omega(self):
        result = type_from_annotation(object)
        self.assertIs(result, OMEGA)


class TestNativeType_(unittest.TestCase):

    def test_empty_class(self):
        class E(Builtin): ...
        nt = native_type(E)
        self.assertEqual(nt.arity, 0)

    def test_generic_typevar(self):
        class G[T](Builtin):
            items: tuple[T, ...]

        gt = native_type(G)
        ft = gt.field_at(0).type
        self.assertIsInstance(ft, UniformType)
        self.assertIsInstance(ft.element_type, Placeholder)

    def test_generic_typevar_tuple(self):
        class V[*T](Builtin):
            items: tuple[int, *T, float]

        vt = native_type(V)
        ft = vt.field_at(0).type
        self.assertIsInstance(ft, VaryingType)
        # Should contain int, *T placeholder, float
        self.assertIs(ft.values[0], INT_TYPE)
        self.assertIsInstance(ft.values[1], Placeholder)
        self.assertEqual(ft.values[1].id, "*T")
        self.assertIs(ft.values[2], FLOAT_TYPE)


class TestWrap(unittest.TestCase):

    def test_wrap_returns_native_carrier(self):
        class Pt(Builtin):
            x: int

        c = wrap(Pt(5))
        self.assertIsInstance(c, NativeObjectCarrier)
        self.assertEqual(c.fetch(), Pt(5))

    def test_wrap_traversal(self):
        class Pt(Builtin):
            x: int
            y: str

        c = wrap(Pt(1, "a"))
        leaves = list(c.deep_iter())
        values = {l.fetch() for l in leaves}
        self.assertIn(1, values)
        self.assertIn("a", values)


if __name__ == "__main__":
    unittest.main()
