from __future__ import annotations

import unittest
from typing import Any, cast

from protobase import frozendict

from protomorph import Builtin, ELLIPSIS, Err, Map, SELF, Id, Index, LeafCarrier, Option, OptionUnwrapError, Qual, Result, ResultUnwrapError, Set, Spec, Tuple, UniformType, UnionType, VaryingType, WILDCARD, subst_marks, subst_self, subst_where, var, val


INT = cast(Spec, val(int).fetch())
STR = cast(Spec, val(str).fetch())
ANY = Spec.of("std.types.Any")


class TestLeafCarrier(unittest.TestCase):
    def test_len_zero(self):
        carrier = LeafCarrier(ANY, 42)

        self.assertEqual(len(carrier), 0)
        self.assertEqual(list(carrier), [])

    def test_fetch(self):
        self.assertEqual(LeafCarrier(ANY, "hello").fetch(), "hello")


class TestTuple(unittest.TestCase):
    def test_uniform_iteration(self):
        carrier = Tuple(UniformType(INT), (10, 20, 30))
        self.assertEqual([child.fetch() for child in carrier], [10, 20, 30])

    def test_varying_iteration(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (42, "hello"))
        self.assertEqual([child.fetch() for child in carrier], [42, "hello"])

    def test_reconstruct(self):
        carrier = Tuple(UniformType(INT), (10, 20))
        children = (LeafCarrier(INT, 100), LeafCarrier(INT, 200))
        self.assertEqual(carrier.reconstruct(children).fetch(), (100, 200))

    def test_invalid_descriptor_length_raises(self):
        with self.assertRaises(AssertionError):
            Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, 2, 3))


class TestIndexCarrier(unittest.TestCase):
    def test_sparse(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertTrue(index.is_sparse)

    def test_offset_of(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(index.offset_of(Id("z")), 2)

    def test_offsets(self):
        index = Index.of(Id("x"), None, Id("z"))
        self.assertEqual(index.offsets, {Id("x"): 0, Id("z"): 2})


class TestNativeObjectCarrier(unittest.TestCase):
    def test_attr(self):
        class Pt(Builtin):
            SPEC_NAME = "test.carrier.Point"
            x: int
            y: int

        carrier = val(Pt(3, 4))
        self.assertEqual(carrier.attr(Id("x")).fetch(), 3)
        self.assertEqual(carrier.attr(Id("y")).fetch(), 4)

    def test_reconstruct(self):
        class Pt(Builtin):
            SPEC_NAME = "test.carrier.Point2"
            x: int
            y: int

        carrier = val(Pt(1, 2))
        rebuilt = carrier.reconstruct((LeafCarrier(ANY, 10), LeafCarrier(ANY, 20)))
        self.assertEqual(rebuilt.fetch(), Pt(10, 20))


class TestMakeValueRules(unittest.TestCase):
    def test_placeholder_data_becomes_leaf(self):
        ph = var("T")
        child = INT.make(ph)
        self.assertIsInstance(child, LeafCarrier)
        self.assertIs(child.fetch(), ph)

    def test_type_data_becomes_type_carrier(self):
        child = ANY.make(INT)
        self.assertEqual(child.fetch(), INT)

    def test_nested_carrier_is_preserved(self):
        nested = LeafCarrier(INT, 7)
        child = ANY.make(nested)
        self.assertIs(child, nested)


class TestCarrierSubstitution(unittest.TestCase):
    def test_subst_where_replaces_matching_leaves(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(ANY, ANY)), (1, 2))

        updated = subst_where(
            carrier,
            lambda leaf: leaf.fetch() == 2,
            lambda leaf: LeafCarrier(leaf.descriptor, 20),
        )

        self.assertEqual(updated.fetch(), (1, 20))

    def test_subst_marks_replaces_it_and_wildcard(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(ANY, ANY)), (SELF, WILDCARD))

        updated = subst_marks(carrier, {SELF: LeafCarrier(INT, 7), WILDCARD: "x"})

        self.assertEqual(updated.fetch(), (7, "x"))

    def test_subst_it_replaces_it_mark(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(ANY, ANY)), (1, SELF))

        updated = subst_self(carrier, LeafCarrier(INT, 9))

        self.assertEqual(updated.fetch(), (1, 9))

    def test_tuple_empty_singleton_and_factory_match(self):
        self.assertIs(Tuple.empty(), Tuple.Empty)
        self.assertEqual(Tuple.Empty.fetch(), ())

    def test_ellipsis_mark_is_exported(self):
        self.assertEqual(type(ELLIPSIS).__name__, "EllipsisMark")

class TestResultCarrier(unittest.TestCase):
    def test_result_make_accepts_plain_success_payload(self):
        result_int = Qual(Result.qualifier(val(STR)), INT)

        carrier = cast(Result, result_int.make(1))

        self.assertTrue(carrier.is_ok)
        self.assertEqual(carrier.value_carrier().fetch(), 1)

    def test_result_err_uses_result_error_type(self):
        result_int = Qual(Result.qualifier(val(STR)), INT)

        carrier = cast(Result, result_int.make(Err("bad")))

        self.assertTrue(carrier.is_err)
        self.assertEqual(carrier.error_carrier().descriptor, STR)

    def test_result_ok_constructor_uses_result_qualifier(self):
        value = LeafCarrier(INT, 1)

        carrier = Result.ok(value)

        self.assertEqual(type(carrier.descriptor).__name__, "Qual")
        self.assertTrue(carrier.is_ok)
        self.assertEqual(carrier.value_carrier().descriptor, INT)

    def test_result_ok_constructor_preserves_qualified_descriptor(self):
        value = cast(Map, Qual.of(INT, Spec.of("std.qualifiers.Map", STR)).make({Id("a"): 1}))

        carrier = Result.ok(value)

        self.assertEqual(carrier.value_carrier().descriptor, value.descriptor)
        self.assertEqual(carrier.descriptor.underlying, INT)
        self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[0].fetch()).anchor, "std.qualifiers.Map")
        self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[-1].fetch()).anchor, "std.qualifiers.Result")

    def test_result_ok_constructor_rejects_non_carrier(self):
        with self.assertRaises(TypeError):
            cast(Any, Result.ok)(1)

    def test_unwrap_returns_ok_carrier(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        self.assertEqual(carrier.unwrap(), carrier.value_carrier())
        self.assertEqual(carrier.unwrap().fetch(), 1)

    def test_unwrap_raises_on_err(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        with self.assertRaises(ResultUnwrapError) as raised:
            carrier.unwrap()

        self.assertEqual(raised.exception.payload, carrier.error_carrier())

    def test_unwrap_err_returns_err_carrier(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        self.assertEqual(carrier.unwrap_err(), carrier.error_carrier())
        self.assertEqual(carrier.unwrap_err().fetch(), "bad")

    def test_expect_uses_custom_message(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        with self.assertRaises(ResultUnwrapError) as raised:
            carrier.expect("boom")

        self.assertEqual(str(raised.exception), "boom: 'bad'")

    def test_expect_err_raises_on_ok(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        with self.assertRaises(ResultUnwrapError) as raised:
            carrier.expect_err("wanted err")

        self.assertEqual(str(raised.exception), "wanted err: 1")

    def test_unwrap_or_returns_default_on_err(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        self.assertEqual(carrier.unwrap_or(LeafCarrier(INT, 7)).fetch(), 7)

    def test_unwrap_or_else_computes_default_from_err(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        self.assertEqual(
            carrier.unwrap_or_else(lambda err: LeafCarrier(INT, len(cast(str, err.fetch())))).fetch(),
            3,
        )

    def test_map_transforms_ok_value(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        mapped = carrier.map(lambda value: LeafCarrier(INT, cast(int, value.fetch()) + 1))

        self.assertTrue(mapped.is_ok)
        self.assertEqual(mapped.unwrap().fetch(), 2)
        self.assertEqual(mapped.value_carrier().descriptor, INT)

    def test_map_preserves_err_value(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        mapped = carrier.map(lambda value: LeafCarrier(INT, cast(int, value.fetch()) + 1))

        self.assertTrue(mapped.is_err)
        self.assertEqual(mapped.unwrap_err().fetch(), "bad")

    def test_map_err_transforms_err_value(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        mapped = carrier.map_err(lambda error: LeafCarrier(INT, len(cast(str, error.fetch()))))

        self.assertTrue(mapped.is_err)
        self.assertEqual(mapped.unwrap_err().fetch(), 3)
        self.assertEqual(mapped.error_carrier().descriptor, INT)

    def test_map_err_preserves_ok_value(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        mapped = carrier.map_err(lambda error: LeafCarrier(INT, len(cast(str, error.fetch()))))

        self.assertTrue(mapped.is_ok)
        self.assertEqual(mapped.unwrap().fetch(), 1)

    def test_and_then_flattens_result(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        chained = carrier.and_then(
            lambda value: Result.ok(LeafCarrier(INT, cast(int, value.fetch()) + 1))
        )

        self.assertTrue(chained.is_ok)
        self.assertEqual(chained.unwrap().fetch(), 2)

    def test_and_then_preserves_err_value(self):
        carrier = Result.err(LeafCarrier(STR, "bad"))

        chained = carrier.and_then(
            lambda value: Result.ok(LeafCarrier(INT, cast(int, value.fetch()) + 1))
        )

        self.assertTrue(chained.is_err)
        self.assertEqual(chained.unwrap_err().fetch(), "bad")

    def test_and_then_requires_result_return(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        with self.assertRaises(TypeError):
            carrier.and_then(lambda value: cast(Any, value.fetch()) + 1)

    def test_manual_result_requires_result_qualified_descriptor(self):
        with self.assertRaises(AssertionError):
            Result(cast(Any, INT), 1)

    def test_manual_result_allows_plain_success_content(self):
        result_int = Qual(Result.qualifier(val(STR)), INT)

        carrier = Result(result_int, 1)

        self.assertTrue(carrier.is_ok)
        self.assertEqual(carrier.value_carrier().fetch(), 1)


class TestOptionCarrier(unittest.TestCase):
    def test_option_some_constructor_uses_optional_qualifier(self):
        value = LeafCarrier(INT, 1)

        carrier = Option.some(value)

        self.assertTrue(carrier.is_some)
        self.assertEqual(carrier.value_carrier().descriptor, INT)
        self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[-1].fetch()).anchor, "std.qualifiers.Optional")

    # def test_option_none_projects_python_annotation(self): OLD FUNCTIONALITY, NEED TO BE DELETED
    #     carrier = Option.none(dict[str, int])

    #     self.assertTrue(carrier.is_none)
    #     #self.assertEqual(carrier.descriptor.underlying, INT)
    #     self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[0].fetch()).anchor, "std.qualifiers.Map")
    #     self.assertEqual(cast(Spec, carrier.descriptor.qualifiers[-1].fetch()).anchor, "std.qualifiers.Optional")

    def test_optional_make_defaults_to_some(self):
        optional_int = Qual.of(INT, Spec.of("std.qualifiers.Optional"))

        carrier = cast(Option, optional_int.make(1))

        self.assertTrue(carrier.is_some)
        self.assertEqual(carrier.unwrap().fetch(), 1)

    def test_optional_make_accepts_some(self):
        optional_int = Qual.of(INT, Spec.of("std.qualifiers.Optional"))

        carrier = cast(Option, optional_int.make(1))

        self.assertTrue(carrier.is_some)
        self.assertEqual(carrier.unwrap().fetch(), 1)

    def test_optional_make_accepts_none(self):
        optional_int = Qual.of(INT, Spec.of("std.qualifiers.Optional"))

        carrier = cast(Option, optional_int.make(None))

        self.assertTrue(carrier.is_none)

    def test_option_unwrap_returns_some_value(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        self.assertEqual(carrier.unwrap().fetch(), 1)

    def test_option_unwrap_raises_on_none(self):
        carrier = Option.none(int)

        with self.assertRaises(OptionUnwrapError):
            carrier.unwrap()

    def test_option_unwrap_or_returns_default(self):
        carrier = Option.none(int)

        self.assertEqual(carrier.unwrap_or(LeafCarrier(INT, 7)).fetch(), 7)

    def test_option_unwrap_or_else_computes_default(self):
        carrier = Option.none(int)

        self.assertEqual(carrier.unwrap_or_else(lambda: LeafCarrier(INT, 7)).fetch(), 7)

    def test_option_expect_raises_on_none(self):
        carrier = Option.none(int)

        with self.assertRaises(OptionUnwrapError) as raised:
            carrier.expect("boom")

        self.assertEqual(str(raised.exception), "boom")

    def test_option_map_transforms_some_value(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        mapped = carrier.map(lambda value: LeafCarrier(INT, cast(int, value.fetch()) + 1))

        self.assertTrue(mapped.is_some)
        self.assertEqual(mapped.unwrap().fetch(), 2)

    def test_option_map_preserves_none(self):
        carrier = Option.none(int)

        mapped = carrier.map(lambda value: LeafCarrier(INT, cast(int, value.fetch()) + 1))

        self.assertTrue(mapped.is_none)

    def test_option_and_then_flattens_option(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        chained = carrier.and_then(
            lambda value: Option.some(LeafCarrier(INT, cast(int, value.fetch()) + 1))
        )

        self.assertTrue(chained.is_some)
        self.assertEqual(chained.unwrap().fetch(), 2)

    def test_option_and_then_requires_option_return(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        with self.assertRaises(TypeError):
            carrier.and_then(lambda value: cast(Any, value.fetch()) + 1)

    def test_option_reconstruct_rebuilds_structured_some(self):
        carrier = Option.some(Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a")))

        rebuilt = cast(
            Option,
            carrier.reconstruct(
                (
                    Option.some(LeafCarrier(INT, 2)),
                    Option.some(LeafCarrier(STR, "b")),
                )
            ),
        )

        self.assertTrue(rebuilt.is_some)
        self.assertEqual(rebuilt.unwrap().fetch(), (2, "b"))

    def test_option_reconstruct_rebuilds_structured_none(self):
        carrier = Option.some(Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a")))

        rebuilt = cast(
            Option,
            carrier.reconstruct(
                (
                    Option.none(),
                    Option.none(),
                )
            ),
        )

        self.assertTrue(rebuilt.is_none)

    def test_option_reconstruct_rejects_mixed_some_and_none(self):
        carrier = Option.some(Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a")))

        with self.assertRaises(TypeError):
            carrier.reconstruct(
                (
                    Option.some(LeafCarrier(INT, 2)),
                    Option.none(),
                )
            )

    def test_option_ok_or_converts_some_to_result_ok(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        result = carrier.ok_or(LeafCarrier(STR, "bad"))

        self.assertTrue(result.is_ok)
        self.assertEqual(result.unwrap().fetch(), 1)

    def test_option_ok_or_converts_none_to_result_err(self):
        carrier = Option.none(int)

        result = carrier.ok_or(LeafCarrier(STR, "bad"))

        self.assertTrue(result.is_err)
        self.assertEqual(result.unwrap_err().fetch(), "bad")


class TestQualHelpers(unittest.TestCase):
    def test_constructor_stores_qualifier_then_qualified(self):
        qualifier = Spec.of("std.qualifiers.Optional")
        qual = Qual(qualifier, INT)

        self.assertIs(qual.qualifier, qualifier)
        self.assertIs(qual.qualified, INT)

    def test_last_qualifier_returns_last_item(self):
        qual = Qual.of(INT, Spec.of("std.qualifiers.List"), Spec.of("std.qualifiers.Optional"))

        self.assertEqual(cast(Spec, qual.qualifier).anchor, "std.qualifiers.Optional")

    def test_unwrap_returns_underlying_when_single_qualifier(self):
        qual = Qual.of(INT, Spec.of("std.qualifiers.Optional"))

        self.assertEqual(qual.qualified, INT)

    def test_unwrap_returns_nested_qual_when_multiple_qualifiers(self):
        qual = Qual.of(INT, Spec.of("std.qualifiers.List"), Spec.of("std.qualifiers.Optional"))

        self.assertEqual(qual.qualified, Qual.of(INT, Spec.of("std.qualifiers.List")))


class TestTypeSchema(unittest.TestCase):
    def test_leaf_types_have_no_schema(self):
        self.assertTrue(ANY.is_leaf)
        self.assertIsNone(ANY.schema)

    def test_leaf_type_len_and_iter_raise(self):
        with self.assertRaises(TypeError):
            len(ANY)

        with self.assertRaises(TypeError):
            tuple(ANY)

    def test_spec_schema_returns_known_schema(self):
        spec = Spec.of("std.types.Result.Err", INT)
        schema = spec.schema

        assert schema is not None
        self.assertEqual(schema.attr(Id("payload")).fetch(), INT)

    def test_qual_schema_projects_one_level(self):
        qual = Qual.of(Spec.of("std.types.Result.Err", INT), Spec.of("std.qualifiers.Optional"))
        schema = qual.schema

        assert schema is not None
        self.assertEqual(
            schema.attr(Id("payload")).fetch(),
            Qual.of(INT, Spec.of("std.qualifiers.Optional")),
        )

    def test_uniform_schema_none_for_leaf_element(self):
        self.assertIsNone(UniformType(INT).schema)

    def test_uniform_schema_projects_one_level(self):
        schema = UniformType(cast(VaryingType, VaryingType.of(INT, STR))).schema

        assert schema is not None
        self.assertEqual(schema[0].fetch(), UniformType(INT))
        self.assertEqual(schema[1].fetch(), UniformType(STR))

    def test_union_schema_is_none(self):
        union = cast(UnionType, UnionType.of(INT, STR))

        self.assertTrue(union.is_leaf)
        self.assertIsNone(union.schema)


class TestProjectedCarrierTraversal(unittest.TestCase):
    def test_option_logical_children_project_payload(self):
        carrier = Option.some(LeafCarrier(INT, 1))

        self.assertEqual(len(carrier), 0)

    def test_result_logical_children_project_payload(self):
        carrier = Result.ok(LeafCarrier(INT, 1))

        self.assertEqual(len(carrier), 0)

    def test_option_logical_children_project_structured_payload(self):
        carrier = Option.some(Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a")))

        self.assertEqual([child.fetch() for child in carrier], [1, "a"])
        self.assertEqual(
            [child.descriptor for child in carrier],
            [
                Qual.of(INT, Spec.of("std.qualifiers.Optional")),
                Qual.of(STR, Spec.of("std.qualifiers.Optional")),
            ],
        )

    def test_result_logical_children_project_structured_payload(self):
        carrier = Result.ok(Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a")))

        projected = [cast(Result, child) for child in carrier]

        self.assertTrue(all(isinstance(child, Result) for child in projected))
        self.assertTrue(all(child.is_ok for child in projected))
        self.assertEqual([child.unwrap().fetch() for child in projected], [1, "a"])


class TestContainerCarriers(unittest.TestCase):
    def test_map_make_and_iterate_values(self):
        map_type = Qual.of(INT, Spec.of("std.qualifiers.Map", STR))

        carrier = cast(Map, map_type.make({Id("a"): 1, Id("b"): 2}))

        self.assertEqual({child.fetch() for child in carrier.values()}, {1, 2})

    def test_set_iterates_payload_content(self):
        set_type = Qual.of(INT, Spec.of("std.qualifiers.Set"))

        carrier = cast(Set, set_type.make({1, 2, 3}))

        self.assertEqual([child.fetch() for child in carrier.values()], [1, 2, 3])

    def test_set_values_are_deterministic(self):
        set_type = Qual.of(INT, Spec.of("std.qualifiers.Set"))
        left = cast(Set, set_type.make({3, 1, 2}))
        right = cast(Set, set_type.make({2, 3, 1}))

        self.assertEqual(
            [child.fetch() for child in left.values()],
            [child.fetch() for child in right.values()],
        )

    def test_map_logical_children_are_not_implemented(self):
        carrier = cast(Map, Qual.of(INT, Spec.of("std.qualifiers.Map", STR)).make({Id("a"): 1}))

        with self.assertRaises(NotImplementedError):
            _ = carrier.children

    def test_set_logical_children_are_not_implemented(self):
        carrier = cast(Set, Qual.of(INT, Spec.of("std.qualifiers.Set")).make({1}))

        with self.assertRaises(NotImplementedError):
            _ = carrier.children


class TestTupleMap(unittest.TestCase):
    def test_map_updates_child_descriptors(self):
        carrier = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "hello"))

        mapped = carrier.map(lambda child: LeafCarrier(ANY, str(child.fetch())))

        self.assertEqual(mapped.fetch(), ("1", "hello"))
        self.assertEqual(mapped.descriptor, VaryingType.of(ANY, ANY))

    def test_map_degrades_uniform_to_varying_when_descriptors_diverge(self):
        carrier = Tuple(UniformType(INT), (1, 2))

        mapped = carrier.map(
            lambda child: LeafCarrier(INT if child.fetch() == 1 else STR, child.fetch())
        )

        self.assertEqual(mapped.fetch(), (1, 2))
        self.assertEqual(mapped.descriptor, VaryingType.of(INT, STR))


class TestTypeProperty(unittest.TestCase):
    def test_type_carrier(self):
        carrier = LeafCarrier(INT, 42)
        self.assertEqual(carrier.type.fetch(), INT)


if __name__ == "__main__":
    unittest.main()
