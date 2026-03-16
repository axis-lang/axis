from __future__ import annotations

import unittest
from pathlib import Path
import sys
from typing import cast

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import Thing


class RefsAndQualifiersTests(unittest.TestCase):
    def test_anchor_routes_cover_root_child_parent_name_and_specialize(self):
        root = morph.Anchor.from_root("std")
        child = root.child("Text")
        spec = child.specialize(morph.spec(K=str))

        self.assertEqual(root.root, "std")
        self.assertEqual(child.name, "Text")
        self.assertEqual(child.parent, root)
        self.assertEqual(child.path, "std.Text")
        self.assertEqual(spec.path, "std.Text")
        self.assertEqual(repr(morph.val(spec)), "std.Text[K=std.Text]")

    def test_anchor_type_decode_route_rejects_non_string_segments(self):
        anchor_type = morph.refs.AnchorType()

        self.assertEqual(anchor_type.decode(("std", "Text")).data, ("std", "Text"))
        with self.assertRaises(ValueError):
            anchor_type.decode(("std", 1))

    def test_spec_type_routes_cover_meta_args_encode_decode_and_dir(self):
        spec_type = morph.refs.SpecType(meta_args=morph.struct_type(K=str, V=int))
        decoded = spec_type.decode((("std", "Map"), ("x", 1)))
        layout = spec_type.layout()

        self.assertEqual(decoded.data, (("std", "Map"), ("x", 1)))
        self.assertEqual(spec_type.serialize((("std", "Map"), ("x", 1))), (("std", "Map"), ("x", 1)))
        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), ("K", "V"))

        metaspec = spec_type._metaspec()
        self.assertIsNotNone(metaspec)
        assert metaspec is not None
        self.assertEqual(repr(metaspec), "(K=std.Nominal.Type, V=std.Nominal.Type)")
        self.assertEqual(
            tuple(cast(morph.StructType, metaspec.__type__).meta_attrs.index.keys),
            ("K", "V"),
        )

    def test_spec_type_exception_routes_reject_invalid_meta_payloads(self):
        plain = morph.refs.SpecType(meta_args=morph.EMPTY_STRUCT_TYPE)
        typed = morph.refs.SpecType(meta_args=morph.struct_type(K=str))

        with self.assertRaises(ValueError):
            plain.serialize((("std", "Map"), ("x",)))
        with self.assertRaises(ValueError):
            typed.decode((("std", "Map"), "x"))
        with self.assertRaises(ValueError):
            typed.serialize((("std", "Map"), "x"))

    def test_spec_args_routes_cover_roundtrip_back_to_struct_consts(self):
        spec = morph.spec_ref("test.Box", morph.spec(T=str))
        bare = morph.spec_ref("std.Text")

        args = spec.args
        self.assertIsNotNone(args)
        assert args is not None
        self.assertEqual(repr(args.get("T")), "std.Text")
        self.assertEqual(spec._args_const(), morph.spec(T=str))
        self.assertEqual(bare.args, morph.Struct.Empty)
        self.assertEqual(bare._args_const(), morph.spec())

    def test_nominal_and_qualifier_metaspecs_track_arg_schema(self):
        left = morph.nominal_type("std.Map", morph.spec(K=str, V=int))
        right = morph.nominal_type("std.Map", morph.spec(K=int, V=str))

        self.assertEqual(left._metaspec(), right._metaspec())
        self.assertEqual(repr(left._metaspec()), "(K=std.Nominal.Type, V=std.Nominal.Type)")

        left_qual = morph.nominal_qual("std.Map", morph.spec(K=str), underlying=morph.INTEGER_TYPE)
        right_qual = morph.nominal_qual("std.Map", morph.spec(K=int), underlying=morph.INTEGER_TYPE)

        self.assertEqual(left_qual._metaspec(), right_qual._metaspec())
        self.assertEqual(repr(left_qual._metaspec()), "(S=(K=std.Nominal.Type), U=std.Nominal.Type)")

    def test_qualifier_routes_cover_layout_and_opaque_decode_contract(self):
        with morph.NATIVE_BACKEND:
            qualified = morph.nominal_type("test.Future").qualify(morph.struct_type(name=str, value=int))
            layout = qualified.layout()

        self.assertIsNotNone(layout)
        assert isinstance(layout, morph.StructLayout)
        self.assertEqual(tuple(layout.fields.index.keys), ("name", "value"))
        with self.assertRaises(TypeError):
            qualified.decode(("x", 1))
        with self.assertRaises(TypeError):
            qualified.construct(name="x", value=1)

    def test_qualifier_routes_reject_opaque_and_unsupported_projection_paths(self):
        qualifier = morph.nominal_type("test.Future").qualify(morph.TEXT_TYPE)

        with self.assertRaises(TypeError):
            qualifier.construct("x")
        with self.assertRaises(TypeError):
            qualifier.decode("x")
        with self.assertRaises(NotImplementedError):
            qualifier._get("x", "name")


if __name__ == "__main__":
    unittest.main()
