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

    def test_spec_type_exception_routes_reject_invalid_meta_payloads(self):
        plain = morph.refs.SpecType(meta_args=None)
        typed = morph.refs.SpecType(meta_args=morph.struct_type(K=str))

        with self.assertRaises(ValueError):
            plain.serialize((("std", "Map"), ("x",)))
        with self.assertRaises(ValueError):
            typed.decode((("std", "Map"), "x"))
        with self.assertRaises(ValueError):
            typed.serialize((("std", "Map"), "x"))

    def test_spec_args_routes_cover_roundtrip_back_to_struct_consts(self):
        spec = morph.spec_ref("test.Box", morph.spec(T=str))

        args = spec.args
        self.assertIsNotNone(args)
        assert args is not None
        self.assertEqual(repr(args.get("T")), "std.Text")
        self.assertEqual(spec._args_const(), morph.spec(T=str))

    def test_qualifier_routes_cover_layout_and_opaque_decode_contract(self):
        with morph.DEFAULT_NATIVE_BACKEND:
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
