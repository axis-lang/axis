import unittest
from typing import cast

from axis import expr, items, log, sem
from axis.items.defs.base import build_binding_struct


class DummyRealm(sem.Realm):
    @property
    def all_contexts(self) -> tuple[sem.Context, ...]:
        return ()


TEST_REALM = DummyRealm()


def parse_def(source: str) -> items.Def:
    node = items.Def.from_src(source, realm=TEST_REALM)[0]
    assert node is not None
    assert isinstance(node, items.Def)
    return node


class DefFromSrcTest(unittest.TestCase):
    def test_from_src_parses_def_without_unit_wrapper(self):
        cases = (
            ("def Optional T", items.QualDef),
            ("def E[A](x, y)", items.ClassDef),
        )

        for source, expected_type in cases:
            with self.subTest(source=source):
                node = parse_def(source)
                self.assertIsInstance(node, expected_type)

    def test_from_src_preserves_inline_shape_information(self):
        node = parse_def(
            """def Array[..Dims, ...] T
where:
    val Dims: Array Natural
    val T: Type = Sym
"""
        )
        node = cast(items.QualDef, node)

        self.assertIsInstance(node, items.QualDef)
        self.assertIsNotNone(node.spec)
        assert node.spec is not None
        self.assertTrue(node.spec.elements[0].is_spread)
        self.assertTrue(node.spec.elements[1].is_ellipsis)
        self.assertEqual(
            tuple(str(element) for element in node.where[0].elements),
            ("Dims: Array Natural", "T: Type = Sym"),
        )

    def test_from_src_preserves_inline_args_and_takes_blocks(self):
        node = parse_def(
            """def E[A, ...](x, y)
where:
    val A: Type
    val K: Type = Sym
takes:
    val x: Whole
    val y: Text
"""
        )
        node = cast(items.ClassDef, node)

        self.assertIsInstance(node, items.ClassDef)
        self.assertEqual(str(node.spec), "(A, Lit(Ellipsis))")
        self.assertEqual(str(node.args), "(x, y)")
        self.assertEqual(
            tuple(str(element) for element in node.takes[0].elements),
            ("x: Whole", "y: Text"),
        )


class DefBuildBindingStructTest(unittest.TestCase):
    def test_inline_only_bindings_are_preserved(self):
        node = parse_def("def Struct[Key: Type = Text]")
        node = cast(items.ClassDef, node)
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=None,
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertEqual(len(struct.values), 1)
        self.assertEqual(struct.values[0].binder_name, "Key")
        self.assertEqual(struct.values[0].slot_key, None)
        self.assertEqual(str(struct.values[0].bound_expr), "Type")
        self.assertEqual(str(struct.values[0].default_expr), "Text")
        self.assertFalse(struct.open_tail)

    def test_block_only_bindings_remain_nominal(self):
        node = parse_def(
            """def E
where:
    val A: Type
    val B: Type = Sym
"""
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, ("A", "B"))
        self.assertEqual(tuple(binding.slot_key for binding in struct.values), ("A", "B"))

    def test_prefix_match_with_spread(self):
        node = parse_def(
            """def Array[..Dims, ...] T
where:
    val Dims: Array Natural
    val T: Type = Sym
"""
        )
        assert isinstance(node, items.QualDef)
        struct = build_binding_struct(
            inline_expr=node.spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None, "T"))
        self.assertEqual(len(struct.values), 2)
        self.assertTrue(struct.values[0].is_variadic)
        self.assertTrue(struct.open_tail)

    def test_param_bindings_use_real_takes_blocks(self):
        node = parse_def(
            """def E[A](x, ...)
where:
    val A: Type
takes:
    val x: Whole
    val y: Text
"""
        )
        assert isinstance(node, items.ClassDef)
        struct = build_binding_struct(
            inline_expr=node.args,
            block_expr=node.takes[0],
        )
        self.assertEqual(struct.index.keys, (None, "y"))
        self.assertEqual(len(struct.values), 2)
        self.assertTrue(struct.open_tail)

    def test_inline_placeholder_merges_with_block_placeholder(self):
        node = parse_def(
            """def E[_]
where:
    val _: Natural
"""
        )
        struct = build_binding_struct(
            inline_expr=cast(items.ClassDef, node).spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertTrue(struct.values[0].is_placeholder)
        self.assertEqual(str(struct.values[0].bound_expr), "Natural")

    def test_block_only_spread_is_supported(self):
        node = parse_def(
            """def E
where:
    val ..Args: Array Natural
"""
        )
        struct = build_binding_struct(
            inline_expr=None,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None,))
        self.assertTrue(struct.values[0].is_variadic)
        self.assertEqual(struct.values[0].binder_name, "Args")

    def test_closed_inline_rejects_extra_block_bindings(self):
        node = parse_def(
            """def E[A]
where:
    val A: Type
    val B: Type
"""
        )
        struct = build_binding_struct(
            inline_expr=cast(items.ClassDef, node).spec,
            block_expr=node.where[0],
        )
        self.assertEqual(struct.index.keys, (None, "B"))
        self.assertEqual(tuple(binding.binder_name for binding in struct.values), ("A", "B"))

    def test_rejects_conflicting_bounds(self):
        node = parse_def(
            """def E[A: Whole]
where:
    val A: Text
"""
        )
        with self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=cast(items.ClassDef, node).spec,
                block_expr=node.where[0],
            )

    def test_rejects_nonfinal_ellipsis(self):
        inline_expr = expr.Tuple.from_str("(a, ..., b)")
        with self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=inline_expr,
                block_expr=None,
            )

    def test_rejects_nonfinal_spread(self):
        inline_expr = expr.Tuple.from_str("(..rest, a)")
        with self.assertRaises(log.Report.Exception):
            build_binding_struct(
                inline_expr=inline_expr,
                block_expr=None,
            )
