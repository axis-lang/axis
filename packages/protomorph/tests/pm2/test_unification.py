from __future__ import annotations

import unittest
from typing import cast

from pm import (
    Placeholder, placeholder,
    LeafCarrier, TupleCarrier,
    VaryingType, Spec,
    unify, wrap,
)

ANY = Spec.of("std.core.Any")
INT = wrap(int)
STR = wrap(str)
FLOAT = wrap(float)


def is_var(carrier) -> bool:
    return isinstance(carrier.fetch(), Placeholder)


class TestUnify(unittest.TestCase):
    def test_identical_leaves(self):
        a = LeafCarrier(INT, 42)
        b = LeafCarrier(INT, 42)
        result = unify(a, b, is_var=is_var)
        assert result is not None
        self.assertEqual(result.fetch(), 42)

    def test_different_leaves_fail(self):
        a = LeafCarrier(INT, 42)
        b = LeafCarrier(INT, 99)
        self.assertIsNone(unify(a, b, is_var=is_var))

    def test_var_captures_value(self):
        T = placeholder("T")
        a = LeafCarrier(ANY, T)
        b = LeafCarrier(ANY, INT)
        result = unify(a, b, is_var=is_var)
        assert result is not None
        self.assertIs(result.fetch(), INT)

    def test_tuple_unification(self):
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        T = placeholder("T")
        a = TupleCarrier(vt, (T, STR))
        b = TupleCarrier(vt, (INT, STR))
        result = unify(a, b, is_var=is_var)
        assert result is not None
        self.assertEqual(result.fetch(), (INT, STR))

    def test_tuple_mismatch_fails(self):
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        a = TupleCarrier(vt, (INT, STR))
        b = TupleCarrier(vt, (INT, FLOAT))
        self.assertIsNone(unify(a, b, is_var=is_var))


if __name__ == "__main__":
    unittest.main()
