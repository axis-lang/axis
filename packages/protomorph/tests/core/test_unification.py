from __future__ import annotations

import unittest

from protomorph.core import (
    Builtin, OMEGA,
    Placeholder, placeholder,
    LeafCarrier, TupleCarrier,
    VaryingType, UniformType,
    INT_TYPE, STR_TYPE, FLOAT_TYPE,
    unify,
)


def is_var(carrier) -> bool:
    """A carrier is a variable if its data is a Placeholder."""
    return isinstance(carrier.fetch(), Placeholder)


class TestUnify(unittest.TestCase):

    def test_identical_leaves(self):
        a = LeafCarrier(INT_TYPE, 42)
        b = LeafCarrier(INT_TYPE, 42)
        result = unify(a, b, is_var=is_var)
        self.assertIsNotNone(result)
        self.assertEqual(result.fetch(), 42)

    def test_different_leaves_fail(self):
        a = LeafCarrier(INT_TYPE, 42)
        b = LeafCarrier(INT_TYPE, 99)
        result = unify(a, b, is_var=is_var)
        self.assertIsNone(result)

    def test_var_captures_value(self):
        T = placeholder("T")
        a = LeafCarrier(OMEGA, T)
        b = LeafCarrier(OMEGA, INT_TYPE)
        result = unify(a, b, is_var=is_var)
        self.assertIsNotNone(result)
        self.assertIs(result.fetch(), INT_TYPE)

    def test_var_on_right(self):
        T = placeholder("T")
        a = LeafCarrier(OMEGA, INT_TYPE)
        b = LeafCarrier(OMEGA, T)
        result = unify(a, b, is_var=is_var)
        self.assertIsNotNone(result)
        self.assertIs(result.fetch(), INT_TYPE)

    def test_both_vars(self):
        T = placeholder("T")
        U = placeholder("U")
        a = LeafCarrier(OMEGA, T)
        b = LeafCarrier(OMEGA, U)
        result = unify(a, b, is_var=is_var)
        # Both are vars, they bind to each other.
        # Result substitutes a's var → b's var (or vice versa).
        self.assertIsNotNone(result)

    def test_tuple_unification(self):
        vt = VaryingType.make(OMEGA, OMEGA)
        T = placeholder("T")
        a = TupleCarrier(vt, (T, STR_TYPE))
        b = TupleCarrier(vt, (INT_TYPE, STR_TYPE))
        result = unify(a, b, is_var=is_var)
        self.assertIsNotNone(result)
        self.assertEqual(result.fetch(), (INT_TYPE, STR_TYPE))

    def test_tuple_mismatch_fails(self):
        vt = VaryingType.make(OMEGA, OMEGA)
        a = TupleCarrier(vt, (INT_TYPE, STR_TYPE))
        b = TupleCarrier(vt, (INT_TYPE, FLOAT_TYPE))
        result = unify(a, b, is_var=is_var)
        self.assertIsNone(result)

    def test_arity_mismatch_fails(self):
        vt2 = VaryingType.make(OMEGA, OMEGA)
        vt3 = VaryingType.make(OMEGA, OMEGA, OMEGA)
        a = TupleCarrier(vt2, (INT_TYPE, STR_TYPE))
        b = TupleCarrier(vt3, (INT_TYPE, STR_TYPE, FLOAT_TYPE))
        result = unify(a, b, is_var=is_var)
        # Root pair: not leaves, arities differ → deep_zip doesn't descend
        # But roots themselves are not equal → returns None
        self.assertIsNone(result)

    def test_nested_var(self):
        vt = VaryingType.make(OMEGA, OMEGA)
        T = placeholder("T")
        a = TupleCarrier(vt, (INT_TYPE, T))
        b = TupleCarrier(vt, (INT_TYPE, FLOAT_TYPE))
        result = unify(a, b, is_var=is_var)
        self.assertIsNotNone(result)
        self.assertEqual(result.fetch()[1], FLOAT_TYPE)

    def test_custom_op(self):
        """Custom op can resolve multiple bindings."""
        vt = VaryingType.make(OMEGA, OMEGA)
        T = placeholder("T")
        a = TupleCarrier(vt, (T, T))
        b = TupleCarrier(vt, (INT_TYPE, INT_TYPE))

        def strict_op(vals):
            vals_list = list(vals)
            if all(v == vals_list[0] for v in vals_list):
                return vals_list[0]
            return None

        result = unify(a, b, is_var=is_var, op=strict_op)
        self.assertIsNotNone(result)
        self.assertEqual(result.fetch(), (INT_TYPE, INT_TYPE))

    def test_custom_op_conflict(self):
        vt = VaryingType.make(OMEGA, OMEGA)
        T = placeholder("T")
        a = TupleCarrier(vt, (T, T))
        b = TupleCarrier(vt, (INT_TYPE, STR_TYPE))

        def strict_op(vals):
            vals_list = list(vals)
            if all(v == vals_list[0] for v in vals_list):
                return vals_list[0]
            return None

        result = unify(a, b, is_var=is_var, op=strict_op)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
