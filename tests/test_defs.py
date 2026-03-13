import unittest
from typing import cast

from axis import expr, sem
from axis.items import blocks
from axis.items.defs.base import build_binding_struct


class DefBuildBindingStructTest(unittest.TestCase):
    def test_inline_ignored_when_no_block(self):
        inline_expr = expr.Tuple.from_str("(a, ..rest)")
        struct = build_binding_struct(
            inline_expr=inline_expr,
            block_expr=None,
            binding_cls=sem.Entity.OverloadContribution.ParamBinding,
        )
        self.assertEqual(struct.index.keys, ())
        self.assertEqual(struct.values, ())

    # def test_prefix_mismatch_raises(self):
    #     inline_expr = cast(expr.Tuple, syn.Expr.from_str("(a, ..rest)"))
    #     block_expr = cast(expr.Tuple, syn.Expr.from_str("(b: T)"))
    #     with self.assertRaises(Report.Exception):
    #         build_binding_struct(
    #             inline_expr=inline_expr,
    #             block_expr=block_expr,
    #             binding_cls=sem.Entity.OverloadContribution.ParamBinding,
    #         )

    def test_prefix_match_with_spread(self):
        inline_expr = expr.Tuple.from_str("(a, ..rest)")
        block_expr = cast(blocks.TupleBlock, expr.Tuple.from_str("(a: T, b: U)"))
        struct = build_binding_struct(
            inline_expr=inline_expr,
            block_expr=block_expr,
            binding_cls=sem.Entity.OverloadContribution.ParamBinding,
        )
        self.assertEqual(struct.index.keys, ("a", "b"))
        self.assertEqual(len(struct.values), 2)

    def test_unsupported_block_element_is_ignored(self):
        inline_expr = expr.Tuple.from_str("(a, ..rest)")
        block_expr = cast(blocks.TupleBlock, expr.Tuple.from_str("(a)"))
        struct = build_binding_struct(
            inline_expr=inline_expr,
            block_expr=block_expr,
            binding_cls=sem.Entity.OverloadContribution.ParamBinding,
        )
        self.assertEqual(struct.index.keys, ())
        self.assertEqual(struct.values, ())
