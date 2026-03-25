from __future__ import annotations

import unittest
from typing import cast

from pm import Builtin, Id, NativeVar, Placeholder, Qual, Spec, UniformType, UnionType, Var, VaryingType, _project_type, wrap


INT = wrap(int).fetch()
STR = wrap(str).fetch()
FLOAT = wrap(float).fetch()
BOOL = wrap(bool).fetch()
NONE = wrap(type(None)).fetch()


class TestProjectType(unittest.TestCase):
    def test_scalars(self):
        self.assertEqual(_project_type(int), INT)
        self.assertEqual(_project_type(str), STR)
        self.assertEqual(_project_type(float), FLOAT)
        self.assertEqual(_project_type(bool), BOOL)
        self.assertEqual(_project_type(type(None)), NONE)

    def test_type_passthrough(self):
        self.assertIs(_project_type(INT), INT)

    def test_tuple_uniform(self):
        result = cast(UniformType, _project_type(tuple[int, ...]))
        self.assertIsInstance(result, UniformType)
        self.assertIs(result.element_type, INT)

    def test_tuple_varying(self):
        result = cast(VaryingType, _project_type(tuple[int, str, float]))
        self.assertIsInstance(result, VaryingType)
        self.assertEqual(result.values, (INT, STR, FLOAT))

    def test_union(self):
        result = cast(UnionType, _project_type(int | str))
        self.assertIsInstance(result, UnionType)
        self.assertEqual(result.variants, frozenset({INT, STR}))

    def test_union_with_none(self):
        result = cast(UnionType, _project_type(int | None))
        self.assertIn(INT, result.variants)
        self.assertIn(NONE, result.variants)

    def test_builtin_class_projects_to_spec(self):
        class Pt(Builtin):
            SPEC_NAME = "test.bridge.Point"
            x: int

        self.assertEqual(_project_type(Pt), Spec.of("test.bridge.Point"))

    def test_typevar_projects_to_placeholder(self):
        from typing import TypeVar

        T = TypeVar("T")
        result = cast(Placeholder, _project_type(T))
        self.assertIsInstance(result, Placeholder)
        self.assertIsInstance(result, Var)
        self.assertIsInstance(result, NativeVar)
        self.assertEqual(cast(Var, result).id, "T")

    def test_unknown_annotation_raises(self):
        with self.assertRaises(ValueError):
            _project_type(object)

    def test_unknown_wrap_raises(self):
        with self.assertRaises(ValueError):
            wrap(object)


class TestWrap(unittest.TestCase):
    def test_wrap_annotation_returns_type_carrier(self):
        self.assertEqual(wrap(int).fetch(), INT)

    def test_wrap_tuple_annotation_returns_type_carrier(self):
        self.assertIsInstance(wrap(tuple[int, ...]).fetch(), UniformType)

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
        projected = _project_type(list[int])
        self.assertIsInstance(projected, Qual)


if __name__ == "__main__":
    unittest.main()
