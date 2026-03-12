"""Focused DOM infrastructure tests.

Public end-to-end behavior lives in `tests/test_dom_e2e.py`.
This module keeps a smaller set of tests for lower-level invariants that are
still useful while redesigning the DOM core.
"""

import unittest
from decimal import Decimal
from typing import Generic, TypeVar, Union

from protobase import _

from axis import dom
from axis.dom.interop import _PY_TO_AX_TRANSFORMS, python_to_axis_type, register_py_to_ax


class _Context(dom.ContextProto):
    anchor: dom.Anchor = _


class _VarSpecType(dom.VarType[_Context]):
    ANCHOR = "text.VarSpec"


class _VarParamType(dom.VarType[_Context]):
    ANCHOR = "text.VarParam"


class _NoAnchorBuiltin(dom.Builtin):
    pass


_T_Draft = TypeVar("_T_Draft")


class _DraftGenericBuiltin(dom.Builtin, Generic[_T_Draft]):
    pass


_PY_TO_AXIS_CTX = _Context(anchor=dom.Anchor.from_str("test.py_to_axis"))


def _anchor_path(t: dom.Type) -> str:
    if isinstance(t, dom.NominalQualifier):
        return t.spec_ref.path
    if isinstance(t, dom.NominalType):
        return t.spec_ref.path
    raise TypeError(f"Cannot extract anchor path from {type(t).__name__}")


class TestAnchorAndSpec(unittest.TestCase):
    def test_anchor_roundtrip_helpers(self):
        ref = dom.anchor("std.Array")
        self.assertEqual(ref.path, "std.Array")
        self.assertEqual(ref.parent.data, ("std",))
        self.assertEqual(ref.child("Item").data, ("std", "Array", "Item"))

    def test_spec_ref_without_args(self):
        spec = dom.spec_ref("std.Text")
        self.assertEqual(spec.path, "std.Text")
        self.assertIsNone(spec.args)

    def test_spec_ref_with_struct_args(self):
        spec = dom.spec_ref("std.Array", dom.literal_struct(size=3))
        self.assertIsNotNone(spec.args)
        self.assertIsInstance(spec.type.meta_args, dom.StructType)


class TestBuiltinTypeFactory(unittest.TestCase):
    def test_builtin_without_anchor_uses_module_qualname(self):
        builtin_type = _NoAnchorBuiltin._type()
        self.assertEqual(
            builtin_type.spec_ref.anchor,
            dom.anchor(f"{_NoAnchorBuiltin.__module__}.{_NoAnchorBuiltin.__qualname__}"),
        )

    def test_non_generic_builtin_rejects_type_args(self):
        with self.assertRaises(TypeError):
            _NoAnchorBuiltin._type(int)

    def test_generic_builtin_requires_exact_arity(self):
        with self.assertRaises(TypeError):
            _DraftGenericBuiltin._type()
        with self.assertRaises(TypeError):
            _DraftGenericBuiltin._type(int, str)

    def test_generic_builtin_specializes_nominal(self):
        builtin_type = _DraftGenericBuiltin._type(int)
        self.assertEqual(builtin_type.spec_ref.path, _DraftGenericBuiltin._anchor_path())
        self.assertIsNotNone(builtin_type.spec_ref.args)


class TestVarsAndStructs(unittest.TestCase):
    def setUp(self):
        self.contrib = _Context(anchor=dom.Anchor.from_str("test.foo"))
        self.K = dom.var(_VarSpecType, self.contrib, "K")
        self.V = dom.var(_VarSpecType, self.contrib, "V")

    def test_var_identity_depends_on_name(self):
        self.assertNotEqual(self.K, self.V)
        self.assertEqual(self.K.type, self.V.type)

    def test_var_spec_and_param_are_distinct(self):
        k_param = dom.var(_VarParamType, self.contrib, "K")
        self.assertNotEqual(self.K, k_param)
        self.assertIsInstance(self.K.type, _VarSpecType)
        self.assertIsInstance(k_param.type, _VarParamType)

    def test_struct_preserves_var_data_and_type_slots(self):
        result = dom.struct(self.K, self.V)
        self.assertEqual(result.data, ("K", "V"))
        self.assertEqual(result.type.meta_attrs.arity, 2)
        self.assertIsInstance(result.type.meta_attrs[0], dom.Var)
        self.assertIsInstance(result.type.meta_attrs[1], dom.Var)

    def test_mixed_struct_keeps_const_and_var_shapes(self):
        result = dom.struct(dom.val(42), self.K)
        self.assertEqual(result.data, (42, "K"))
        self.assertIs(result.type.meta_attrs[0], dom.INTEGER_TYPE)
        self.assertIsInstance(result.type.meta_attrs[1], dom.Var)


class TestUnionInfrastructure(unittest.TestCase):
    def test_union_type_flattens_nested_members(self):
        a = dom.nominal_type("A")
        b = dom.nominal_type("B")
        c = dom.nominal_type("C")
        ab = dom.UnionType(types=frozenset({a, b}))
        abc = dom.union_type(ab, c)
        self.assertEqual(abc.types, frozenset({a, b, c}))

    def test_union_requires_active_variant_in_member_set(self):
        with self.assertRaises(TypeError):
            dom.union(frozenset({dom.TEXT_TYPE}), dom.val(42))

    def test_union_can_use_var_as_discriminator(self):
        contrib = _Context(anchor=dom.Anchor.from_str("test.foo"))
        k = dom.var(_VarSpecType, contrib, "K")
        v = dom.var(_VarSpecType, contrib, "V")
        union = dom.union(frozenset({k, v}), k)
        self.assertIs(union.data[0], k)
        self.assertEqual(union.data[1], "K")


class TestEncodeDecodeContracts(unittest.TestCase):
    def test_unknown_nominal_tuple_payload_fails_strictly(self):
        value = dom.Const(type=dom.nominal_type("test.MissingBuiltin"), data=(1,))
        with self.assertRaisesRegex(ValueError, "no registered builtin class"):
            dom.decode(value)

    def test_union_decode_is_explicitly_not_supported(self):
        union = dom.union(frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}), dom.val(42))
        with self.assertRaises(NotImplementedError):
            dom.decode(dom.encode(union))

    def test_err_is_typed_and_roundtrips(self):
        err = dom.Err()
        self.assertIsInstance(dom.type_of(err).data, dom.ErrType)
        self.assertEqual(dom.decode(dom.encode(err)), err)


class TestPyToAxisInterop(unittest.TestCase):
    def test_scalar_types_map_to_expected_nominals(self):
        self.assertIs(python_to_axis_type(int, ctx=_PY_TO_AXIS_CTX), dom.INTEGER_TYPE)
        self.assertIs(python_to_axis_type(str, ctx=_PY_TO_AXIS_CTX), dom.TEXT_TYPE)
        self.assertIs(python_to_axis_type(bool, ctx=_PY_TO_AXIS_CTX), dom.BOOLEAN_TYPE)
        self.assertIs(python_to_axis_type(float, ctx=_PY_TO_AXIS_CTX), dom.DECIMAL_TYPE)
        self.assertIs(python_to_axis_type(Decimal, ctx=_PY_TO_AXIS_CTX), dom.DECIMAL_TYPE)
        self.assertIs(python_to_axis_type(type(None), ctx=_PY_TO_AXIS_CTX), dom.EMPTY_TYPE)

    def test_union_annotations_map_to_union_type(self):
        result = python_to_axis_type(Union[int, str], ctx=_PY_TO_AXIS_CTX)
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}))

        result = python_to_axis_type(int | None, ctx=_PY_TO_AXIS_CTX)
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.EMPTY_TYPE}))

    def test_collection_annotations_map_to_nominal_qualifiers(self):
        self.assertEqual(_anchor_path(python_to_axis_type(dict[str, int], ctx=_PY_TO_AXIS_CTX)), "std.Map")
        self.assertEqual(_anchor_path(python_to_axis_type(list[str], ctx=_PY_TO_AXIS_CTX)), "std.List")
        self.assertEqual(_anchor_path(python_to_axis_type(set[int], ctx=_PY_TO_AXIS_CTX)), "std.Set")

    def test_builtin_alias_projects_to_nominal_type(self):
        projected = python_to_axis_type(_DraftGenericBuiltin[int], ctx=_PY_TO_AXIS_CTX)
        self.assertIsInstance(projected, dom.NominalType)
        self.assertEqual(projected.spec_ref.path, _DraftGenericBuiltin._anchor_path())

    def test_register_py_to_ax_accepts_custom_transform(self):
        class CustomPyType:
            pass

        custom_dom_type = dom.nominal_type("test.CustomPyType")
        register_py_to_ax(CustomPyType, lambda: custom_dom_type)

        self.assertIn(CustomPyType, _PY_TO_AX_TRANSFORMS)
