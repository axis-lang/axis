from __future__ import annotations

import unittest
from typing import cast
from pathlib import Path
import sys

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


class RefsAndVarsTests(unittest.TestCase):
    def test_anchor_route_covers_root_child_parent_name_and_specialize(self):
        root = morph.Anchor.from_root("std")
        child = root.child("Text")
        spec = child.specialize(morph.struct(K=cast(morph.Const | morph.Var, morph.val(morph.TEXT_TYPE))))

        self.assertEqual(root.root, "std")
        self.assertEqual(child.name, "Text")
        self.assertEqual(child.parent, root)
        self.assertEqual(spec.path, "std.Text")

    def test_anchor_and_ref_routes_cover_edge_state_without_abstract_segments_override(self):
        empty_anchor = morph.Anchor(morph.refs._anchor_type_instance(), cast(tuple[str, ...], ()))

        self.assertEqual(empty_anchor.path, "")

    def test_anchor_type_decode_route_accepts_string_tuples_and_rejects_other_payloads(self):
        anchor_type = morph.refs.AnchorType()

        self.assertEqual(anchor_type._decode(("std", "Text")), ("std", "Text"))
        with self.assertRaises(ValueError):
            anchor_type._decode(("std", 1))

    def test_spec_type_routes_cover_meta_spec_encode_decode_and_dir(self):
        meta_args = morph.StructType(meta_attrs=morph.Struct.new(K=morph.TEXT_TYPE))
        spec_type = morph.refs.SpecType(meta_args=meta_args)

        self.assertIsNotNone(spec_type._metaspec())
        self.assertEqual(spec_type._encode((("std", "Map"), ("x",))), (("std", "Map"), ("x",)))
        self.assertEqual(spec_type._decode((("std", "Map"), ("x",))), (("std", "Map"), ("x",)))
        fields = spec_type._dir()
        assert fields is not None
        self.assertEqual(tuple(fields.index.keys), ("K",))

    def test_spec_type_exception_routes_reject_incompatible_meta_payloads(self):
        plain_spec_type = morph.refs.SpecType(meta_args=None)
        typed_spec_type = morph.refs.SpecType(meta_args=morph.StructType(meta_attrs=morph.Struct.new(K=morph.TEXT_TYPE)))

        with self.assertRaises(ValueError):
            plain_spec_type._encode((("std", "Map"), ("x",)))
        with self.assertRaises(ValueError):
            typed_spec_type._encode((("std", "Map"), "x"))
        with self.assertRaises(ValueError):
            typed_spec_type._decode((("std", "Map"), "x"))

    def test_spec_route_rehydrates_args_and_round_trips_back_to_struct_consts(self):
        ctx = DummyContext()
        type_var = morph.var(DummyVarType, ctx, "T")
        spec_const = morph.struct(K=cast(morph.Const | morph.Var, morph.val(morph.TEXT_TYPE)), T=type_var)
        spec = morph.spec_ref("std.Map", spec_const)

        args = spec.args
        self.assertIsNotNone(args)
        assert args is not None
        self.assertEqual(repr(args.get("K")), "std.Text")
        self.assertEqual(repr(args.get("T")), "$T")
        self.assertEqual(spec._args_const(), spec_const)

    def test_var_routes_cover_wrap_and_metatype_identity_paths(self):
        ctx = DummyContext()
        type_var = morph.var(DummyVarType, ctx, "T")

        self.assertIs(type_var._metatype(), type_var.type)
        self.assertEqual(type_var.type._wrap("T"), type_var)
        self.assertIs(type_var._wrap("T"), type_var)
        with self.assertRaises(ValueError):
            type_var.type._wrap(1)
        with self.assertRaises(ValueError):
            type_var._wrap("U")
