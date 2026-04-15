from __future__ import annotations

from typing import Generator

import protomorph

_SKIP = object()


class _ZipMismatch(Exception):
    pass


def _zip_children(carrier: protomorph.Val) -> tuple[protomorph.Val, ...]:
    return tuple(carrier)


def _deep_zip_gen(
    master: protomorph.Val, slave: protomorph.Val,
) -> Generator[tuple[protomorph.Val, protomorph.Val], object, None]:
    stack = [(master, slave)]
    while stack:
        left, right = stack.pop()
        ctrl = yield (left, right)
        if ctrl is _SKIP:
            continue
        left_is_leaf = not left._has_structural_children()
        right_is_leaf = not right._has_structural_children()
        if left_is_leaf != right_is_leaf:
            raise _ZipMismatch
        if left_is_leaf and right_is_leaf:
            continue
        if not protomorph.compatible_structure(left.descriptor, right.descriptor):
            raise _ZipMismatch
        l_ch = _zip_children(left)
        r_ch = _zip_children(right)
        if len(l_ch) != len(r_ch):
            raise _ZipMismatch
        stack.extend(reversed(list(zip(l_ch, r_ch))))


class ZipWalker:
    __slots__ = ("_gen", "_ctrl")

    def __init__(self, master: protomorph.Val, slave: protomorph.Val):
        self._gen = _deep_zip_gen(master, slave)
        self._ctrl = None

    def __iter__(self):
        return self

    def __next__(self) -> tuple[protomorph.Val, protomorph.Val]:
        try:
            return self._gen.send(self._ctrl)
        finally:
            self._ctrl = None

    def skip(self):
        self._ctrl = _SKIP


def deep_zip(master: protomorph.Val, slave: protomorph.Val) -> ZipWalker:
    """Paired depth-first traversal of two carrier trees.

    Yields (left, right) pairs. Call walker.skip() to prevent
    descending into the current pair's children.
    """
    return ZipWalker(master, slave)
