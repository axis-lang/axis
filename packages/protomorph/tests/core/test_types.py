from __future__ import annotations

import unittest
from typing import cast

import protomorph as pm


class TestTypesApi(unittest.TestCase):
    def test_bootstraped_specs_are_exposed(self):
        self.assertIs(pm.types.any, pm.Spec.Any)
        self.assertIs(pm.types.never, pm.Spec.Never)
        self.assertIs(pm.types.integer, pm.Spec.Integer)
        self.assertIs(pm.types.text, pm.Spec.Text)

    def test_named_builds_specialization(self):
        spec = pm.types.named(pm.anchors.any)

        self.assertEqual(spec.anchor, pm.anchors.any)

    def test_qualify_builds_nested_qual(self):
        descriptor = cast(
            pm.Qual,
            pm.types.qualify(
                pm.Spec.of("test.qualifiers.Inner"),
                pm.Spec.of(pm.anchors.optional),
                under=pm.types.integer,
            ),
        )

        self.assertIsInstance(descriptor, pm.Qual)
        self.assertEqual(descriptor.qualifier.anchor, pm.anchors.optional)
        self.assertEqual(cast(pm.Qual, descriptor.qualified).qualifier.anchor, "test.qualifiers.Inner")

    def test_optional_builds_optional_qual(self):
        descriptor = cast(pm.Qual, pm.types.optional(pm.types.integer))

        self.assertEqual(descriptor.qualifier.anchor, pm.anchors.optional)
        self.assertIs(descriptor.qualified, pm.types.integer)

    def test_map_builds_map_qual(self):
        descriptor = cast(pm.Qual, pm.types.map(pm.types.integer, key=pm.types.text))

        self.assertEqual(descriptor.qualifier.anchor, pm.anchors.map)
        self.assertEqual(descriptor.qualifier.args[0].content, pm.types.text)
        self.assertIs(descriptor.qualified, pm.types.integer)

    def test_result_defaults_to_never_error(self):
        descriptor = cast(pm.Qual, pm.types.result(pm.types.integer))

        self.assertEqual(descriptor.qualifier.anchor, pm.anchors.result)
        self.assertEqual(descriptor.qualifier.args[0].content, pm.types.never)
        self.assertIs(descriptor.qualified, pm.types.integer)

    def test_result_accepts_explicit_error(self):
        descriptor = cast(pm.Qual, pm.types.result(pm.types.integer, err=pm.types.text))

        self.assertEqual(descriptor.qualifier.args[0].content, pm.types.text)


if __name__ == "__main__":
    unittest.main()
