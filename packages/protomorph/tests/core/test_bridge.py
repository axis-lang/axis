from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin,
    Placeholder, Spec,
    NativeObjectCarrier,
    UniformType, UnionType, VaryingType, NativeType,
    type_from_annotation, native_type, wrap,
)


INT = wrap(int)
STR = wrap(str)
FLOAT = wrap(float)
BOOL = wrap(bool)
NONE = wrap(type(None))


class TestTypeFromAnnotation(unittest.TestCase):
    def test_int(self):
        self.assertIs(type_from_annotation(int), INT)

    def test_str(self):
        self.assertIs(type_from_annotation(str), STR)

    def test_float(self):
        self.assertIs(type_from_annotation(float), FLOAT)

    def test_bool(self):
        self.assertIs(type_from_annotation(bool), BOOL)

    def test_none_type(self):
        self.assertIs(type_from_annotation(type(None)), NONE)

    def test_type_passthrough(self):
        self.assertIs(type_from_annotation(INT), INT)

    def test_tuple_uniform(self):
        result = type_from_annotation(tuple[int, ...])
        self.assertIsInstance(result, UniformType)
        self.assertIs(result.element_type, INT)

    def test_tuple_varying(self):
        result = type_from_annotation(tuple[int, str, float])
        self.assertIsInstance(result, VaryingType)
        self.assertEqual(result.arity, 3)
        self.assertIs(result.values[0], INT)
        self.assertIs(result.values[1], STR)
        self.assertIs(result.values[2], FLOAT)

    def test_union(self):
        result = type_from_annotation(int | str)
        self.assertIsInstance(result, UnionType)
        self.assertEqual(result.variants, frozenset({INT, STR}))

    def test_union_with_none(self):
        result = type_from_annotation(int | None)
        self.assertIsInstance(result, UnionType)
        self.assertIn(INT, result.variants)
        self.assertIn(NONE, result.variants)

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

    def test_unknown_falls_to_any_spec(self):
        result = type_from_annotation(object)
        self.assertEqual(result, Spec.of("std.types.Any"))


class TestNativeType_(unittest.TestCase):
    def test_empty_class(self):
        class E(Builtin): ...

        nt = native_type(E)
        self.assertEqual(nt.arity, 0)

    def test_generic_typevar(self):
        class G[T](Builtin):
            items: tuple[T, ...]

        gt = native_type(G)
        ft = gt.item_at(0).value
        self.assertIsInstance(ft, UniformType)
        self.assertIsInstance(ft.element_type, Placeholder)

    def test_generic_typevar_tuple(self):
        class V[*T](Builtin):
            items: tuple[int, *T, float]

        vt = native_type(V)
        ft = vt.item_at(0).value
        self.assertIsInstance(ft, VaryingType)
        self.assertIs(ft.values[0], INT)
        self.assertIsInstance(ft.values[1], Placeholder)
        self.assertEqual(ft.values[1].id, "*T")
        self.assertIs(ft.values[2], FLOAT)


class TestWrap(unittest.TestCase):
    def test_wrap_annotation_returns_descriptor(self):
        self.assertIs(wrap(int), INT)

    def test_wrap_tuple_annotation_returns_uniform_type(self):
        result = wrap(tuple[int, ...])
        self.assertIsInstance(result, UniformType)

    def test_wrap_returns_native_carrier(self):
        class Pt(Builtin):
            x: int

        c = wrap(Pt(5))
        self.assertIsInstance(c, NativeObjectCarrier)
        self.assertEqual(c.fetch(), Pt(5))

    def test_wrap_scalar_value_returns_leaf_carrier(self):
        c = wrap(7)
        self.assertEqual(c.fetch(), 7)
        self.assertIs(c.descriptor, INT)

    def test_make_constructs_carrier(self):
        descriptor = wrap(tuple[int, ...])
        carrier = descriptor.make((1, 2, 3))
        self.assertEqual(carrier.fetch(), (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
