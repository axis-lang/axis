from __future__ import annotations

from typing import Callable

import pm


class UnionFind:
    """Substitution environment with path compression, occurs check, and rollback.

    Operates on pm.Carrier instances. Variables are identified by the
    ``is_var`` predicate supplied at construction time.

    Designed to be shared across multiple ``unify`` calls so that bindings
    accumulate — enabling bidirectional type resolution and multi-step
    constraint solving.
    """

    __slots__ = ("_parent", "_rank", "_trail", "is_var")

    def __init__(self, is_var: Callable[[pm.Carrier], bool]):
        self._parent: dict[pm.Carrier, pm.Carrier] = {}
        self._rank: dict[pm.Carrier, int] = {}
        self._trail: list[tuple] = []
        self.is_var = is_var

    # ── core operations ───────────────────────────────────────────

    def find(self, x: pm.Carrier) -> pm.Carrier:
        """Follow parent chain to canonical representative (with path compression)."""
        if x not in self._parent:
            return x
        root = x
        while root in self._parent:
            root = self._parent[root]
        curr = x
        while curr is not root:
            nxt = self._parent[curr]
            if nxt is not root:
                self._trail.append(("c", curr, nxt))
                self._parent[curr] = root
            curr = nxt
        return root

    def bind(self, var: pm.Carrier, term: pm.Carrier, *, occurs_check: bool = True) -> bool:
        """Bind *var* to *term*. Returns False if occurs check fails."""
        rv = self.find(var)
        rt = self.find(term)
        if rv is rt:
            return True
        if occurs_check and not self.is_var(rt) and not rt.is_leaf:
            if self._occurs(rv, rt):
                return False
        self._link(rv, rt)
        return True

    def _link(self, a: pm.Carrier, b: pm.Carrier) -> None:
        """Make *a* point to *b*, preferring non-vars as root."""
        if self.is_var(b) and not self.is_var(a):
            a, b = b, a
        elif self.is_var(a) == self.is_var(b):
            ra, rb = self._rank.get(a, 0), self._rank.get(b, 0)
            if ra > rb:
                a, b = b, a
        self._trail.append(("b", a, self._parent.get(a)))
        self._parent[a] = b
        ra, rb = self._rank.get(a, 0), self._rank.get(b, 0)
        if ra == rb:
            self._trail.append(("r", b, rb))
            self._rank[b] = rb + 1

    def _occurs(self, var: pm.Carrier, term: pm.Carrier) -> bool:
        """Return True if *var* appears anywhere inside *term*."""
        term = self.find(term)
        if var is term:
            return True
        if term.is_leaf:
            return False
        return any(self._occurs(var, child) for child in term)

    # ── snapshot / rollback ───────────────────────────────────────

    def snapshot(self) -> int:
        """Return an opaque mark for later rollback."""
        return len(self._trail)

    def rollback(self, mark: int) -> None:
        """Undo all operations since *mark*."""
        while len(self._trail) > mark:
            tag, node, old = self._trail.pop()
            if tag == "r":
                self._rank[node] = old
            else:  # "b" or "c"
                if old is None:
                    self._parent.pop(node, None)
                else:
                    self._parent[node] = old

    # ── reification ───────────────────────────────────────────────

    def reify(self, carrier: pm.Carrier, _seen: set | None = None) -> pm.Carrier:
        """Deep-substitute all bound variables in *carrier*."""
        if self.is_var(carrier):
            root = self.find(carrier)
            if root is carrier:
                return carrier  # unbound variable
            if _seen is not None and id(carrier) in _seen:
                return carrier  # cycle detected
            seen = _seen or set()
            seen.add(id(carrier))
            return self.reify(root, seen)
        if carrier.is_leaf:
            return carrier
        changed = False
        children: list[pm.Carrier] = []
        for child in carrier:
            reified = self.reify(child, _seen)
            if reified is not child:
                changed = True
            children.append(reified)
        if not changed:
            return carrier
        return carrier.reconstruct(tuple(children))


# ── walk ──────────────────────────────────────────────────────────


def _walk(
    a: pm.Carrier,
    b: pm.Carrier,
    uf: UnionFind,
    occurs_check: bool,
) -> bool:
    """Structural unification walk. Mutates *uf* with bindings."""
    stack = [(a, b)]
    while stack:
        left, right = stack.pop()
        left = uf.find(left)
        right = uf.find(right)

        if left is right:
            continue

        l_var = uf.is_var(left)
        r_var = uf.is_var(right)

        if l_var or r_var:
            var, term = (left, right) if l_var else (right, left)
            if not uf.bind(var, term, occurs_check=occurs_check):
                return False
            continue

        # both non-var
        if left.is_leaf and right.is_leaf:
            if left != right:
                return False
            continue

        if left.is_leaf != right.is_leaf:
            return False

        l_ch = list(left)
        r_ch = list(right)
        if len(l_ch) != len(r_ch):
            return False

        stack.extend(zip(reversed(l_ch), reversed(r_ch)))

    return True


# ── public API ────────────────────────────────────────────────────


def unify(
    a: pm.Carrier,
    b: pm.Carrier,
    *,
    is_var: Callable[[pm.Carrier], bool] | None = None,
    subst: UnionFind | None = None,
    occurs_check: bool = True,
    op: Callable | None = None,  # backward compat, ignored
) -> pm.Carrier | None:
    """Unify two carrier trees.

    Accepts either an ``is_var`` predicate (creates a fresh UnionFind) or
    a shared ``subst`` (accumulates bindings across calls).

    Returns the reified result rooted at *a*, or None on failure.
    """
    if subst is not None:
        uf = subst
    elif is_var is not None:
        uf = UnionFind(is_var)
    else:
        raise TypeError("Either is_var or subst must be provided")

    if not _walk(a, b, uf, occurs_check):
        return None

    return uf.reify(a)
