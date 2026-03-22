from __future__ import annotations

from typing import Generator

from .foundation import Val, ITERATIVE_TRAVERSAL

_SKIP = object()


if ITERATIVE_TRAVERSAL:

    def _deep_zip_gen(
        master: Val, slave: Val,
    ) -> Generator[tuple[Val, Val], object, None]:
        stack = [(master, slave)]
        while stack:
            left, right = stack.pop()
            ctrl = yield (left, right)
            if ctrl is _SKIP:
                continue
            if left.is_leaf or right.is_leaf:
                continue
            l_ch = left.children()
            r_ch = right.children()
            if len(l_ch) != len(r_ch):
                continue
            stack.extend(reversed(list(zip(l_ch, r_ch))))

else:

    def _deep_zip_gen(
        left: Val, right: Val,
    ) -> Generator[tuple[Val, Val], object, None]:
        ctrl = yield (left, right)
        if ctrl is _SKIP:
            return
        if left.is_leaf or right.is_leaf:
            return
        l_ch = left.children()
        r_ch = right.children()
        if len(l_ch) != len(r_ch):
            return
        for lc, rc in zip(l_ch, r_ch):
            yield from _deep_zip_gen(lc, rc)


class ZipWalker:
    __slots__ = ("_gen", "_ctrl")

    def __init__(self, master: Val, slave: Val):
        self._gen = _deep_zip_gen(master, slave)
        self._ctrl = None

    def __iter__(self):
        return self

    def __next__(self) -> tuple[Val, Val]:
        try:
            return self._gen.send(self._ctrl)
        finally:
            self._ctrl = None

    def skip(self):
        self._ctrl = _SKIP


def deep_zip(master: Val, slave: Val) -> ZipWalker:
    return ZipWalker(master, slave)
