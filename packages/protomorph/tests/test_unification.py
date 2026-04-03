from __future__ import annotations

import unittest
from typing import cast

from protomorph import (
    Builtin,
    Placeholder, placeholder,
    LeafCarrier, NativeObjectCarrier, Tuple,
    VaryingType, Spec,
    UnionFind, unify, wrap,
)

ANY = Spec.of("std.core.Any")
INT = cast(Spec, wrap(int).fetch())
STR = cast(Spec, wrap(str).fetch())
FLOAT = cast(Spec, wrap(float).fetch())


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
        a = Tuple(vt, (T, STR))
        b = Tuple(vt, (INT, STR))
        result = unify(a, b, is_var=is_var)
        assert result is not None
        self.assertEqual(repr(result.fetch()), repr((INT, STR)))

    def test_tuple_mismatch_fails(self):
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        a = Tuple(vt, (INT, STR))
        b = Tuple(vt, (INT, FLOAT))
        self.assertIsNone(unify(a, b, is_var=is_var))

    def test_descriptor_mismatch_fails(self):
        a = Tuple(cast(VaryingType, VaryingType.of(INT, STR)), (1, "a"))
        b = Tuple(cast(VaryingType, VaryingType.of(INT, FLOAT)), (1, 2.0))
        self.assertIsNone(unify(a, b, is_var=is_var))


class TestOccursCheck(unittest.TestCase):
    def test_self_referential_fails(self):
        """$T = Tuple($T, int) should fail — prevents infinite types."""
        T = placeholder("T")
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        a = LeafCarrier(ANY, T)
        b = Tuple(vt, (T, INT))
        self.assertIsNone(unify(a, b, is_var=is_var))

    def test_self_referential_allowed_without_check(self):
        """With occurs_check=False, self-referential binding succeeds."""
        T = placeholder("T")
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        a = LeafCarrier(ANY, T)
        b = Tuple(vt, (T, INT))
        result = unify(a, b, is_var=is_var, occurs_check=False)
        self.assertIsNotNone(result)


class TestTransitiveResolution(unittest.TestCase):
    def test_var_chain(self):
        """$T = $U, $U = int  →  $T resolves to int."""
        T = placeholder("T")
        U = placeholder("U")
        uf = UnionFind(is_var)

        a1 = LeafCarrier(ANY, T)
        a2 = LeafCarrier(ANY, U)
        result1 = unify(a1, a2, subst=uf)
        self.assertIsNotNone(result1)

        b1 = LeafCarrier(ANY, U)
        b2 = LeafCarrier(ANY, INT)
        result2 = unify(b1, b2, subst=uf)
        self.assertIsNotNone(result2)

        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), INT)

    def test_conflicting_binding_fails(self):
        """$T = int then $T = str should fail."""
        T = placeholder("T")
        uf = UnionFind(is_var)

        r1 = unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        self.assertIsNotNone(r1)

        r2 = unify(LeafCarrier(ANY, T), LeafCarrier(ANY, STR), subst=uf)
        self.assertIsNone(r2)

    def test_consistent_rebinding_succeeds(self):
        """$T = int then $T = int again should succeed."""
        T = placeholder("T")
        uf = UnionFind(is_var)

        r1 = unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        self.assertIsNotNone(r1)

        r2 = unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        self.assertIsNotNone(r2)


class TestSnapshotRollback(unittest.TestCase):
    def test_rollback_undoes_binding(self):
        T = placeholder("T")
        uf = UnionFind(is_var)
        mark = uf.snapshot()

        unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), INT)

        uf.rollback(mark)
        # T should be unbound again
        resolved = uf.reify(LeafCarrier(ANY, T))
        self.assertIsInstance(resolved.fetch(), Placeholder)

    def test_rollback_nested(self):
        T = placeholder("T")
        U = placeholder("U")
        uf = UnionFind(is_var)

        # Bind T
        unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        mark = uf.snapshot()

        # Bind U
        unify(LeafCarrier(ANY, U), LeafCarrier(ANY, STR), subst=uf)
        self.assertIs(uf.reify(LeafCarrier(ANY, U)).fetch(), STR)

        # Rollback only U
        uf.rollback(mark)
        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), INT)  # T still bound
        self.assertIsInstance(uf.reify(LeafCarrier(ANY, U)).fetch(), Placeholder)  # U unbound

    def test_rollback_allows_alternative(self):
        """Simulate impl selection: try one, rollback, try another."""
        T = placeholder("T")
        uf = UnionFind(is_var)
        mark = uf.snapshot()

        # Try binding T = int — then decide it's wrong
        unify(LeafCarrier(ANY, T), LeafCarrier(ANY, INT), subst=uf)
        uf.rollback(mark)

        # Try binding T = str instead
        r = unify(LeafCarrier(ANY, T), LeafCarrier(ANY, STR), subst=uf)
        self.assertIsNotNone(r)
        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), STR)


class TestSharedSubst(unittest.TestCase):
    def test_bidirectional_resolution(self):
        """Simulate Rust-style: info flows forward then backward."""
        T = placeholder("T")
        U = placeholder("U")
        uf = UnionFind(is_var)

        # Forward: from call site, we know T = int
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        r1 = unify(
            Tuple(vt, (T, U)),
            Tuple(vt, (INT, U)),  # U still unknown
            subst=uf,
        )
        self.assertIsNotNone(r1)
        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), INT)

        # Backward: from return type, we learn U = str
        r2 = unify(LeafCarrier(ANY, U), LeafCarrier(ANY, STR), subst=uf)
        self.assertIsNotNone(r2)

        # Both resolved
        self.assertIs(uf.reify(LeafCarrier(ANY, T)).fetch(), INT)
        self.assertIs(uf.reify(LeafCarrier(ANY, U)).fetch(), STR)

    def test_deep_reify(self):
        """Reify resolves variables inside bound terms."""
        T = placeholder("T")
        U = placeholder("U")
        uf = UnionFind(is_var)

        # T = Tuple(U, int)
        vt = cast(VaryingType, VaryingType.of(ANY, ANY))
        inner = Tuple(vt, (U, INT))
        unify(LeafCarrier(ANY, T), inner, subst=uf)

        # U = str
        unify(LeafCarrier(ANY, U), LeafCarrier(ANY, STR), subst=uf)

        # Reify T should give Tuple(str, int)
        result = uf.reify(LeafCarrier(ANY, T))
        self.assertEqual(result.fetch(), (STR, INT))


if __name__ == "__main__":
    unittest.main()
