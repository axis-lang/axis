"""Comprehensive tests for the axis domain model (dom/).

Tests the cremallera (zipper) pattern: every Pure is (type, data),
where type describes how to interpret data. Types are also values
(self-descriptive via __type__/__data__).
"""
import unittest
from decimal import Decimal

from axis import dom


class _Contrib(dom.ContributionBase):
    """Concrete ContributionBase for testing."""
    pass


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
        self.contrib = _Contrib(anchor=self.anchor)
        self.K = dom.Var.spec("K", self.contrib)
        self.V = dom.Var.spec("V", self.contrib)

    def test_new_struct_positional(self):
        result = dom.Const.new_struct(self.K, self.V)
        self.assertIsInstance(result.type, dom.StructType)
        # data side: variable names
        self.assertEqual(result.data, ("K", "V"))
        # type side: distinct VarSpecTypes
        self.assertNotEqual(result.type.fields[0], result.type.fields[1])
        self.assertIsInstance(result.type.fields[0], dom.VarSpecType)
        self.assertIsInstance(result.type.fields[1], dom.VarSpecType)

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
        self.assertIsInstance(result.type.fields[1], dom.VarSpecType)


# ---------------------------------------------------------------------------
# NominalType
# ---------------------------------------------------------------------------

class TestNominalType(unittest.TestCase):
    def test_from_str(self):
        nt = dom.NominalType.from_str("std.Text")
        self.assertIsInstance(nt, dom.NominalType)
        self.assertEqual(dom.ref_segments(nt.spec_ref), ("std", "Text"))

    def test_from_ref(self):
        ref = dom.Anchor.from_str("std.Array")
        nt = dom.NominalType.from_ref(ref)
        self.assertIsInstance(nt, dom.NominalType)
        self.assertEqual(dom.ref_segments(nt.spec_ref), ("std", "Array"))

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
# Qualifier (cremallera: type = NominalQualifier, data = (underlying, ref_spec))
# ---------------------------------------------------------------------------

class TestQualifier(unittest.TestCase):
    def setUp(self):
        self.anchor = dom.Anchor.from_str("test.foo")
        self.contrib = _Contrib(anchor=self.anchor)
        self.K = dom.Var.spec("K", self.contrib)
        self.V = dom.Var.spec("V", self.contrib)

    def test_new_qual_simple(self):
        """Mapping[K] V — single qualifier."""
        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(self.K)
        )
        result = dom.Const.new_qual(ref_spec=mapping_spec, underlying=self.V)

        self.assertIsInstance(result.type, dom.NominalQualifier)
        self.assertIsInstance(result.type.ref_spec, dom.SpecType)
        self.assertEqual(result.type.underlying, self.V.type)
        # data side: (underlying.data, ref_spec.data)
        self.assertEqual(result.data[0], "V")
        self.assertEqual(result.data[1], (("std", "Mapping"), ("K",)))

    def test_new_qual_chained(self):
        """Array[2,2] Mapping[K] V — chained qualifiers (nested cremallera)."""
        two = dom.Const.new_literal(2)

        # inner: Mapping[K] V
        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(self.K)
        )
        inner = dom.Const.new_qual(ref_spec=mapping_spec, underlying=self.V)

        # outer: Array[2,2] (Mapping[K] V)
        array_spec = dom.Anchor.from_str("std.Array").specialize(
            dom.Const.new_struct(two, two)
        )
        outer = dom.Const.new_qual(ref_spec=array_spec, underlying=inner)

        # type side: nested NominalQualifiers
        self.assertIsInstance(outer.type, dom.NominalQualifier)
        self.assertIsInstance(outer.type.underlying, dom.NominalQualifier)
        self.assertEqual(outer.type.underlying.underlying, self.V.type)

        # data side
        inner_data = outer.data[0]
        array_data = outer.data[1]
        self.assertEqual(inner_data, ("V", (("std", "Mapping"), ("K",))))
        self.assertEqual(array_data, (("std", "Array"), (2, 2)))


# ---------------------------------------------------------------------------
# Var types — name distinguishability
# ---------------------------------------------------------------------------

class TestVarType(unittest.TestCase):
    def setUp(self):
        self.anchor = dom.Anchor.from_str("test.foo")
        self.contrib = _Contrib(anchor=self.anchor)

    def test_subclass_relationships(self):
        self.assertTrue(issubclass(dom.VarSpecType, dom.VarType))
        self.assertTrue(issubclass(dom.VarParamType, dom.VarType))
        self.assertTrue(issubclass(dom.VarType, dom.Type))

    def test_spec_vars_distinguishable(self):
        """K and V from same contribution must be distinct types."""
        K = dom.Var.spec("K", self.contrib)
        V = dom.Var.spec("V", self.contrib)
        self.assertNotEqual(K.type, V.type)
        self.assertEqual(K.type.name, "K")
        self.assertEqual(V.type.name, "V")

    def test_param_vars_distinguishable(self):
        """Param variables also distinguishable."""
        a = dom.Var.param("a", self.contrib)
        b = dom.Var.param("b", self.contrib)
        self.assertNotEqual(a.type, b.type)
        self.assertEqual(a.type.name, "a")
        self.assertEqual(b.type.name, "b")

    def test_spec_vs_param_distinct(self):
        """Spec and param vars with same name are distinct types."""
        K_spec = dom.Var.spec("K", self.contrib)
        K_param = dom.Var.param("K", self.contrib)
        self.assertNotEqual(K_spec.type, K_param.type)
        self.assertIsInstance(K_spec.type, dom.VarSpecType)
        self.assertIsInstance(K_param.type, dom.VarParamType)

    def test_union_with_type_vars_no_collapse(self):
        """Union of two distinct type vars should have 2 members."""
        K = dom.Var.spec("K", self.contrib)
        V = dom.Var.spec("V", self.contrib)
        union = dom.UnionType(types=frozenset({K.type, V.type}))
        self.assertEqual(len(union.types), 2)


# ---------------------------------------------------------------------------
# Union: flattening, factory, cremallera
# ---------------------------------------------------------------------------

class TestUnion(unittest.TestCase):

    # --- __invariants__: direct UnionType must be flat ---

    def test_invariants_rejects_nested(self):
        """Direct UnionType() with nested UnionType violates __invariants__."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        # Direct construction with a nested UnionType is allowed by Consed,
        # but __invariants__ catches it.
        nested = dom.UnionType(types=frozenset({ab, C}))
        with self.assertRaises(TypeError):
            nested.__invariants__()

    def test_invariants_accepts_flat(self):
        """Flat UnionType passes __invariants__."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
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
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        abc = dom._union_type(ab, C)
        self.assertEqual(len(abc.types), 3)
        self.assertEqual(abc.types, frozenset({A, B, C}))

    def test_union_type_flatten_deeply_nested(self):
        """_union_type flattens ((A|B)|C, D) → {A, B, C, D}."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
        D = dom.NominalType.from_str("D")
        ab = dom.UnionType(types=frozenset({A, B}))
        # ab is flat, use _union_type for the rest
        abc = dom._union_type(ab, C)
        abcd = dom._union_type(abc, D)
        self.assertEqual(len(abcd.types), 4)
        self.assertEqual(abcd.types, frozenset({A, B, C, D}))

    def test_union_type_flatten_both_sides(self):
        """_union_type(A|B, C|D) flattens to {A, B, C, D}."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
        D = dom.NominalType.from_str("D")
        ab = dom.UnionType(types=frozenset({A, B}))
        cd = dom.UnionType(types=frozenset({C, D}))
        abcd = dom._union_type(ab, cd)
        self.assertEqual(len(abcd.types), 4)

    def test_union_type_no_op_when_flat(self):
        """_union_type on already-flat types is a no-op."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        union = dom._union_type(A, B)
        self.assertEqual(len(union.types), 2)

    def test_union_type_deduplicates(self):
        """_union_type(A|B, A) deduplicates to {A, B}."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        ab = dom.UnionType(types=frozenset({A, B}))
        aba = dom._union_type(ab, A)
        self.assertEqual(len(aba.types), 2)
        self.assertEqual(aba.types, frozenset({A, B}))

    def test_union_type_result_passes_invariants(self):
        """_union_type always produces a flat result."""
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
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
        A = dom.NominalType.from_str("A")
        B = dom.NominalType.from_str("B")
        C = dom.NominalType.from_str("C")
        ab = dom.UnionType(types=frozenset({A, B}))
        val = dom.Const(type=A, data=None)
        # Pass frozenset containing a UnionType — _union should flatten
        union = dom._union(frozenset({ab, C}), val)
        self.assertEqual(len(union.type.types), 3)
        self.assertEqual(union.type.types, frozenset({A, B, C}))

    # --- _dir / _get ---

    def test_dir_union(self):
        """Union values expose discriminator and value."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        self.assertEqual(dom._dir(union), ('discriminator', 'value'))

    def test_get_union_discriminator(self):
        """_get(union, 'discriminator') returns the active type as a value."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        disc = dom._get(union, 'discriminator')
        self.assertIsInstance(disc, dom.Const)
        self.assertIs(disc.data, dom.INTEGER_TYPE)

    def test_get_union_value(self):
        """_get(union, 'value') returns the active variant."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        val = dom._get(union, 'value')
        self.assertIsInstance(val, dom.Const)
        self.assertEqual(val.data, 42)
        self.assertIs(val.type, dom.INTEGER_TYPE)

    def test_get_union_invalid_key(self):
        """_get on union with invalid key raises KeyError."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        with self.assertRaises(KeyError):
            dom._get(union, 'nonexistent')

    def test_union_with_var_types(self):
        """Union over type variables with one active."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)
        types = frozenset({K.type, V.type})
        # Active variant is K
        union = dom._union(types, K)
        self.assertIs(union.data[0], K.type)
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
        ref_type = dom.SpecType(anchor=dom.AnchorType(), spec=None)
        qual = dom.NominalQualifier(ref_spec=ref_type, underlying=dom.TEXT_TYPE)
        val = qual.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertIsInstance(val.type, dom.NominalType)
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
            ("dom", "Type", "Qual", "Nominal"),
        )

    def test_var_spec_type_as_val(self):
        """VarSpecType.as_val should work."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        vt = dom.VarSpecType(contribution=contrib, name="K")
        val = vt.as_val
        self.assertIsInstance(val, dom.Const)
        self.assertEqual(
            dom.ref_segments(val.type.spec_ref),
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
# _dir / _get: cremallera decomposition
# ---------------------------------------------------------------------------

class TestDirGet(unittest.TestCase):
    def test_dir_struct_positional(self):
        val = dom._literal_struct(1, 2, 3)
        keys = dom._dir(val)
        self.assertEqual(keys, (0, 1, 2))

    def test_dir_struct_named(self):
        val = dom._literal_struct(x=1, y=2)
        keys = dom._dir(val)
        self.assertEqual(keys, ("x", "y"))

    def test_dir_struct_mixed(self):
        """Positional fields get int keys, named fields get str keys."""
        val = dom._literal_struct(1, x=2)
        keys = dom._dir(val)
        self.assertEqual(keys, (0, "x"))

    def test_get_struct_by_name(self):
        val = dom._literal_struct(x=42, y="hello")
        x = dom._get(val, "x")
        self.assertIsInstance(x, dom.Const)
        self.assertEqual(x.data, 42)
        self.assertEqual(x.type, dom.INTEGER_TYPE)

    def test_get_struct_by_index(self):
        val = dom._literal_struct(1, 2, 3)
        second = dom._get(val, 1)
        self.assertEqual(second.data, 2)

    def test_get_qualifier(self):
        """_get on NominalQualifier returns empty sentinel (disabled)."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)
        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(K)
        )
        qual = dom.Const.new_qual(ref_spec=mapping_spec, underlying=V)

        # Qualifier _get always returns the empty sentinel
        result = dom._get(qual, "underlying")
        self.assertIsInstance(result, dom.Const)
        self.assertEqual(result.type, dom.EMPTY_TYPE)
        self.assertIsNone(result.data)

    def test_dir_qualifier(self):
        """Qualifier _dir is disabled — returns empty tuple."""
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.Var.spec("K", contrib)
        V = dom.Var.spec("V", contrib)
        mapping_spec = dom.Anchor.from_str("std.Mapping").specialize(
            dom.Const.new_struct(K)
        )
        qual = dom.Const.new_qual(ref_spec=mapping_spec, underlying=V)
        self.assertEqual(dom._dir(qual), ())

    def test_dir_nominal_empty(self):
        """NominalType values have no introspectable members (opaque)."""
        val = dom.Const.new_literal(42)
        self.assertEqual(dom._dir(val), ())

    def test_get_nonexistent_raises(self):
        val = dom._literal_struct(x=1)
        with self.assertRaises(KeyError):
            dom._get(val, "nonexistent")

    def test_get_non_pure_raises(self):
        err = dom.Err()
        with self.assertRaises(TypeError):
            dom._get(err, "x")


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
        encoded = union.encode
        self.assertIs(encoded.type, union.type)

    def test_encode_data_is_raw(self):
        """After encode, data contains no Builtins."""
        int_val = dom.Const.new_literal(42)
        types = frozenset({dom.INTEGER_TYPE, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, int_val)
        encoded = union.encode
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
        encoded = union.encode
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
        encoded = union.encode
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
        """KNOWN ISSUE: VarSpecType and VarParamType with the same name
        and contribution encode to identical raw data.

        _encode strips class identity — it only sees attrs. Both classes
        have {contribution, name}, so the encoded tuples are equal.

        This means: for a union of VarSpecType("K") | VarParamType("K"),
        the encoded discriminator is ambiguous.
        """
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K_spec = dom.VarSpecType(contribution=contrib, name="K")
        K_param = dom.VarParamType(contribution=contrib, name="K")

        enc_spec = dom._encode(K_spec)
        enc_param = dom._encode(K_param)

        # COLLISION: same attrs → same encoded form
        self.assertEqual(enc_spec, enc_param)

        # The types themselves ARE different (different classes)
        self.assertNotEqual(K_spec, K_param)

        # In a union containing both, encode makes the discriminator ambiguous
        union = dom.Const.new_union(
            frozenset({K_spec, K_param}),
            dom.Const(type=K_spec, data="K"),
        )
        encoded = union.encode
        enc_disc = encoded.data[0]

        ambiguous = [
            t for t in encoded.type.types
            if dom._encode(t) == enc_disc
        ]
        # Two matches — ambiguous!
        self.assertEqual(len(ambiguous), 2)

    def test_encode_no_collision_different_names(self):
        """VarSpecType("K") vs VarSpecType("V") have different names,
        so they encode to different raw data — no collision.
        """
        anchor = dom.Anchor.from_str("test.foo")
        contrib = _Contrib(anchor=anchor)
        K = dom.VarSpecType(contribution=contrib, name="K")
        V = dom.VarSpecType(contribution=contrib, name="V")
        self.assertNotEqual(dom._encode(K), dom._encode(V))

    def test_encode_struct_variant_preserves_data(self):
        """Encoding a union whose active variant is a struct
        recursively encodes the struct data.
        """
        struct_val = dom._literal_struct(x=1, y="hi")
        types = frozenset({struct_val.type, dom.TEXT_TYPE})
        union = dom.Const.new_union(types, struct_val)
        encoded = union.encode

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
        once = union.encode
        twice = once.encode
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
        encoded = union.encode

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


if __name__ == "__main__":
    unittest.main()
