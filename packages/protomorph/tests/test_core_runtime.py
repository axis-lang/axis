from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import cast

from protobase import Inmutable

from protomorph import core
from protomorph.core import display
from protomorph.core.native import meta_from_native

sys.path.insert(0, str(Path(__file__).parent))


class Box[T](core.Builtin):
    value: T


class PairBox[K, V](core.Builtin):
    left: K
    right: V


class FancyBox[T](core.Builtin):
    pair: PairBox[T, int]
    box: Box[T]


class CoreRuntimeTests(unittest.TestCase):
    def test_display_helpers_render_core_values_simply(self):
        tuple_value = core.Tuple.of(core.Integer, name=core.Text)
        dict_type = meta_from_native(dict[str, set[int]])

        self.assertEqual(repr(tuple_value), "(Integer, name=Text)")
        self.assertEqual(repr(core.Spec.of("test.Box", T=core.Text)), "test.Box[T=Text]")
        self.assertEqual(
            repr(dict_type),
            "Dict[K=Text] Set Integer",
        )
        self.assertEqual(repr(meta_from_native(list[int])), "List Integer")
        self.assertEqual(
            repr(meta_from_native(dict[str, int])),
            "Dict[K=Text] Integer",
        )

    def test_tuple_can_store_meta_values_without_losing_identity(self):
        union = core.Union.of(core.Integer, core.Text)
        tuple_value = core.Tuple.of(core.Integer, union)

        self.assertIs(tuple_value.at(0), core.Integer)
        self.assertIs(tuple_value.at(1), union)
        self.assertEqual(repr(tuple_value), "(Integer, Integer | Text)")
        self.assertTrue(all(not isinstance(item, core.Val) for item in tuple_value.__data__))

    def test_spec_of_preserves_positional_and_keyword_args(self):
        spec = core.Spec.of("test.Box", core.Integer, name=core.Text)

        self.assertEqual(spec.path, "test.Box")
        self.assertEqual(spec.args.arity, 2)
        self.assertEqual(tuple(spec.args.index or ()), (None, "name"))
        self.assertEqual(spec.args.at(0), core.Integer)
        self.assertEqual(spec.args.at(1), core.Text)

    def test_qual_of_preserves_raw_meta_values(self):
        qual = core.Qual.of(core.Union.of(core.Text, core.Integer), core.Spec.of("std.qualifiers.List"))
        qualifier = cast(core.Spec, qual.qualifiers[0])

        self.assertIsInstance(qual.underlying, core.Union)
        self.assertEqual(qual.qualifiers.arity, 1)
        self.assertIsInstance(qualifier, core.Spec)
        self.assertEqual(qualifier.path, "std.qualifiers.List")
        self.assertEqual(repr(qual), "List Integer | Text")

    def test_qual_display_is_flattened_in_tuple_order(self):
        qual = core.Qual.of(
            core.Integer,
            core.Spec.of("std.qualifiers.A"),
            core.Spec.of("std.qualifiers.B", T=core.Text),
        )

        self.assertEqual(
            repr(qual),
            "B[T=Text] A Integer",
        )

    def test_spec_display_trims_default_prefixes(self):
        self.assertEqual(repr(core.Integer), "Integer")
        self.assertEqual(repr(core.Spec.of("std.qualifiers.List")), "List")

    def test_spec_display_prefixes_are_configurable(self):
        original = list(display.SPEC_PATH_PREFIXES)
        try:
            display.SPEC_PATH_PREFIXES.append("test.")
            self.assertEqual(repr(core.Spec.of("test.Widget")), "Widget")
        finally:
            display.SPEC_PATH_PREFIXES[:] = original

    def test_tuple_replace_key_preserves_index_when_schema_becomes_varying(self):
        value = core.Tuple.of(name=core.Integer, value=core.Text)
        key = (value.index and value.index.key_meta.wrap("value"))
        assert key is not None

        replaced = value.replace_key(key, core.Bool)

        self.assertIsNotNone(replaced.index)
        self.assertEqual(tuple(replaced.index or ()), ("name", "value"))
        self.assertEqual(replaced.get(key), core.Bool)

    def test_unify_rejects_non_leaf_nodes_with_different_identity(self):
        left = core.Spec.of("test.Left", core.Integer)
        right = core.Spec.of("test.Right", core.Integer)

        result = core.unify(left, right, is_var=lambda _: False)

        self.assertIsNone(result)

    def test_native_host_specializes_generic_builtin_fields(self):
        spec = meta_from_native(FancyBox[str])
        self.assertIsInstance(spec, core.Spec)
        spec = spec

        value = FancyBox(
            pair=PairBox(left="x", right=1),
            box=Box(value="y"),
        )

        children = core.NATIVE_HOST.val_children(spec, value)
        pair_meta = children[0].__meta__
        box_meta = children[1].__meta__

        self.assertEqual(pair_meta.path, f"{PairBox.__module__}.{PairBox.__qualname__}")
        self.assertEqual(pair_meta.args.at(0), core.Text)
        self.assertEqual(pair_meta.args.at(1), core.Integer)
        self.assertEqual(box_meta.path, f"{Box.__module__}.{Box.__qualname__}")
        self.assertEqual(box_meta.args.at(0), core.Text)


if __name__ == "__main__":
    unittest.main()
