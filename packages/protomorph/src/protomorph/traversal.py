from __future__ import annotations

from typing import Generator

import protomorph

_SKIP = object()


class _ZipMismatch(Exception):
    pass


def _deep_zip_gen(
    master: protomorph.Carrier, slave: protomorph.Carrier,
) -> Generator[tuple[protomorph.Carrier, protomorph.Carrier], object, None]:
    stack = [(master, slave)]
    while stack:
        left, right = stack.pop()
        ctrl = yield (left, right)
        if ctrl is _SKIP:
            continue
        if left.is_leaf or right.is_leaf:
            continue
        if left.descriptor != right.descriptor:
            raise _ZipMismatch
        l_ch = list(left)
        r_ch = list(right)
        if len(l_ch) != len(r_ch):
            raise _ZipMismatch
        stack.extend(reversed(list(zip(l_ch, r_ch))))


class ZipWalker:
    __slots__ = ("_gen", "_ctrl")

    def __init__(self, master: protomorph.Carrier, slave: protomorph.Carrier):
        self._gen = _deep_zip_gen(master, slave)
        self._ctrl = None

    def __iter__(self):
        return self

    def __next__(self) -> tuple[protomorph.Carrier, protomorph.Carrier]:
        try:
            return self._gen.send(self._ctrl)
        finally:
            self._ctrl = None

    def skip(self):
        self._ctrl = _SKIP


def deep_zip(master: protomorph.Carrier, slave: protomorph.Carrier) -> ZipWalker:
    """Paired depth-first traversal of two carrier trees.

    Yields (left, right) pairs. Call walker.skip() to prevent
    descending into the current pair's children.
    """
    return ZipWalker(master, slave)
