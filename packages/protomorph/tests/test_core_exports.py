from __future__ import annotations

import unittest

import protomorph as pm
import protomorph.core.anchors as core_anchors
import protomorph.core.types as core_types
import protomorph.core.values as core_values


class TestCoreExports(unittest.TestCase):
    def test_core_types_reexport_root_types(self):
        self.assertIs(core_types.Type, pm.Type)
        self.assertIs(core_types.Spec, pm.Spec)
        self.assertIs(core_types.Qual, pm.Qual)
        self.assertIs(core_types.Union, pm.Union)

    def test_core_exports_namespace_modules(self):
        self.assertIs(pm.types.Spec, pm.Spec)
        self.assertEqual(pm.anchors.result, core_anchors.result)
        self.assertIs(pm.types.any, pm.Spec.Any)

    def test_core_values_reexport_root_values(self):
        self.assertIs(core_values.Val, pm.Val)
        self.assertIs(core_values.Tuple, pm.Tuple)
        self.assertIs(core_values.make_value, pm.make_value)


if __name__ == "__main__":
    unittest.main()
