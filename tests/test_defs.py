import unittest
from typing import cast

from axis import expr, syn, sem
from axis.log.report import Report
from axis.items.defs.base import merge_inline_block_tuple
from axis.sem import Context


class DefMergeInlineBlockTupleTest(unittest.TestCase):
    def test_inline_ignored_when_no_block(self):
        inline_expr = cast(expr.Tuple, syn.Expr.from_str("(a, ..rest)"))
        struct = merge_inline_block_tuple(
            inline_expr=inline_expr,
            block_expr=None,
            binding_cls=sem.Entity.OverloadContribution.ParamBinding,
        )
        self.assertEqual(struct.index.keys, ())
        self.assertEqual(struct.values, ())

    def test_prefix_mismatch_raises(self):
        inline_expr = cast(expr.Tuple, syn.Expr.from_str("(a, ..rest)"))
        block_expr = cast(expr.Tuple, syn.Expr.from_str("(b: T)"))
        with self.assertRaises(Report.Exception):
            merge_inline_block_tuple(
                inline_expr=inline_expr,
                block_expr=block_expr,
                binding_cls=sem.Entity.OverloadContribution.ParamBinding,
            )

    def test_prefix_match_with_spread(self):
        inline_expr = cast(expr.Tuple, syn.Expr.from_str("(a, ..rest)"))
        block_expr = cast(expr.Tuple, syn.Expr.from_str("(a: T, b: U)"))
        struct = merge_inline_block_tuple(
            inline_expr=inline_expr,
            block_expr=block_expr,
            binding_cls=sem.Entity.OverloadContribution.ParamBinding,
        )
        self.assertEqual(struct.index.keys, ("a", "b"))
        self.assertEqual(len(struct.values), 2)

    def test_block_requires_bound(self):
        inline_expr = cast(expr.Tuple, syn.Expr.from_str("(a, ..rest)"))
        block_expr = cast(expr.Tuple, syn.Expr.from_str("(a)"))
        with self.assertRaises(Report.Exception):
            merge_inline_block_tuple(
                inline_expr=inline_expr,
                block_expr=block_expr,
                binding_cls=sem.Entity.OverloadContribution.ParamBinding,
            )
