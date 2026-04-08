from __future__ import annotations

from typing import Any, Callable

import protomorph


_MISSING = object()


class UnionFind:
    """Substitution environment with path compression, occurs check, and rollback.

    Operates on protomorph.Carrier instances. Variables are identified by the
    ``is_var`` predicate supplied at construction time.

    Designed to be shared across multiple ``unify`` calls so that bindings
    accumulate — enabling bidirectional type resolution and multi-step
    constraint solving.
    """

    __slots__ = ("_parent", "_rank", "_trail", "_var_info", "_class_info", "is_var", "info_for", "merge_info")

    def __init__(
        self,
        is_var: Callable[[protomorph.Val], bool],
        *,
        info_for: Callable[[protomorph.Val], Any | None] | None = None,
        merge_info: Callable[[Any | None, Any | None], Any | None] | None = None,
    ):
        self._parent: dict[protomorph.Val, protomorph.Val] = {}
        self._rank: dict[protomorph.Val, int] = {}
        self._trail: list[tuple] = []
        self._var_info: dict[protomorph.Val, Any] = {}
        self._class_info: dict[protomorph.Val, Any] = {}
        self.is_var = is_var
        self.info_for = _default_info_for if info_for is None else info_for
        self.merge_info = _default_merge_info if merge_info is None else merge_info

    # ── core operations ───────────────────────────────────────────

    def find(self, x: protomorph.Val) -> protomorph.Val:
        """Follow parent chain to canonical representative (with path compression)."""
        if x not in self._parent:
            self._ensure_class_info(x)
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
        self._ensure_class_info(root)
        return root

    def bind(self, var: protomorph.Val, term: protomorph.Val, *, occurs_check: bool = True) -> bool:
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

    def _link(self, a: protomorph.Val, b: protomorph.Val) -> None:
        """Make *a* point to *b*, preferring non-vars as root."""
        if self.is_var(b) and not self.is_var(a):
            a, b = b, a
        elif self.is_var(a) == self.is_var(b):
            ra, rb = self._rank.get(a, 0), self._rank.get(b, 0)
            if ra > rb:
                a, b = b, a
        self._trail.append(("b", a, self._parent.get(a)))
        self._parent[a] = b
        self._merge_class_info(a, b)
        ra, rb = self._rank.get(a, 0), self._rank.get(b, 0)
        if ra == rb:
            self._trail.append(("r", b, rb))
            self._rank[b] = rb + 1

    def _occurs(self, var: protomorph.Val, term: protomorph.Val) -> bool:
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
        assert 0 <= mark <= len(self._trail), (
            f"Invalid rollback mark {mark!r}: trail has {len(self._trail)} entries"
        )
        while len(self._trail) > mark:
            tag, node, old = self._trail.pop()
            if tag == "r":
                self._rank[node] = old
            elif tag == "i":
                if old is _MISSING:
                    self._class_info.pop(node, None)
                else:
                    self._class_info[node] = old
            else:  # "b" or "c"
                if old is None:
                    self._parent.pop(node, None)
                else:
                    self._parent[node] = old

    def variable_info(self, var: protomorph.Val) -> Any | None:
        if var in self._var_info:
            return self._var_info[var]
        info = self.info_for(var)
        if info is not None:
            self._var_info[var] = info
        return info

    def class_info(self, carrier: protomorph.Val) -> Any | None:
        root = self.find(carrier)
        self._ensure_class_info(root)
        return self._class_info.get(root)

    def set_class_info(self, carrier: protomorph.Val, info: Any | None) -> None:
        root = self.find(carrier)
        self._trail.append(("i", root, self._class_info.get(root, _MISSING)))
        if info is None:
            self._class_info.pop(root, None)
        else:
            self._class_info[root] = info

    # ── reification ───────────────────────────────────────────────

    def reify(self, carrier: protomorph.Val, _seen: set | None = None) -> protomorph.Val:
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
        children: list[protomorph.Val] = []
        for child in carrier:
            reified = self.reify(child, _seen)
            if reified is not child:
                changed = True
            children.append(reified)
        if not changed:
            return carrier
        return carrier.reconstruct(tuple(children))

    def _ensure_class_info(self, root: protomorph.Val) -> None:
        if root in self._class_info:
            return
        if not self.is_var(root):
            return
        info = self.variable_info(root)
        if info is not None:
            self._class_info[root] = info

    def _merge_class_info(self, a: protomorph.Val, b: protomorph.Val) -> None:
        self._ensure_class_info(a)
        self._ensure_class_info(b)
        merged = self.merge_info(self._class_info.get(a), self._class_info.get(b))
        self._trail.append(("i", b, self._class_info.get(b, _MISSING)))
        if merged is None:
            self._class_info.pop(b, None)
        else:
            self._class_info[b] = merged
        if a is b:
            return
        self._trail.append(("i", a, self._class_info.get(a, _MISSING)))
        self._class_info.pop(a, None)


# ── walk ──────────────────────────────────────────────────────────


def _walk(
    a: protomorph.Val,
    b: protomorph.Val,
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
    a: protomorph.Val,
    b: protomorph.Val,
    *,
    is_var: Callable[[protomorph.Val], bool] | None = None,
    subst: UnionFind | None = None,
    occurs_check: bool = True,
    op: Callable | None = None,  # backward compat, ignored
) -> protomorph.Val | None:
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


def _default_info_for(_: protomorph.Val) -> Any | None:
    return None


def _default_merge_info(left: Any | None, right: Any | None) -> Any | None:
    if left is None:
        return right
    if right is None:
        return left
    if isinstance(left, frozenset) and isinstance(right, frozenset):
        return left | right
    return right if left != right else left
