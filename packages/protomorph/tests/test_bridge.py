from __future__ import annotations

from typing import TypeVar
import unittest
from typing import cast

from protomorph import Builtin, Id, NativeVar, Placeholder, Qual, Spec, UniformType, UnionType, Var, VaryingType, project_type, wrap


INT = wrap(int).fetch()
STR = wrap(str).fetch()
FLOAT = wrap(float).fetch()
BOOL = wrap(bool).fetch()
NONE = wrap(type(None)).fetch()


class TestWrapProjection(unittest.TestCase):
    def test_scalars(self):
        self.assertEqual(wrap(int).fetch(), INT)
        self.assertEqual(wrap(str).fetch(), STR)
        self.assertEqual(wrap(float).fetch(), FLOAT)
        self.assertEqual(wrap(bool).fetch(), BOOL)
        self.assertEqual(wrap(type(None)).fetch(), NONE)

    def test_type_passthrough(self):
        self.assertIs(wrap(INT).fetch(), INT)

    def test_tuple_uniform(self):
        result = cast(UniformType, project_type(tuple[int, ...]))
        self.assertIsInstance(result, UniformType)
        self.assertIs(result.element_type, INT)

    def test_tuple_varying(self):
        result = cast(VaryingType, project_type(tuple[int, str, float]))
        self.assertIsInstance(result, VaryingType)
        self.assertEqual(result.values, (INT, STR, FLOAT))

    def test_union(self):
        result = cast(UnionType, project_type(int | str))
        self.assertIsInstance(result, UnionType)
        self.assertEqual(result.variants, frozenset({INT, STR}))

    def test_union_with_none(self):
        result = cast(UnionType, project_type(int | None))
        self.assertIn(INT, result.variants)
        self.assertIn(NONE, result.variants)

    def test_builtin_class_projects_to_spec(self):
        class Pt(Builtin):
            SPEC_NAME = "test.bridge.Point"
            x: int

        self.assertEqual(project_type(Pt), Spec.of("test.bridge.Point"))

    def test_typevar_projects_to_placeholder(self):
        T = TypeVar("T")
        result = cast(Placeholder, project_type(cast(object, T)))
        self.assertIsInstance(result, Placeholder)
        self.assertIsInstance(result, Var)
        self.assertIsInstance(result, NativeVar)
        self.assertEqual(cast(NativeVar, result).id, "T")

    def test_unknown_annotation_raises(self):
        with self.assertRaises(ValueError):
            project_type(object)


class TestWrap(unittest.TestCase):
    def test_wrap_annotation_returns_type_carrier(self):
        self.assertEqual(wrap(int).fetch(), INT)

    def test_wrap_tuple_annotation_returns_type_carrier(self):
        self.assertIsInstance(wrap(tuple[int, ...]).fetch(), UniformType)

    def test_wrap_tuple_varying_annotation_returns_type_value(self):
        descriptor = cast(VaryingType, cast(object, project_type(tuple[int, str, float])))
        self.assertIsInstance(descriptor, VaryingType)
        self.assertEqual(descriptor.values, (INT, STR, FLOAT))

    def test_wrap_runtime_builtin_returns_native_carrier(self):
        class Pt(Builtin):
            SPEC_NAME = "test.bridge.Point2"
            x: int

        carrier = wrap(Pt(5))
        self.assertEqual(carrier.attr(Id("x")).fetch(), 5)

    def test_wrap_scalar_value_returns_leaf_carrier(self):
        carrier = wrap(7)
        self.assertEqual(carrier.fetch(), 7)
        self.assertIs(carrier.descriptor, INT)

    def test_list_projection_builds_qual(self):
        projected = project_type(list[int])
        self.assertIsInstance(projected, Qual)


if __name__ == "__main__":
    unittest.main()
