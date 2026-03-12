import unittest
from typing import Generic, TypeVar
from typing import cast

from axis import dom
from protobase import frozendict


class Person(dom.Builtin):
    ANCHOR = "test.Person"

    name: str
    age: int


T = TypeVar("T")


class Box(dom.Builtin, Generic[T]):
    ANCHOR = "test.Box"

    value: T


class Inventory(dom.Builtin, Generic[T]):
    ANCHOR = "test.Inventory"

    owner: str
    items: frozendict[str, T]


class TestDomValueCreation(unittest.TestCase):
    def test_literal_values_render_as_expected(self):
        self.assertEqual(repr(dom.val(42)), "42")
        self.assertEqual(repr(dom.val("hello")), "'hello'")
        self.assertEqual(repr(dom.val(True)), "true")
        self.assertEqual(repr(dom.val(None)), "none")

    def test_type_tokens_render_as_type_values(self):
        self.assertEqual(repr(dom.val(int)), "std.Integer")
        self.assertEqual(repr(dom.val(str)), "std.Text")

    def test_named_struct_from_dict_is_navigable(self):
        value = dom.val({"x": 1, "y": "hi"})

        self.assertEqual(repr(value), "(x=1, y='hi')")
        self.assertEqual(tuple(value.dir()), ("x", "y"))
        self.assertEqual(dom.get(value, "x"), dom.val(1))
        self.assertEqual(dom.get(value, "y"), dom.val("hi"))

    def test_positional_struct_is_navigable_by_index(self):
        value = dom.val(1, "hi")

        self.assertEqual(repr(value), "(1, 'hi')")
        self.assertEqual(dom.get(value, 0), dom.val(1))
        self.assertEqual(dom.get(value, 1), dom.val("hi"))

    def test_builtin_value_renders_through_public_dom_api(self):
        value = dom.val(Person(name="Alice", age=30))

        self.assertEqual(repr(value), "test.Person(name='Alice', age=30)")
        self.assertEqual(tuple(value.dir()), ("name", "age"))
        self.assertEqual(dom.get(value, "name"), dom.val("Alice"))
        self.assertEqual(dom.get(value, "age"), dom.val(30))

    def test_builtin_class_and_specialized_alias_become_type_values(self):
        self.assertEqual(repr(dom.val(Person)), "test.Person")
        self.assertEqual(repr(dom.val(Box[int])), "test.Box[T=std.Integer]")

    def test_collection_annotations_render_as_qualified_types(self):
        self.assertEqual(repr(dom.val(dict[str, int])), "std.Map[K=std.Text] std.Integer")
        self.assertEqual(repr(dom.val(dict[str, str])), "std.Map[K=std.Text] std.Text")
        self.assertEqual(repr(dom.val(list[str])), "std.List std.Text")


class TestDomNavigation(unittest.TestCase):
    def test_type_of_returns_a_type_value(self):
        self.assertEqual(repr(dom.type_of(dom.val(42))), "std.Integer")
        self.assertEqual(repr(dom.type_of(dom.val("hello"))), "std.Text")

    def test_dir_of_opaque_value_is_empty(self):
        self.assertEqual(tuple(dom.val(42).dir()), ())
        self.assertFalse(dom.val(42).has_attrs)
        self.assertEqual(len(dom.val(42)), 0)

    def test_get_on_opaque_value_raises_key_error(self):
        with self.assertRaises(KeyError):
            dom.get(dom.val(42), "missing")

    def test_attrs_expose_struct_children_as_values(self):
        value = dom.val({"x": 1, "y": "hi"})
        attrs = cast(dom.Struct[str | None, dom.Val], value.attrs)

        self.assertIsNotNone(attrs)
        self.assertTrue(value.has_attrs)
        self.assertEqual(len(value), 2)
        self.assertEqual(attrs.index.keys, ("x", "y"))
        self.assertEqual(attrs.values, (dom.val(1), dom.val("hi")))

    def test_get_accepts_default(self):
        value = dom.val({"x": 1})
        missing = value.get("missing", default=dom.val(None))
        self.assertEqual(missing, dom.val(None))

    def test_err_is_a_typed_value(self):
        err = dom.Err()

        self.assertIsInstance(err.type, dom.ErrType)
        self.assertIsNone(err.data)
        self.assertIsNone(dom.dir(err))

        with self.assertRaises(KeyError):
            dom.get(err, "missing")

        err_type = dom.type_of(err)
        self.assertIsInstance(err_type, dom.Const)
        self.assertIsInstance(err_type.data, dom.ErrType)


class TestDomCodec(unittest.TestCase):
    def test_roundtrip_literal_value(self):
        value = cast(dom.Const, dom.val(42))
        self.assertEqual(dom.decode(dom.encode(value)), value)

    def test_roundtrip_type_token_value(self):
        value = cast(dom.Const, dom.val(int))
        self.assertEqual(dom.decode(dom.encode(value)), value)

    def test_roundtrip_struct_value(self):
        value = cast(dom.Const, dom.val({"x": 1, "y": "hi"}))
        self.assertEqual(dom.decode(dom.encode(value)), value)

    def test_roundtrip_builtin_value(self):
        value = cast(dom.Const, dom.val(Person(name="Alice", age=30)))
        self.assertEqual(dom.decode(dom.encode(value)), value)

    def test_type_wrap_builds_values_for_the_type(self):
        self.assertEqual(dom.INTEGER_TYPE.wrap(42), dom.val(42))
        err = dom.ErrType().wrap(None)
        self.assertIsInstance(err, dom.Err)
        self.assertIsNone(err.data)

    def test_type_value_wrap_builds_values_for_type_values(self):
        self.assertEqual(dom.val(int).wrap(42), dom.val(42))
        self.assertEqual(
            dom.val(Person).wrap(Person(name="Alice", age=30)),
            dom.val(Person(name="Alice", age=30)),
        )

    def test_type_value_wrap_supports_builtin_qualifiers(self):
        wrapped = dom.val(frozendict[str, str]).wrap(cast(dom.Data, frozendict({"a": "b"})))

        self.assertIsInstance(wrapped, dom.Const)
        self.assertEqual(wrapped.type, dom.val(frozendict[str, str]).data)
        self.assertEqual(wrapped.data, frozendict({"a": "b"}))

    def test_type_value_wrap_decodes_encoded_type_values(self):
        encoded_type_value = dom.encode(cast(dom.Const, dom.val(Person)))

        self.assertNotIsInstance(encoded_type_value.data, dom.Type)
        self.assertEqual(
            encoded_type_value.wrap(Person(name="Alice", age=30)),
            dom.val(Person(name="Alice", age=30)),
        )

    def test_non_type_values_cannot_wrap(self):
        with self.assertRaisesRegex(TypeError, "type value"):
            dom.val(42).wrap(1)

    def test_qualifier_meta_tracks_underlying_meta(self):
        self.assertTrue(dom.nominal_qual("test.Meta", underlying=dom.NOMINAL_TYPE).is_meta)
        self.assertFalse(dom.nominal_qual("test.Value", underlying=dom.TEXT_TYPE).is_meta)

    def test_roundtrip_err_value(self):
        value = dom.Err()
        self.assertEqual(dom.decode(dom.encode(value)), value)

    def test_decode_unknown_nominal_fails_strictly(self):
        unknown = dom.Const(type=dom.nominal_type("test.MissingBuiltin"), data=(1,))

        with self.assertRaisesRegex(ValueError, "no registered builtin class"):
            dom.decode(unknown)

    def test_generic_builtin_instance_without_runtime_args_fails(self):
        with self.assertRaisesRegex(ValueError, "cannot infer type arguments"):
            dom.val(Box(value=1))


class TestDomCurrentGaps(unittest.TestCase):
    def test_qualified_values_are_explicitly_not_implemented_yet(self):
        qualified_type = dom.nominal_qual("test.Maybe", underlying=dom.TEXT_TYPE)
        qualified_value = dom.Const(type=qualified_type, data="hello")

        with self.assertRaises(NotImplementedError):
            dom.encode(qualified_value)

        with self.assertRaises(NotImplementedError):
            dom.get(qualified_value, "value")


class TestDomQualifierSemantics(unittest.TestCase):
    def test_introspector_projects_through_qualified_nominal_types(self):
        qualified = cast(dom.Type, dom.val(frozendict[str, Inventory[int]]).data)
        projected_owner = dom.DEFAULT_INTROSPECTOR.project(qualified, "owner")
        projected_items = dom.DEFAULT_INTROSPECTOR.project(qualified, "items")

        self.assertEqual(repr(dom.val(projected_owner)), "std.Map[K=std.Text] std.Text")
        self.assertEqual(
            repr(dom.val(projected_items)),
            "std.Map[K=std.Text] std.Map[K=std.Text] std.Integer",
        )

    def test_qualified_type_dir_lifts_underlying_fields(self):
        qualified = cast(dom.Type, dom.val(frozendict[str, Inventory[int]]).data)
        fields = qualified._dir()

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields.index.keys, ("owner", "items"))
        self.assertEqual(repr(dom.val(fields.get("owner"))), "std.Map[K=std.Text] std.Text")
        self.assertEqual(
            repr(dom.val(fields.get("items"))),
            "std.Map[K=std.Text] std.Map[K=std.Text] std.Integer",
        )

    def test_introspector_lift_preserves_nominal_qualifier_context(self):
        qualifier = dom.nominal_qual("std.Map", dom.struct(K=cast(dom.Const, dom.val(dom.TEXT_TYPE))), underlying=dom.INTEGER_TYPE)
        lifted = dom.DEFAULT_INTROSPECTOR.lift(qualifier, dom.TEXT_TYPE)

        self.assertEqual(repr(dom.val(lifted)), "std.Map[K=std.Text] std.Text")

    def test_introspector_combine_remains_semantic_layer_extension_point(self):
        with self.assertRaises(NotImplementedError):
            dom.DEFAULT_INTROSPECTOR.combine(dom.INTEGER_TYPE, dom.INTEGER_TYPE, op="+")


class TestDomReferences(unittest.TestCase):
    def test_spec_args_expose_specialization_as_values(self):
        spec = dom.spec_ref("std.Map", dom.struct(K=cast(dom.Const, dom.val(dom.TEXT_TYPE))))
        args = cast(dom.Struct[str | None, dom.Val], spec.args)

        self.assertIsNotNone(args)
        self.assertEqual(args.index.keys, ("K",))
        self.assertEqual(args.values, (dom.val(dom.TEXT_TYPE),))
