from __future__ import annotations

from pathlib import Path
import sys
import unittest

from protobase import Consed

import protomorph as morph

sys.path.insert(0, str(Path(__file__).parent))

from support import DummyContext, DummyVarType


class LayoutBridge(morph.SemanticBridgeBase, Consed):
    def layout(self, type: morph.Type) -> morph.Layout | None:
        if isinstance(type, morph.NominalType) and type.spec_ref.path in {"test.Left", "test.Right"}:
            return morph.StructLayout(fields=morph.Struct.from_iter((("value", morph.TEXT_TYPE),)))
        return super().layout(type)


class AlgebraTests(unittest.TestCase):
    def setUp(self):
        self._native_bridge = morph.NATIVE_BACKEND
        self._native_bridge.__enter__()

    def tearDown(self):
        self._native_bridge.__exit__(None, None, None)

    def test_unify_is_symmetric_for_vars_and_literals(self):
        ctx = DummyContext()
        var = morph.var(DummyVarType, ctx, "T")

        left = morph.unify(var, morph.literal(7))
        right = morph.unify(morph.literal(7), var)

        self.assertEqual(left[0].subst.bindings[var], morph.literal(7))
        self.assertEqual(right[0].subst.bindings[var], morph.literal(7))

    def test_unify_specs_binds_nested_args(self):
        ctx = DummyContext()
        var = morph.var(DummyVarType, ctx, "T")

        result = morph.unify(
            morph.spec_ref("test.Box", morph.struct(var)),
            morph.spec_ref("test.Box", morph.struct(morph.literal(7))),
        )

        self.assertEqual(result[0].subst.bindings[var], morph.literal(7))

    def test_satisfies_struct_types_requires_closed_shape_compatibility(self):
        left = morph.struct_type(name=str)
        right = morph.struct_type(name=str)
        other = morph.struct_type(value=str)

        self.assertTrue(morph.subsumes(left, right))
        self.assertFalse(morph.subsumes(left, other))

    def test_nominal_types_use_bridge_layout_when_available(self):
        bridge = LayoutBridge()
        left = morph.nominal_type("test.Left")
        right = morph.nominal_type("test.Right")

        self.assertTrue(morph.subsumes(left, right, bridge=bridge))


if __name__ == "__main__":
    unittest.main()
