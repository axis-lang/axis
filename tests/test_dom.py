"""Comprehensive tests for the axis domain model (dom/).

Tests the cremallera (zipper) pattern: every Pure is (type, data),
where type describes how to interpret data. Types are also values
(self-descriptive via __type__/__data__).
"""
import unittest
from decimal import Decimal
from typing import Union, TypeVar, Generic
from types import UnionType as PEP604Union

from protobase import frozendict, _

from axis import dom
from axis.dom.introspect import (
    _python_to_axis_type,
    _transform_generic,
    _PY_TO_AX_TRANSFORMS,
    register_py_to_ax,
)

class _Context(dom.ContextProto): 
    anchor: dom.Anchor = _
class _VarSpecType(dom.VarType[_Context]):
    ANCHOR = 'text.VarSpec'
class _VarParamType(dom.VarType[_Context]): 
    ANCHOR = 'text.VarParam'


# ---------------------------------------------------------------------------
# Anchor / Ref
# ---------------------------------------------------------------------------

class TestAnchor(unittest.TestCase):
    def test_from_str(self):
        ref = dom.Anchor.from_str("std.Array")
        self.assertEqual(dom.ref_segments(ref), ("std", "Array"))

    def test_child(self):
        ref = dom.Anchor.from_str("std").child("Array")
        self.assertEqual(dom.ref_segments(ref), ("std", "Array"))

    def test_parent(self):
        ref = dom.Anchor.from_str("std.Array")
        parent = ref.parent
        self.assertIsNotNone(parent)
        self.assertEqual(dom.ref_segments(parent), ("std",))

    def test_root_has_no_parent(self):
        ref = dom.Anchor.from_str("std")
        self.assertIsNone(ref.parent)

    def test_name(self):
        ref = dom.Anchor.from_str("std.Array")
        self.assertEqual(ref.name, "Array")
        self.assertEqual(ref.root, "std")


class TestSpecRef(unittest.TestCase):
    def test_simple_spec(self):
        spec = dom._spec_ref("std.Text")
        self.assertIsInstance(spec, dom.Spec)
        self.assertEqual(spec.anchor.data, ("std", "Text"))
        self.assertIsNone(spec.specialization)

    def test_spec_with_struct(self):
        struct = dom._literal_struct(x=1, y=2)
        spec = dom._spec_ref("std.Array", struct)
        self.assertIsNotNone(spec.specialization)
        self.assertIsInstance(spec.type.spec, dom.StructType)

    def test_anchor_specialize(self):
        anchor = dom.Anchor.from_str("std.Array")
        struct = dom._literal_struct(size=3)
        spec = anchor.specialize(struct)
        self.assertEqual(spec.anchor.data, ("std", "Array"))
        self.assertIsNotNone(spec.specialization)


# ---------------------------------------------------------------------------
# Literal / Const
# ---------------------------------------------------------------------------

class TestLiteral(unittest.TestCase):
    def test_integer(self):
        val = dom._literal(42)
        self.assertEqual(val.data, 42)
        self.assertEqual(val.type, dom.INTEGER_TYPE)

    def test_string(self):
        val = dom._literal("hello")
        self.assertEqual(val.data, "hello")
        self.assertEqual(val.type, dom.TEXT_TYPE)

    def test_boolean(self):
        val = dom._literal(True)
        self.assertEqual(val.data, True)
        self.assertEqual(val.type, dom.BOOLEAN_TYPE)

    def test_none(self):
        val = dom._literal(None)
        self.assertIsNone(val.data)
        self.assertEqual(val.type, dom.EMPTY_TYPE)

    def test_float(self):
        val = dom._literal(3.14)
        self.assertEqual(val.data, 3.14)
        self.assertEqual(val.type, dom.DECIMAL_TYPE)

    def test_decimal(self):
        val = dom._literal(Decimal("0.5"))
        self.assertEqual(val.data, Decimal("0.5"))
        self.assertEqual(val.type, dom.DECIMAL_TYPE)

    def test_unsupported_type_raises(self):
        with self.assertRaises(TypeError):
            dom._literal([1, 2, 3])


class TestConst(unittest.TestCase):
    def test_new_literal(self):
        val = dom.Const.new_literal(42)
        self.assertEqual(val.data, 42)
        self.assertEqual(val.type, dom.INTEGER_TYPE)

    def test_new_literal_struct(self):
        val = dom.Const.new_literal_struct(x=1, y="hello")
        self.assertIsInstance(val.type, dom.StructType)
        self.assertEqual(val.data, (1, "hello"))

    def test_literal_struct_positional(self):
        val = dom._literal_struct(1, 2, 3)
        self.assertIsInstance(val.type, dom.StructType)
        self.assertEqual(val.data, (1, 2, 3))
        self.assertEqual(val.type.fields.arity, 3)


# ---------------------------------------------------------------------------
# Struct with vars (cremallera decomposition)
# ---------------------------------------------------------------------------

class TestStructWithVars(unittest.TestCase):
    def setUp(self):
        
        self.anchor = dom.Anchor.from_str("test.foo")
        self.contrib = _Context(anchor=self.anchor)
        self.K = dom.var(_VarSpecType, self.contrib, "K")
        self.V = dom.var(_VarSpecType, self.contrib, "V")

    def test_new_struct_positional(self):
        result = dom.Const.new_struct(self.K, self.V)
        self.assertIsInstance(result.type, dom.StructType)
        # data side: variable names
        self.assertEqual(result.data, ("K", "V"))
        # type side: Var instances (which ARE Types) with distinct data
        self.assertNotEqual(result.type.fields[0], result.type.fields[1])
        self.assertIsInstance(result.type.fields[0], dom.Var)
        self.assertIsInstance(result.type.fields[1], dom.Var)

    def test_new_struct_named(self):
        result = dom._struct(key=self.K, val=self.V)
        self.assertIsInstance(result.type, dom.StructType)
        self.assertEqual(result.data, ("K", "V"))
        self.assertEqual(result.type.fields.arity, 2)

    def test_new_struct_mixed(self):
        """Mix Const and Var in a struct."""
        lit = dom.Const.new_literal(42)
        result = dom.Const.new_struct(lit, self.K)
        self.assertEqual(result.data, (42, "K"))
        self.assertEqual(result.type.fields[0], dom.INTEGER_TYPE)
        self.assertIsInstance(result.type.fields[1], dom.Var)


# ---------------------------------------------------------------------------
# NominalType
# ---------------------------------------------------------------------------

class TestNominalType(unittest.TestCase):

    def test_predefined_constants(self):
        """All std.* constants should be NominalType instances."""
        for name, nt in [
            ("INTEGER_TYPE", dom.INTEGER_TYPE),
            ("TEXT_TYPE", dom.TEXT_TYPE),
            ("BOOLEAN_TYPE", dom.BOOLEAN_TYPE),
            ("EMPTY_TYPE", dom.EMPTY_TYPE),
            ("DECIMAL_TYPE", dom.DECIMAL_TYPE),
        ]:
            with self.subTest(name=name):
                self.assertIsInstance(nt, dom.NominalType)


# ---------------------------------------------------------------------------
# Qualifier (cremallera: type = NominalQualifier, data = (underlying, spec_ref))
# ---------------------------------------------------------------------------

class TestQualifier(unittest.TestCase):
    def setUp(self):
        self.anchor = dom.Anchor.from_str("test.foo")
        self.contrib = _Context(anchor=self.anchor)
        self.K = dom.var(_VarSpecType, self.contrib, "K")
        self.V = dom.var(_VarSpecType, self.contrib, "V")



    # def test_new_qual_chained(self):
    #     """Array[2,2] Mapping[K] V — chained qualifiers (nested cremallera)."""
    #     two = dom.Const.new_literal(2)

    #     # inner: Mapping[K] V
    #     mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
    #         dom.Const.new_struct(self.K)
    #     )
    #     inner = dom.Const.new_qual(spec_ref=mapping_spec, underlying=self.V)

    #     # outer: Array[2,2] (Mapping[K] V)
    #     array_spec = dom.Anchor.from_str("std.Array").specialize(
    #         dom.Const.new_struct(two, two)
    #     )
    #     outer = dom.Const.new_qual(spec_ref=array_spec, underlying=inner)

    #     # type side: nested NominalQualifiers
    #     self.assertIsInstance(outer.type, dom.NominalQualifier)
    #     self.assertIsInstance(outer.type.underlying, dom.NominalQualifier)
    #     self.assertEqual(outer.type.underlying.underlying, self.V.type)

    #     # data side
    #     inner_data = outer.data[0]
    #     array_data = outer.data[1]
    #     self.assertEqual(inner_data, ("V", (("std", "Mapping"), ("K",))))
    #     self.assertEqual(array_data, (("std", "Array"), (2, 2)))


# ---------------------------------------------------------------------------
# Var types — name distinguishability
# ---------------------------------------------------------------------------

class TestVarType(unittest.TestCase):
    def setUp(self):
        self.anchor = dom.Anchor.from_str("test.foo")
        self.contrib = _Context(anchor=self.anchor)

    def test_subclass_relationships(self):
        self.assertTrue(issubclass(dom.VarSpecType, dom.VarType))
        self.assertTrue(issubclass(dom.VarParamType, dom.VarType))
        self.assertTrue(issubclass(dom.VarType, dom.Type))

    def test_spec_vars_distinguishable(self):
        """K and V from same contribution must be distinct Vars."""
        K = dom.var(_VarSpecType, self.contrib, "K")
        V = dom.var(_VarSpecType, self.contrib, "V")
        # Var instances are distinct (different data)
        self.assertNotEqual(K, V)
        self.assertEqual(K.data, "K")
        self.assertEqual(V.data, "V")
        # VarTypes carry same ctx, so they are equal
        self.assertEqual(K.type, V.type)

    def test_param_vars_distinguishable(self):
        """Param variables also distinguishable."""
        a = dom.var(_VarParamType, self.contrib, "a")
        b = dom.var(_VarParamType, self.contrib, "b")
        self.assertNotEqual(a, b)
        self.assertEqual(a.data, "a")
        self.assertEqual(b.data, "b")

    def test_spec_vs_param_distinct(self):
        """Spec and param vars with same name are distinct types."""
        K_spec = dom.var(_VarSpecType, self.contrib, "K")
        K_param = dom.var(_VarParamType, self.contrib, "K")
        # Different Var instances (different metatype)
        self.assertNotEqual(K_spec, K_param)
        self.assertIsInstance(K_spec.type, dom.VarSpecType)
        self.assertIsInstance(K_param.type, dom.VarParamType)

    def test_union_with_type_vars_no_collapse(self):
        """Union of two distinct type vars should have 2 members."""
        K = dom.var(_VarSpecType, self.contrib, "K")
        V = dom.var(_VarSpecType, self.contrib, "V")
        # Var IS a Type, so use Var instances directly in the union
        union = dom.UnionType(types=frozenset({K, V}))
        self.assertEqual(len(union.types), 2)


# ---------------------------------------------------------------------------
# Union: flattening, factory, cremallera
# ---------------------------------------------------------------------------

class TestUnion(unittest.TestCase):

    # --- __invariants__: direct UnionType must be flat ---

    def test_invariants_rejects_nested(self):
        """Direct UnionType() with nested UnionType violates __invariants__."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        # Direct construction with a nested UnionType is allowed by Consed,
        # but __invariants__ catches it.
        nested = dom.UnionType(types=frozenset({ab, C}))
        with self.assertRaises(TypeError):
            nested.__invariants__()

    def test_invariants_accepts_flat(self):
        """Flat UnionType passes __invariants__."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        union = dom.UnionType(types=frozenset({A, B}))
        union.__invariants__()  # should not raise

    def test_invariants_rejects_empty(self):
        """Empty UnionType violates __invariants__."""
        empty = dom.UnionType(types=frozenset())
        with self.assertRaises(TypeError):
            empty.__invariants__()

    # --- _union_type: flattening constructor ---

    def test_union_type_flatten_nested(self):
        """_union_type(A|B, C) flattens to {A, B, C}."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        abc = dom._union_type(ab, C)
        self.assertEqual(len(abc.types), 3)
        self.assertEqual(abc.types, frozenset({A, B, C}))

    def test_union_type_flatten_deeply_nested(self):
        """_union_type flattens ((A|B)|C, D) → {A, B, C, D}."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        D = dom._nominal_type("D")
        ab = dom.UnionType(types=frozenset({A, B}))
        # ab is flat, use _union_type for the rest
        abc = dom._union_type(ab, C)
        abcd = dom._union_type(abc, D)
        self.assertEqual(len(abcd.types), 4)
        self.assertEqual(abcd.types, frozenset({A, B, C, D}))

    def test_union_type_flatten_both_sides(self):
        """_union_type(A|B, C|D) flattens to {A, B, C, D}."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        D = dom._nominal_type("D")
        ab = dom.UnionType(types=frozenset({A, B}))
        cd = dom.UnionType(types=frozenset({C, D}))
        abcd = dom._union_type(ab, cd)
        self.assertEqual(len(abcd.types), 4)

    def test_union_type_no_op_when_flat(self):
        """_union_type on already-flat types is a no-op."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        union = dom._union_type(A, B)
        self.assertEqual(len(union.types), 2)

    def test_union_type_deduplicates(self):
        """_union_type(A|B, A) deduplicates to {A, B}."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        ab = dom.UnionType(types=frozenset({A, B}))
        aba = dom._union_type(ab, A)
        self.assertEqual(len(aba.types), 2)
        self.assertEqual(aba.types, frozenset({A, B}))

    def test_union_type_result_passes_invariants(self):
        """_union_type always produces a flat result."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        result = dom._union_type(ab, C)
        result.__invariants__()  # must not raise

    # --- _union / Const.new_union: value factory ---

    def test_new_union_factory(self):
        """Const.new_union creates a proper union value."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        self.assertIsInstance(union, dom.Const)
        self.assertIsInstance(union.type, dom.UnionType)
        self.assertEqual(union.type.types, types)
        # data = (discriminator, value_data)
        self.assertIsInstance(union.data, tuple)
        self.assertEqual(len(union.data), 2)
        self.assertIs(union.data[0], dom.INTEGER_TYPE)
        self.assertEqual(union.data[1], 42)

    def test_new_union_text_variant(self):
        """Union with Text active variant."""
        text_val = dom.Const.new_literal("hello")
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, text_val)
        self.assertIs(union.data[0], dom.TEXT_TYPE)
        self.assertEqual(union.data[1], "hello")

    def test_new_union_rejects_wrong_type(self):
        """Active variant type must be in the union types."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.TEXT_TYPE, dom.BOOLEAN_TYPE})
        with self.assertRaises(TypeError):
            dom.Const.new_union(types, int_val)

    def test_new_union_with_struct_variant(self):
        """Union where the active variant is a struct."""
        struct_val = dom._literal_struct(x=1, y=2)
        types = frozenset({struct_val.type, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, struct_val)
        self.assertIs(union.data[0], struct_val.type)
        self.assertEqual(union.data[1], (1, 2))

    def test_union_flattens_via_union(self):
        """_union flattens types that contain nested UnionTypes."""
        A = dom._nominal_type("A")
        B = dom._nominal_type("B")
        C = dom._nominal_type("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        val = dom.Const(type=A, data=None)
        # Pass frozenset containing a UnionType — _union should flatten
        union = dom._union(frozenset({ab, C}), val)
        self.assertEqual(len(union.type.types), 3)
        self.assertEqual(union.type.types, frozenset({A, B, C}))

    # --- dir / get ---

    def test_dir_union(self):
        """Union dir returns Missing (unions resolved at construction)."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        self.assertIs(dom.dir(union), None)

    def test_get_union_raises(self):
        """get on union raises KeyError (opaque — resolved at construction)."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        with self.assertRaises(KeyError):
            dom.get(union, 'discriminator')
        with self.assertRaises(KeyError):
            dom.get(union, 'value')
        with self.assertRaises(KeyError):
            dom.get(union, 'nonexistent')

    def test_union_with_var_types(self):
        """Union over type variables with one active."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K = dom.var(_VarSpecType, contrib, "K")
        V = dom.var(_VarSpecType, contrib, "V")
        # Var IS a Type, so use Var instances directly
        types = frozenset({K, V})
        # Active variant is K
        union = dom._union(types, K)
        self.assertIs(union.data[0], K)
        self.assertEqual(union.data[1], "K")


# ---------------------------------------------------------------------------
# Self-description: Type.as_val (__type__ / __data__)
# ---------------------------------------------------------------------------

class TestSelfDescription(unittest.TestCase):
    def test_nominal_type_as_val(self):
        """NominalType.as_val produces a valid Const."""
        nt = dom.INTEGER_TYPE
        val = nt.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertIsInstance(val.type, dom.NominalType)
        # The metatype should reference dom.Type.Nominal
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
            ("dom", "Type", "Nominal"),
        )
        # data side is the NominalType itself (no AUTO_ENCODE)
        self.assertIs(val.data, nt)

    def test_struct_type_as_val(self):
        """StructType.as_val produces a valid Const."""
        st = dom.StructType(fields=dom.Struct.new(x=dom.INTEGER_TYPE, y=dom.TEXT_TYPE))
        val = st.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertIsInstance(val.type, dom.NominalType)
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
            ("dom", "Type", "Struct"),
        )
        self.assertIs(val.data, st)

    def test_union_type_as_val(self):
        """UnionType.as_val should work (not raise NotImplementedError)."""
        ut = dom.UnionType(types=frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}))
        val = ut.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertIsInstance(val.type, dom.NominalType)
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
            ("dom", "Type", "Union"),
        )

    def test_qualifier_type_as_val(self):
        """NominalQualifier.as_val should work."""
        qual = dom._nominal_qual(anchor="test.foo", underlying=dom.TEXT_TYPE)  # type: ignore
        val = qual.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertIsInstance(val.type, dom.NominalType)
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
            ("dom", "Qual", "Nominal"),
        )

    def test_var_spec_type_as_val(self):
        """Var.as_val should work (Var IS a Pure)."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K = dom.var(_VarSpecType, contrib, "K")
        val = K.as_val
        self.assertIsInstance(val, dom.Const)
        # Var's metatype is VarSpecType (which is a VarType, not NominalType)
        self.assertIsInstance(val.type, _VarSpecType)
        # The VarSpecType itself is self-descriptive
        vt_val = val.type.as_val
        self.assertIsInstance(vt_val, dom.Const)
        self.assertIsInstance(vt_val.type, dom.NominalType)
        self.assertEqual(
            dom.ref_segments(vt_val.type.spec_ref),
            ("dom", "Type", "Var", "Spec"),
        )

    def test_recursive_self_description(self):
        """Type.as_val.type is also self-descriptive (infinite recursion works)."""
        nt = dom.INTEGER_TYPE
        level1 = nt.as_val           # Const(type=<metatype>, data=nt)
        level2 = level1.type.as_val  # Const(type=<meta-metatype>, data=<metatype>)
        self.assertIsInstance(level2, dom.Const)
        self.assertIsInstance(level2.type, dom.NominalType)


# ---------------------------------------------------------------------------
# _encode: Builtin-rich → raw (JSON-like)
# ---------------------------------------------------------------------------

class TestEncode(unittest.TestCase):
    def test_encode_literal(self):
        self.assertEqual(dom._encode(42), 42)
        self.assertEqual(dom._encode("hello"), "hello")
        self.assertIsNone(dom._encode(None))

    def test_encode_builtin(self):
        """Encoding a NominalType strips it to tuple of attrs."""
        encoded = dom._encode(dom.INTEGER_TYPE)
        self.assertIsInstance(encoded, tuple)
        # NominalType has one attr (spec_ref: Spec), Spec has two attrs (type, data)
        # So encoded should be a tuple containing the encoded spec_ref

    def test_encode_tuple_with_builtins(self):
        """Tuples containing Builtins should be recursed into."""
        data = (dom.INTEGER_TYPE, "hello", 42)
        encoded = dom._encode(data)
        self.assertIsInstance(encoded, tuple)
        self.assertEqual(encoded[1], "hello")
        self.assertEqual(encoded[2], 42)
        # First element should be encoded (not a Builtin anymore)
        self.assertNotIsInstance(encoded[0], dom.Builtin)

    def test_encode_struct(self):
        """Structs are encoded via their values tuple."""
        s = dom.Struct.new(x=1, y=2)
        encoded = dom._encode(s)
        self.assertEqual(encoded, (1, 2))

    def test_encode_struct_type(self):
        """StructType with fields encoded to nested tuples."""
        st = dom.StructType(fields=dom.Struct.new(x=dom.INTEGER_TYPE))
        encoded = dom._encode(st)
        self.assertIsInstance(encoded, tuple)

    def test_encode_idempotent_on_raw(self):
        """Encoding already-raw data should be a no-op."""
        raw = (1, "hello", None, (2, 3))
        self.assertEqual(dom._encode(raw), raw)


# ---------------------------------------------------------------------------
# dir / get: cremallera decomposition
# ---------------------------------------------------------------------------

class TestDirGet(unittest.TestCase):
    def test_dir_struct_positional(self):
        val = dom._literal_struct(1, 2, 3)
        fields = dom.dir(val)
        self.assertIsInstance(fields, dom.Struct)
        self.assertEqual(fields.index.keys, (None, None, None))
        self.assertEqual(fields.arity, 3)

    def test_dir_struct_named(self):
        val = dom._literal_struct(x=1, y=2)
        fields = dom.dir(val)
        self.assertIsInstance(fields, dom.Struct)
        self.assertEqual(fields.index.keys, ("x", "y"))

    def test_dir_struct_mixed(self):
        """Positional fields get None keys, named fields get str keys."""
        val = dom._literal_struct(1, x=2)
        fields = dom.dir(val)
        self.assertIsInstance(fields, dom.Struct)
        self.assertEqual(fields.index.keys, (None, "x"))

    def test_get_struct_by_name(self):
        val = dom._literal_struct(x=42, y="hello")
        x = dom.get(val, "x")
        self.assertIsInstance(x, dom.Const)
        self.assertEqual(x.data, 42)
        self.assertEqual(x.type, dom.INTEGER_TYPE)

    def test_get_struct_by_index(self):
        val = dom._literal_struct(1, 2, 3)
        second = dom.get(val, 1)
        self.assertEqual(second.data, 2)

    def test_get_qualifier_raises(self):
        """get on NominalQualifier raises KeyError (opaque)."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K = dom.var(_VarSpecType, contrib, "K")
        V = dom.var(_VarSpecType, contrib, "V")
        mapping_spec = dom.Anchor.from_str("std.Map").specialize(
            dom.Const.new_struct(K)
        )
        qual_type = dom._nominal_qual(
            anchor=mapping_spec.anchor,
            struct=mapping_spec.specialization,
            underlying=V.type,
        )
        qual = dom.Const(type=qual_type, data=(V.data, mapping_spec.data))

        with self.assertRaises(KeyError):
            dom.get(qual, "underlying")

    def test_dir_qualifier(self):
        """Qualifier dir returns None (opaque)."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K = dom.var(_VarSpecType, contrib, "K")
        V = dom.var(_VarSpecType, contrib, "V")
        mapping_spec = dom.Anchor.from_str("std.Map").specialize(
            dom.Const.new_struct(K)
        )
        qual_type = dom._nominal_qual(
            anchor=mapping_spec.anchor,
            struct=mapping_spec.specialization,
            underlying=V.type,
        )
        qual = dom.Const(type=qual_type, data=(V.data, mapping_spec.data))
        self.assertIs(dom.dir(qual), None)

    def test_dir_nominal_empty(self):
        """NominalType values have no introspectable members (opaque)."""
        val = dom.Const.new_literal(42)
        self.assertIs(dom.dir(val), None)

    def test_get_nonexistent_raises(self):
        val = dom._literal_struct(x=1)
        with self.assertRaises(KeyError):
            dom.get(val, "nonexistent")

    def test_get_non_pure_raises(self):
        err = dom.Err()
        with self.assertRaises(TypeError):
            dom.get(err, "x")

    def test_dir_non_pure_returns_none(self):
        """dir on non-Pure values returns None."""
        err = dom.Err()
        self.assertIs(dom.dir(err), None)

    def test_dir_struct_returns_types(self):
        """dir on struct returns Struct with field types."""
        val = dom._literal_struct(x=42, y="hello")
        fields = dom.dir(val)
        self.assertIsInstance(fields, dom.Struct)
        self.assertEqual(fields[0], dom.INTEGER_TYPE)
        self.assertEqual(fields[1], dom.TEXT_TYPE)


# ---------------------------------------------------------------------------
# type_of
# ---------------------------------------------------------------------------

class TestTypeOf(unittest.TestCase):
    def test_type_of_const(self):
        val = dom.Const.new_literal(42)
        tv = dom.type_of(val)
        self.assertIsInstance(tv, dom.Const)
        self.assertIs(tv.data, dom.INTEGER_TYPE)

    def test_type_of_ref(self):
        ref = dom.Anchor.from_str("std.Text")
        tv = dom.type_of(ref)
        self.assertIsInstance(tv, dom.Const)

    def test_type_of_err_raises(self):
        with self.assertRaises(TypeError):
            dom.type_of(dom.Err())


# ---------------------------------------------------------------------------
# Const.encode — union discriminator behavior under encoding
# ---------------------------------------------------------------------------

class TestUnionEncode(unittest.TestCase):
    """Exclusive tests for union encode behavior.

    When we do union.encode, the data side gets _encode'd:
      (discriminator: Type, value_data) → (_encode(discriminator), _encode(value_data))

    The discriminator is a Type (a Builtin). _encode strips Builtins to raw
    tuples of their attrs. This section explores whether the encoded
    discriminator retains enough information to identify the active variant.
    """

    def test_encode_type_side_unchanged(self):
        """encode preserves the type side exactly (same object)."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        encoded = union.encoded
        self.assertIs(encoded.type, union.type)

    def test_encode_data_is_raw(self):
        """After encode, data contains no Builtins."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        encoded = union.encoded
        disc_raw, val_raw = encoded.data
        self.assertNotIsInstance(disc_raw, dom.Builtin)
        self.assertEqual(val_raw, 42)

    def test_encode_discriminator_loses_identity(self):
        """After encode, the discriminator is no longer a Type instance.

        This is the fundamental change: `union.data[0] is INTEGER_TYPE`
        is True before encode, False after.
        """
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)

        # Before: discriminator IS the Type object
        self.assertIs(union.data[0], dom.INTEGER_TYPE)
        self.assertIsInstance(union.data[0], dom.Type)

        # After: discriminator is raw data (tuple)
        encoded = union.encoded
        self.assertNotIsInstance(encoded.data[0], dom.Type)
        self.assertIsInstance(encoded.data[0], tuple)

    def test_encode_discriminator_recoverable_via_type_side(self):
        """The encoded discriminator can be matched back to its Type
        by encoding each candidate type from the type side.

        This is how _decode would recover the active variant:
        for each t in union_type.types, check if _encode(t) == encoded_disc.
        """
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        encoded = union.encoded
        enc_disc = encoded.data[0]

        # Try to recover which type the discriminator represents
        matches = [
            t for t in encoded.type.types
            if dom._encode(t) == enc_disc
        ]
        self.assertEqual(len(matches), 1)
        self.assertIs(matches[0], dom.INTEGER_TYPE)

    def test_encode_distinct_nominals_distinguishable(self):
        """Different NominalTypes (different anchors) encode to different
        raw data. The discriminator is unambiguous after encoding.
        """
        enc_int = dom._encode(dom.INTEGER_TYPE)
        enc_text = dom._encode(dom.TEXT_TYPE)
        enc_bool = dom._encode(dom.BOOLEAN_TYPE)
        # All distinct
        self.assertNotEqual(enc_int, enc_text)
        self.assertNotEqual(enc_int, enc_bool)
        self.assertNotEqual(enc_text, enc_bool)

    def test_encode_collision_var_spec_vs_param(self):
        """KNOWN ISSUE: VarSpecType and VarParamType with the same ctx
        encode to identical raw data.

        _encode strips class identity — it only sees attrs. Both classes
        have {ctx}, so the encoded tuples are equal.

        This means: for a union of Var.spec("K") | Var.param("K"),
        the encoded discriminator could be ambiguous. However, with the
        new model, Var IS a Type, so the union contains Var instances
        (not VarTypes), and they have different data ("K" from spec vs
        "K" from param) but the *types* (VarSpecType vs VarParamType)
        still encode the same.
        """
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K_spec = dom.var(_VarSpecType, contrib, "K")
        K_param = dom.var(_VarParamType, contrib, "K")

        enc_spec = dom._encode(K_spec.type)
        enc_param = dom._encode(K_param.type)

        # COLLISION: same ctx attrs → same encoded form for VarTypes
        self.assertEqual(enc_spec, enc_param)

        # The Vars themselves ARE different (different metatype class)
        self.assertNotEqual(K_spec, K_param)

    def test_encode_no_collision_different_names(self):
        """Var("K") vs Var("V") are distinct Vars with different data,
        so they encode to different raw forms.
        """
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Context(anchor=anchor)
        K = dom.var(_VarSpecType, contrib, "K")
        V = dom.var(_VarSpecType, contrib, "V")
        self.assertNotEqual(dom._encode(K), dom._encode(V))

    def test_encode_struct_variant_preserves_data(self):
        """Encoding a union whose active variant is a struct
        recursively encodes the struct data.
        """
        struct_val = dom._literal_struct(x=1, y="hi")
        types = frozenset({struct_val.type, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, struct_val)
        encoded = union.encoded

        disc_raw, val_raw = encoded.data
        # value_data was (1, "hi") — already raw, unchanged
        self.assertEqual(val_raw, (1, "hi"))
        # discriminator is the StructType, now encoded
        self.assertNotIsInstance(disc_raw, dom.Builtin)

    def test_encode_idempotent(self):
        """Encoding an already-encoded union is a no-op (idempotent)."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        once = union.encoded
        twice = once.encoded
        self.assertEqual(once.data, twice.data)
        self.assertIs(once.type, twice.type)

    def test_encode_literal_union_roundtrip_info(self):
        """For a union of literal nominal types, ALL information needed
        for reconstruction is present after encode:
        - type side: UnionType with the full set of Types
        - data side: (raw_discriminator, raw_value)
        - matching: exactly one type encodes to raw_discriminator
        """
        text_val = dom.Const.new_literal("world")
        types = frozenset({
            dom.INTEGER_TYPE, dom.TEXT_TYPE,
            dom.BOOLEAN_TYPE, dom.DECIMAL_TYPE,
        })
        union = dom.Const.new_union(types, text_val)
        encoded = union.encoded

        # The type side still knows all possible types
        self.assertEqual(encoded.type.types, types)

        # We can recover exactly which variant is active
        enc_disc = encoded.data[0]
        matches = [
            t for t in encoded.type.types
            if dom._encode(t) == enc_disc
        ]
        self.assertEqual(len(matches), 1)
        self.assertIs(matches[0], dom.TEXT_TYPE)

        # And recover the original value
        recovered_type = matches[0]
        recovered_data = encoded.data[1]
        recovered = dom.Const(type=recovered_type, data=recovered_data)
        self.assertEqual(recovered.type, dom.TEXT_TYPE)
        self.assertEqual(recovered.data, "world")


# ---------------------------------------------------------------------------
# PyAx interop: _python_to_axis_type / register_py_to_ax
# ---------------------------------------------------------------------------


def _anchor_path(t: dom.Type) -> str:
    """Extract the dotted anchor path from a NominalType or NominalQualifier."""
    if isinstance(t, dom.NominalQualifier):
        return ".".join(t.spec_ref.anchor.data)
    if isinstance(t, dom.NominalType):
        return ".".join(t.spec_ref.anchor.data)
    raise TypeError(f"Cannot extract anchor path from {type(t).__name__}")


class TestPyToAxisScalar(unittest.TestCase):
    """Scalar Python types map to the corresponding std.* NominalType."""

    def test_int(self):
        self.assertIs(_python_to_axis_type(int), dom.INTEGER_TYPE)

    def test_str(self):
        self.assertIs(_python_to_axis_type(str), dom.TEXT_TYPE)

    def test_bool(self):
        self.assertIs(_python_to_axis_type(bool), dom.BOOLEAN_TYPE)

    def test_float(self):
        self.assertIs(_python_to_axis_type(float), dom.DECIMAL_TYPE)

    def test_decimal(self):
        self.assertIs(_python_to_axis_type(Decimal), dom.DECIMAL_TYPE)

    def test_none_type(self):
        self.assertIs(_python_to_axis_type(type(None)), dom.EMPTY_TYPE)

    def test_unknown_scalar_fallback(self):
        """A plain class with no registration falls back to ANY_TYPE."""
        class Unregistered:
            pass
        self.assertIs(_python_to_axis_type(Unregistered), dom.ANY_TYPE)


class TestPyToAxisUnion(unittest.TestCase):
    """Union annotations (typing.Union and PEP 604) produce UnionType."""

    def test_typing_union(self):
        result = _python_to_axis_type(Union[int, str])
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}))

    def test_pep604_union(self):
        """PEP 604 `int | str` is handled via the registered PEP604Union transform."""
        result = _python_to_axis_type(int | str)
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}))

    def test_typing_union_with_none(self):
        result = _python_to_axis_type(Union[int, None])
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.EMPTY_TYPE}))

    def test_pep604_union_with_none(self):
        result = _python_to_axis_type(int | None)
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(result.types, frozenset({dom.INTEGER_TYPE, dom.EMPTY_TYPE}))

    def test_triple_union_pep604(self):
        result = _python_to_axis_type(int | str | None)
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(
            result.types,
            frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE, dom.EMPTY_TYPE}),
        )

    def test_triple_union_typing(self):
        result = _python_to_axis_type(Union[int, str, bool])
        self.assertIsInstance(result, dom.UnionType)
        self.assertIn(dom.INTEGER_TYPE, result.types)
        self.assertIn(dom.TEXT_TYPE, result.types)
        self.assertIn(dom.BOOLEAN_TYPE, result.types)

    def test_nested_typing_union_flattens(self):
        """Union[Union[int, str], bool] flattens via _union_type."""
        inner = Union[int, str]
        # Build the outer by hand — typing.Union auto-flattens,
        # so we test _union_type's flattening directly.
        inner_type = _python_to_axis_type(inner)
        outer = dom._union_type(inner_type, dom.BOOLEAN_TYPE)
        self.assertIsInstance(outer, dom.UnionType)
        self.assertEqual(
            outer.types,
            frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE, dom.BOOLEAN_TYPE}),
        )


class TestPyToAxisGeneric(unittest.TestCase):
    """Registered generic Python types project correctly to Axis types."""

    # -- tuple --

    def test_tuple_variadic(self):
        """tuple[int, ...] -> std.List int"""
        result = _python_to_axis_type(tuple[int, ...])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.List")
        self.assertIs(result.underlying, dom.INTEGER_TYPE)

    def test_tuple_fixed(self):
        """tuple[int, str] -> StructType(fields=(INTEGER_TYPE, TEXT_TYPE))"""
        result = _python_to_axis_type(tuple[int, str])
        self.assertIsInstance(result, dom.StructType)
        self.assertEqual(result.fields.arity, 2)
        self.assertIs(result.fields[0], dom.INTEGER_TYPE)
        self.assertIs(result.fields[1], dom.TEXT_TYPE)

    def test_tuple_single_element(self):
        """tuple[int] -> StructType with one positional field."""
        result = _python_to_axis_type(tuple[int])
        self.assertIsInstance(result, dom.StructType)
        self.assertEqual(result.fields.arity, 1)
        self.assertIs(result.fields[0], dom.INTEGER_TYPE)

    def test_tuple_triple(self):
        """tuple[int, str, bool] -> StructType with three fields."""
        result = _python_to_axis_type(tuple[int, str, bool])
        self.assertIsInstance(result, dom.StructType)
        self.assertEqual(result.fields.arity, 3)
        self.assertIs(result.fields[0], dom.INTEGER_TYPE)
        self.assertIs(result.fields[1], dom.TEXT_TYPE)
        self.assertIs(result.fields[2], dom.BOOLEAN_TYPE)

    # -- frozenset / set --

    def test_frozenset(self):
        """frozenset[str] -> std.Set str"""
        result = _python_to_axis_type(frozenset[str])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Set")
        self.assertIs(result.underlying, dom.TEXT_TYPE)

    def test_set(self):
        """set[int] -> std.Set int"""
        result = _python_to_axis_type(set[int])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Set")
        self.assertIs(result.underlying, dom.INTEGER_TYPE)

    # -- frozendict --

    def test_frozendict(self):
        """frozendict[str, int] -> std.Map int (keyed by str)"""
        result = _python_to_axis_type(frozendict[str, int])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Map")
        self.assertIs(result.underlying, dom.INTEGER_TYPE)

    # -- Struct --

    def test_struct_generic(self):
        """Struct[str, Type] -> Struct qualifier with underlying=ANY (for Type)"""
        result = _python_to_axis_type(dom.Struct[str, dom.Type])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "Struct")


class TestPyToAxisComplex(unittest.TestCase):
    """Nested and composed generic types are recursively projected."""

    def test_tuple_variadic_of_union(self):
        """tuple[int | str, ...] -> std.List (int | str)"""
        result = _python_to_axis_type(tuple[int | str, ...])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.List")
        self.assertIsInstance(result.underlying, dom.UnionType)
        self.assertEqual(
            result.underlying.types,
            frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE}),
        )

    def test_frozenset_of_union(self):
        """frozenset[int | None] -> std.Set (int | None)"""
        result = _python_to_axis_type(frozenset[int | None])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Set")
        self.assertIsInstance(result.underlying, dom.UnionType)
        self.assertEqual(
            result.underlying.types,
            frozenset({dom.INTEGER_TYPE, dom.EMPTY_TYPE}),
        )

    def test_frozendict_of_nested_set(self):
        """frozendict[str, frozenset[int]] -> std.Map (std.Set int)"""
        result = _python_to_axis_type(frozendict[str, frozenset[int]])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Map")
        inner = result.underlying
        self.assertIsInstance(inner, dom.NominalQualifier)
        self.assertEqual(_anchor_path(inner), "std.Set")
        self.assertIs(inner.underlying, dom.INTEGER_TYPE)

    def test_tuple_fixed_with_nested_generics(self):
        """tuple[frozenset[int], frozendict[str, bool]] -> StructType with nested types."""
        result = _python_to_axis_type(tuple[frozenset[int], frozendict[str, bool]])
        self.assertIsInstance(result, dom.StructType)
        self.assertEqual(result.fields.arity, 2)

        f0 = result.fields[0]
        self.assertIsInstance(f0, dom.NominalQualifier)
        self.assertEqual(_anchor_path(f0), "std.Set")
        self.assertIs(f0.underlying, dom.INTEGER_TYPE)

        f1 = result.fields[1]
        self.assertIsInstance(f1, dom.NominalQualifier)
        self.assertEqual(_anchor_path(f1), "std.Map")
        self.assertIs(f1.underlying, dom.BOOLEAN_TYPE)

    def test_union_of_generic_types(self):
        """Union[frozenset[int], tuple[str, ...]] -> UnionType of (std.Set int, std.List str)"""
        result = _python_to_axis_type(Union[frozenset[int], tuple[str, ...]])
        self.assertIsInstance(result, dom.UnionType)
        self.assertEqual(len(result.types), 2)

        # Decompose the union members
        types_by_class = {}
        for t in result.types:
            types_by_class[type(t).__name__] = t

        set_type = types_by_class["NominalQualifier"]
        # One should be std.Set, the other std.List — identify by anchor
        anchors = {_anchor_path(t) for t in result.types}
        self.assertEqual(anchors, {"std.Set", "std.List"})

    def test_triple_nesting(self):
        """frozendict[str, frozendict[str, frozenset[int]]] -> three levels deep."""
        result = _python_to_axis_type(frozendict[str, frozendict[str, frozenset[int]]])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Map")

        mid = result.underlying
        self.assertIsInstance(mid, dom.NominalQualifier)
        self.assertEqual(_anchor_path(mid), "std.Map")

        inner = mid.underlying
        self.assertIsInstance(inner, dom.NominalQualifier)
        self.assertEqual(_anchor_path(inner), "std.Set")
        self.assertIs(inner.underlying, dom.INTEGER_TYPE)

    def test_tuple_variadic_of_tuple_fixed(self):
        """tuple[tuple[int, str], ...] -> std.List (StructType(int, str))"""
        result = _python_to_axis_type(tuple[tuple[int, str], ...])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.List")
        self.assertIsInstance(result.underlying, dom.StructType)
        self.assertEqual(result.underlying.fields.arity, 2)
        self.assertIs(result.underlying.fields[0], dom.INTEGER_TYPE)
        self.assertIs(result.underlying.fields[1], dom.TEXT_TYPE)

    def test_pep604_union_of_generics(self):
        """frozenset[int] | tuple[str, ...] via PEP 604."""
        result = _python_to_axis_type(frozenset[int] | tuple[str, ...])
        self.assertIsInstance(result, dom.UnionType)
        anchors = {_anchor_path(t) for t in result.types}
        self.assertEqual(anchors, {"std.Set", "std.List"})

    def test_set_of_tuple_variadic(self):
        """set[tuple[int, ...]] is not directly expressible as a Python type,
        but set[int] | frozenset[str] tests mixed set transforms."""
        result = _python_to_axis_type(set[int] | frozenset[str])
        self.assertIsInstance(result, dom.UnionType)
        for t in result.types:
            self.assertIsInstance(t, dom.NominalQualifier)
            self.assertEqual(_anchor_path(t), "std.Set")


class TestPyToAxisEdgeCases(unittest.TestCase):
    """Edge cases: unregistered origins, TypeVar, non-type annotations."""

    def test_unregistered_generic_fallback(self):
        """list[int] has no registered transform -> ANY_TYPE."""
        result = _python_to_axis_type(list[int])
        self.assertIs(result, dom.ANY_TYPE)

    def test_dict_fallback(self):
        """dict[str, int] has no registered transform -> ANY_TYPE."""
        result = _python_to_axis_type(dict[str, int])
        self.assertIs(result, dom.ANY_TYPE)

    def test_bare_tuple_no_args(self):
        """Plain `tuple` (no parameters) has origin=None, treated as a class."""
        result = _python_to_axis_type(tuple)
        # tuple itself is a type, falls through to _try_builtin_mapping
        # which won't find a Builtin named 'tuple', so ANY_TYPE
        self.assertIs(result, dom.ANY_TYPE)

    def test_bare_int_is_scalar(self):
        """Bare `int` is identity-matched, not via Builtin registry."""
        self.assertIs(_python_to_axis_type(int), dom.INTEGER_TYPE)

    def test_any_annotation(self):
        """typing.Any is not a type class — fallback."""
        from typing import Any
        result = _python_to_axis_type(Any)
        # Any has no origin, is not a type class — fallback
        self.assertIs(result, dom.ANY_TYPE)

    def test_none_literal(self):
        """NoneType (type(None)) maps to EMPTY_TYPE."""
        self.assertIs(_python_to_axis_type(type(None)), dom.EMPTY_TYPE)

    def test_ellipsis_in_non_tuple_context(self):
        """Ellipsis on its own is not a recognized type."""
        result = _python_to_axis_type(...)
        self.assertIs(result, dom.ANY_TYPE)


class TestRegisterPyToAx(unittest.TestCase):
    """register_py_to_ax allows extending and overriding transforms."""

    def setUp(self):
        """Snapshot the registry to restore after each test."""
        self._snapshot = dict(_PY_TO_AX_TRANSFORMS)

    def tearDown(self):
        """Restore the original registry."""
        _PY_TO_AX_TRANSFORMS.clear()
        _PY_TO_AX_TRANSFORMS.update(self._snapshot)

    def test_register_new_origin(self):
        """Register a previously unhandled origin (list)."""
        register_py_to_ax(
            list,
            lambda V: dom._nominal_qual('std.List', None, underlying=V),
        )
        result = _python_to_axis_type(list[int])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.List")
        self.assertIs(result.underlying, dom.INTEGER_TYPE)

    def test_register_dict(self):
        """Register dict as a std.Map analog."""
        register_py_to_ax(
            dict,
            lambda K, V: dom._nominal_qual('std.Map', None, underlying=V),
        )
        result = _python_to_axis_type(dict[str, int])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Map")
        self.assertIs(result.underlying, dom.INTEGER_TYPE)

    def test_override_existing_transform(self):
        """Overriding an existing transform replaces the old one."""
        # frozenset currently maps to std.Set
        original = _python_to_axis_type(frozenset[int])
        self.assertEqual(_anchor_path(original), "std.Set")

        # Override to map frozenset to std.List instead
        register_py_to_ax(
            frozenset,
            lambda V: dom._nominal_qual('std.List', None, underlying=V),
        )
        overridden = _python_to_axis_type(frozenset[int])
        self.assertEqual(_anchor_path(overridden), "std.List")
        self.assertIs(overridden.underlying, dom.INTEGER_TYPE)

    def test_transform_receives_converted_args(self):
        """Transform callback receives dom.Types, not raw Python types."""
        received_args = []

        def capture_transform(*args):
            received_args.extend(args)
            return dom.ANY_TYPE

        register_py_to_ax(list, capture_transform)
        _python_to_axis_type(list[int])

        self.assertEqual(len(received_args), 1)
        self.assertIs(received_args[0], dom.INTEGER_TYPE)

    def test_transform_receives_ellipsis_unchanged(self):
        """Ellipsis is not converted — passed through as-is."""
        received_args = []

        def capture_transform(*args):
            received_args.extend(args)
            return dom.ANY_TYPE

        # Override tuple to capture what it receives
        register_py_to_ax(tuple, capture_transform)
        _python_to_axis_type(tuple[int, ...])

        self.assertEqual(len(received_args), 2)
        self.assertIs(received_args[0], dom.INTEGER_TYPE)
        self.assertIs(received_args[1], ...)

    def test_nested_generics_recurse_through_new_registration(self):
        """A newly registered list transform is picked up inside nested types."""
        register_py_to_ax(
            list,
            lambda V: dom._nominal_qual('std.List', None, underlying=V),
        )
        # frozenset[list[int]] -> std.Set (std.List int)
        result = _python_to_axis_type(frozenset[list[int]])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Set")

        inner = result.underlying
        self.assertIsInstance(inner, dom.NominalQualifier)
        self.assertEqual(_anchor_path(inner), "std.List")
        self.assertIs(inner.underlying, dom.INTEGER_TYPE)

    def test_custom_struct_projection(self):
        """Example from the design doc: custom Struct transform with spec."""
        register_py_to_ax(
            dom.Struct,
            lambda K, V: dom._nominal_qual(
                'std.Struct',
                None,
                underlying=V,
            ),
        )
        result = _python_to_axis_type(dom.Struct[str, dom.Type])
        self.assertIsInstance(result, dom.NominalQualifier)
        self.assertEqual(_anchor_path(result), "std.Struct")


def _field_type(struct: dom.Struct[str, dom.Type], key: str) -> dom.Type:
    offset = struct.index.get(key)
    if offset is None:
        raise AssertionError(f"Struct has no key {key!r}")
    return struct[offset]


# Generic test class for TestNativeIntrospectorGenerics
T_Generic = TypeVar("T_Generic")

class GenericBuiltin(dom.Builtin, Generic[T_Generic]):
    """Generic builtin class for testing introspector substitution."""
    ANCHOR = "test.GenericBuiltin"
    value: T_Generic


class TestNativeIntrospectorGenerics(unittest.TestCase):
    """NativeIntrospector substitutes VarGenericType placeholders using spec_ref."""

    def test_substitutes_placeholder_from_spec(self):
        spec = dom._struct(T_Generic=dom.INTEGER_TYPE.as_val)
        nominal = dom._nominal_type("test.GenericBuiltin", spec)

        introspector = dom.INTROSPECTOR.get()
        self.assertIsNotNone(introspector)

        fields = introspector.fields(nominal)
        self.assertIsNotNone(fields)
        self.assertIs(_field_type(fields, "value"), dom.INTEGER_TYPE)

    def test_placeholder_without_spec_defaults_to_any(self):
        nominal = dom._nominal_type("test.GenericBuiltin")
        introspector = dom.INTROSPECTOR.get()
        fields = introspector.fields(nominal)
        self.assertIsNotNone(fields)
        self.assertIs(_field_type(fields, "value"), dom.ANY_TYPE)


class TestGenericIntrospectionComprehensive(unittest.TestCase):
    """Comprehensive tests for generic type introspection with Python generics."""

    def setUp(self):
        """Create generic test classes for introspection."""
        # Define TypeVars
        self.T = TypeVar("T")
        self.K = TypeVar("K")
        self.V = TypeVar("V")
        
        # Basic generic with variadic tuple
        class TestGeneric(dom.Builtin, Generic[self.T]):
            ANCHOR = "test.TestGeneric"
            tuple_t: tuple[self.T, ...]
        
        self.TestGeneric = TestGeneric
        
        # Multi-parameter generic
        class TestMap(dom.Builtin, Generic[self.K, self.V]):
            ANCHOR = "test.TestMap"
            keys: frozenset[self.K]
            values: tuple[self.V, ...]
            mapping: frozendict[self.K, self.V]
        
        self.TestMap = TestMap
        
        # Nested generics
        class TestNested(dom.Builtin, Generic[self.T]):
            ANCHOR = "test.TestNested"
            lists: tuple[frozenset[self.T], ...]
            optional_t: self.T | None
            struct_t: dom.Struct[str, self.T]
        
        self.TestNested = TestNested
        
        # Mixed concrete and generic
        class TestMixed(dom.Builtin, Generic[self.T]):
            ANCHOR = "test.TestMixed"
            concrete_int: int
            generic_t: self.T
            tuple_mixed: tuple[int, self.T, str]
            generic_list: tuple[self.T, ...]
        
        self.TestMixed = TestMixed
        
        # Ensure classes are drained
        dom.introspect._drain_pending()
        
        self.introspector = dom.INTROSPECTOR.get()

    def test_basic_generic_variadic_tuple(self):
        """Test TestGeneric[int] with tuple[T, ...] field."""
        # Create specialized type
        spec = dom._struct(T=dom.INTEGER_TYPE.as_val)
        nominal = dom._nominal_type("test.TestGeneric", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # Check tuple_t field
        tuple_t = _field_type(fields, "tuple_t")
        self.assertIsInstance(tuple_t, dom.NominalQualifier)
        self.assertEqual(_anchor_path(tuple_t), "std.List")
        self.assertIs(tuple_t.underlying, dom.INTEGER_TYPE)

    def test_multi_parameter_generic(self):
        """Test TestMap[str, int] with multiple type parameters."""
        # Create specialized type
        spec = dom._struct(
            K=dom.TEXT_TYPE.as_val,
            V=dom.INTEGER_TYPE.as_val
        )
        nominal = dom._nominal_type("test.TestMap", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # Check keys field
        keys = _field_type(fields, "keys")
        self.assertIsInstance(keys, dom.NominalQualifier)
        self.assertEqual(_anchor_path(keys), "std.Set")
        self.assertIs(keys.underlying, dom.TEXT_TYPE)
        
        # Check values field
        values = _field_type(fields, "values")
        self.assertIsInstance(values, dom.NominalQualifier)
        self.assertEqual(_anchor_path(values), "std.List")
        self.assertIs(values.underlying, dom.INTEGER_TYPE)
        
        # Check mapping field
        mapping = _field_type(fields, "mapping")
        self.assertIsInstance(mapping, dom.NominalQualifier)
        self.assertEqual(_anchor_path(mapping), "std.Map")
        self.assertIs(mapping.underlying, dom.INTEGER_TYPE)

    def test_nested_generics(self):
        """Test TestNested[bool] with nested generic structures."""
        # Create specialized type
        spec = dom._struct(T=dom.BOOLEAN_TYPE.as_val)
        nominal = dom._nominal_type("test.TestNested", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # Check lists field: tuple[frozenset[T], ...]
        lists = _field_type(fields, "lists")
        self.assertIsInstance(lists, dom.NominalQualifier)
        self.assertEqual(_anchor_path(lists), "std.List")
        
        # Inner type should be frozenset[bool] -> std.Set bool
        inner = lists.underlying
        self.assertIsInstance(inner, dom.NominalQualifier)
        self.assertEqual(_anchor_path(inner), "std.Set")
        self.assertIs(inner.underlying, dom.BOOLEAN_TYPE)
        
        # Check optional_t field: T | None
        optional_t = _field_type(fields, "optional_t")
        self.assertIsInstance(optional_t, dom.UnionType)
        self.assertEqual(
            optional_t.types,
            frozenset({dom.BOOLEAN_TYPE, dom.EMPTY_TYPE})
        )
        
        # Check struct_t field: Struct[str, T]
        struct_t = _field_type(fields, "struct_t")
        self.assertIsInstance(struct_t, dom.NominalQualifier)
        self.assertEqual(_anchor_path(struct_t), "Struct")

    def test_mixed_concrete_and_generic(self):
        """Test TestMixed[float] with both concrete and generic fields."""
        # Create specialized type
        spec = dom._struct(T=dom.DECIMAL_TYPE.as_val)
        nominal = dom._nominal_type("test.TestMixed", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # Check concrete field is unchanged
        concrete_int = _field_type(fields, "concrete_int")
        self.assertIs(concrete_int, dom.INTEGER_TYPE)
        
        # Check generic field is substituted
        generic_t = _field_type(fields, "generic_t")
        self.assertIs(generic_t, dom.DECIMAL_TYPE)
        
        # Check tuple_mixed: tuple[int, T, str]
        tuple_mixed = _field_type(fields, "tuple_mixed")
        self.assertIsInstance(tuple_mixed, dom.StructType)
        self.assertEqual(tuple_mixed.fields.arity, 3)
        self.assertIs(tuple_mixed.fields[0], dom.INTEGER_TYPE)
        self.assertIs(tuple_mixed.fields[1], dom.DECIMAL_TYPE)
        self.assertIs(tuple_mixed.fields[2], dom.TEXT_TYPE)
        
        # Check generic_list: tuple[T, ...]
        generic_list = _field_type(fields, "generic_list")
        self.assertIsInstance(generic_list, dom.NominalQualifier)
        self.assertEqual(_anchor_path(generic_list), "std.List")
        self.assertIs(generic_list.underlying, dom.DECIMAL_TYPE)

    def test_unspecialized_generic_defaults_to_any(self):
        """Test that unspecialized generics default to ANY_TYPE."""
        # Create nominal without spec
        nominal = dom._nominal_type("test.TestGeneric")
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # Check tuple_t field defaults to tuple[Any, ...]
        tuple_t = _field_type(fields, "tuple_t")
        self.assertIsInstance(tuple_t, dom.NominalQualifier)
        self.assertEqual(_anchor_path(tuple_t), "std.List")
        self.assertIs(tuple_t.underlying, dom.ANY_TYPE)

    def test_partial_specialization(self):
        """Test partial specialization (some params unbound)."""
        # Only specify K, not V
        spec = dom._struct(K=dom.TEXT_TYPE.as_val)
        nominal = dom._nominal_type("test.TestMap", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        self.assertIsNotNone(fields)
        
        # K should be str
        keys = _field_type(fields, "keys")
        self.assertIsInstance(keys, dom.NominalQualifier)
        self.assertEqual(_anchor_path(keys), "std.Set")
        self.assertIs(keys.underlying, dom.TEXT_TYPE)
        
        # V should default to ANY
        values = _field_type(fields, "values")
        self.assertIsInstance(values, dom.NominalQualifier)
        self.assertEqual(_anchor_path(values), "std.List")
        self.assertIs(values.underlying, dom.ANY_TYPE)

    def test_caching_by_spec(self):
        """Test that specialized types are cached by spec."""
        # Create two nominals with same spec
        spec = dom._struct(T=dom.INTEGER_TYPE.as_val)
        nominal1 = dom._nominal_type("test.TestGeneric", spec)
        nominal2 = dom._nominal_type("test.TestGeneric", spec)
        
        # Get fields twice
        fields1 = self.introspector.fields(nominal1)
        fields2 = self.introspector.fields(nominal2)
        
        # Should be same cached result
        self.assertIs(fields1, fields2)

    def test_different_specs_produce_different_fields(self):
        """Test that different specs produce different field structures."""
        # Create two nominals with different specs
        spec_int = dom._struct(T=dom.INTEGER_TYPE.as_val)
        spec_str = dom._struct(T=dom.TEXT_TYPE.as_val)
        
        nominal_int = dom._nominal_type("test.TestGeneric", spec_int)
        nominal_str = dom._nominal_type("test.TestGeneric", spec_str)
        
        # Get fields
        fields_int = self.introspector.fields(nominal_int)
        fields_str = self.introspector.fields(nominal_str)
        
        # Should be different objects
        self.assertIsNot(fields_int, fields_str)
        
        # But with different underlying types
        tuple_int = _field_type(fields_int, "tuple_t")
        tuple_str = _field_type(fields_str, "tuple_t")
        
        self.assertIs(tuple_int.underlying, dom.INTEGER_TYPE)
        self.assertIs(tuple_str.underlying, dom.TEXT_TYPE)

    def test_complex_nested_substitution(self):
        """Test complex nested generic substitution scenarios."""
        # Create a class with deeply nested generics
        class TestComplex(dom.Builtin, Generic[self.T]):
            ANCHOR = "test.TestComplex"
            # frozendict[str, tuple[frozenset[T], ...]]
            complex_field: frozendict[str, tuple[frozenset[self.T], ...]]
        
        # Drain pending
        dom.introspect._drain_pending()
        
        # Create specialized type
        spec = dom._struct(T=dom.INTEGER_TYPE.as_val)
        nominal = dom._nominal_type("test.TestComplex", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        complex_field = _field_type(fields, "complex_field")
        
        # Should be std.Map
        self.assertIsInstance(complex_field, dom.NominalQualifier)
        self.assertEqual(_anchor_path(complex_field), "std.Map")
        
        # Underlying should be tuple[frozenset[int], ...] -> std.List (std.Set int)
        tuple_type = complex_field.underlying
        self.assertIsInstance(tuple_type, dom.NominalQualifier)
        self.assertEqual(_anchor_path(tuple_type), "std.List")
        
        # Inner should be frozenset[int] -> std.Set int
        set_type = tuple_type.underlying
        self.assertIsInstance(set_type, dom.NominalQualifier)
        self.assertEqual(_anchor_path(set_type), "std.Set")
        self.assertIs(set_type.underlying, dom.INTEGER_TYPE)

    def test_union_with_generic_parameter(self):
        """Test union types involving generic parameters."""
        class TestUnion(dom.Builtin, Generic[self.T]):
            ANCHOR = "test.TestUnion"
            union_field: self.T | int | None
            optional_union: tuple[self.T | str, ...] | None
        
        # Drain pending
        dom.introspect._drain_pending()
        
        # Create specialized type
        spec = dom._struct(T=dom.BOOLEAN_TYPE.as_val)
        nominal = dom._nominal_type("test.TestUnion", spec)
        
        # Get fields
        fields = self.introspector.fields(nominal)
        
        # Check union_field: bool | int | None
        union_field = _field_type(fields, "union_field")
        self.assertIsInstance(union_field, dom.UnionType)
        self.assertEqual(
            union_field.types,
            frozenset({dom.BOOLEAN_TYPE, dom.INTEGER_TYPE, dom.EMPTY_TYPE})
        )
        
        # Check optional_union: tuple[bool | str, ...] | None
        optional_union = _field_type(fields, "optional_union")
        self.assertIsInstance(optional_union, dom.UnionType)
        
        # Find the tuple type in the union
        tuple_type = None
        for t in optional_union.types:
            if isinstance(t, dom.NominalQualifier) and _anchor_path(t) == "std.List":
                tuple_type = t
                break
        
        self.assertIsNotNone(tuple_type)
        # Inner should be bool | str
        inner_union = tuple_type.underlying
        self.assertIsInstance(inner_union, dom.UnionType)
        self.assertEqual(
            inner_union.types,
            frozenset({dom.BOOLEAN_TYPE, dom.TEXT_TYPE})
        )


if __name__ == "__main__":
    unittest.main()
