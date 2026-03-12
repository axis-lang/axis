import unittest
from typing import Generic, TypeVar
from typing import cast

from axis import dom


class Person(dom.Builtin):
    ANCHOR = "test.Person"

    name: str
    age: int


T = TypeVar("T")


class Box(dom.Builtin, Generic[T]):
    ANCHOR = "test.Box"

    value: T


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
            dom.dir(qualified_value)

        with self.assertRaises(NotImplementedError):
            dom.get(qualified_value, "value")


class TestDomReferences(unittest.TestCase):
    def test_spec_args_expose_specialization_as_values(self):
        spec = dom.spec_ref("std.Map", dom.struct(K=cast(dom.Const, dom.val(dom.TEXT_TYPE))))
        args = cast(dom.Struct[str | None, dom.Val], spec.args)

        self.assertIsNotNone(args)
        self.assertEqual(args.index.keys, ("K",))
        self.assertEqual(args.values, (dom.val(dom.TEXT_TYPE),))
