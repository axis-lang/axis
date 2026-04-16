from __future__ import annotations

from collections.abc import Iterator as _Iterator, Mapping as _Mapping
from typing import Any as _Any, Callable as _Callable, cast as _cast

import protomorph.core as _pm

_RECONSTRUCT = object()

class _ZipMismatch(Exception):
    pass


def _children(node: _pm.Val) -> tuple[_pm.Val, ...]:
    return tuple(node.children)


def _validate_zip_pair(
    left: _pm.Val, right: _pm.Val
) -> tuple[tuple[_pm.Val, _pm.Val], ...]:
    left_children = _children(left)
    right_children = _children(right)

    if not left_children and not right_children:
        return ()
    if not left_children or not right_children:
        raise _ZipMismatch
    if not _pm.compatible(left.descriptor, right.descriptor):
        raise _ZipMismatch
    if len(left_children) != len(right_children):
        raise _ZipMismatch

    return tuple(reversed(tuple(zip(left_children, right_children, strict=True))))


class ZipWalker(_Iterator[tuple[_pm.Val, _pm.Val]]):
    __slots__ = ("_pairs", "_pending", "_skip_children")

    def __init__(self, master: _pm.Val, slave: _pm.Val):
        self._pairs: list[tuple[_pm.Val, _pm.Val]] = [(master, slave)]
        self._pending: tuple[_pm.Val, _pm.Val] | None = None
        self._skip_children = False

    def __iter__(self) -> ZipWalker:
        return self

    def __next__(self) -> tuple[_pm.Val, _pm.Val]:
        if self._pending is not None:
            if not self._skip_children:
                self._pairs.extend(_validate_zip_pair(*self._pending))
            self._pending = None
            self._skip_children = False

        if not self._pairs:
            raise StopIteration

        pair = self._pairs.pop()
        self._pending = pair
        return pair

    def skip(self) -> None:
        self._skip_children = True


def deep_zip(master: _pm.Val, slave: _pm.Val) -> ZipWalker:
    """Paired depth-first traversal of two carrier trees.

    Yields `(left, right)` pairs in pre-order. Call `walker.skip()` after receiving
    a pair to avoid descending into that pair's children.
    """

    return ZipWalker(master, slave)


def walk(value: _pm.Val) -> _Iterator[_pm.Val]:
    stack: list[_pm.Val] = [value]
    while stack:
        node = stack.pop()
        yield node
        if len(node.children) > 0:
            stack.extend(reversed(tuple(node.children)))


def walk_leafs(value: _pm.Val) -> _Iterator[_pm.Val]:
    return (node for node in walk(value) if len(node.children) == 0)


def walk_branches(value: _pm.Val) -> _Iterator[_pm.Val]:
    return (node for node in walk(value) if len(node.children) > 0)


def walk_map(
    value: _pm.Val,
    f: _Callable[[_pm.Val], _pm.Val],
    is_leaf: _Callable[[_pm.Val], bool] | None = None,
) -> _pm.Val:
    is_leaf_fn = is_leaf or (lambda carrier: len(carrier.children) == 0)
    stack: list[_Any] = [value]
    results: list[_pm.Val] = []
    while stack:
        item = stack.pop()
        if item is _RECONSTRUCT:
            node, size = stack.pop()
            new_children = tuple(results[len(results) - size :])
            del results[len(results) - size :]
            results.append(node.reconstruct(new_children))
            continue
        if is_leaf_fn(item):
            results.append(f(item))
            continue
        children = list(item.children)
        stack.append((item, len(children)))
        stack.append(_RECONSTRUCT)
        stack.extend(reversed(children))
    return results[0]


def walk_subst(value: _pm.Val, mapping: _Mapping[_pm.Val, _pm.Val]) -> _pm.Val:
    if not mapping:
        return value
    return walk_map(
        value,
        lambda carrier: mapping.get(carrier, carrier),
        is_leaf=lambda carrier: carrier in mapping or len(carrier.children) == 0,
    )


def subst_where(
    value: _pm.Val,
    pred: _Callable[[_pm.Val], bool],
    replace: _Callable[[_pm.Val], _pm.Val],
) -> _pm.Val:
    mapping: dict[_pm.Val, _pm.Val] = {}
    for leaf in walk_leafs(value):
        if pred(leaf):
            mapping[leaf] = replace(leaf)
    return value if not mapping else walk_subst(value, mapping)


def subst_marks(value: _pm.Val, mapping: _Mapping[_pm.Mark, _pm.Val | _pm.Datum]) -> _pm.Val:
    def pred(leaf: _pm.Val) -> bool:
        value = leaf.fetch()
        return isinstance(value, _pm.Mark) and value in mapping

    def replace(leaf: _pm.Val) -> _pm.Val:
        value = _cast(_pm.Mark, leaf.fetch())
        replacement = mapping[value]
        if isinstance(replacement, _pm.Val):
            return replacement
        return _pm.val(replacement)

    return subst_where(value, pred, replace)


def subst_self(value: _pm.Val, subject: _pm.Val | _pm.Datum) -> _pm.Val:
    replacement = subject if isinstance(subject, _pm.Val) else _pm.val(subject)
    return subst_marks(value, {_pm.SELF: replacement})


def walk_search(value: _pm.Val, target: _pm.Val) -> bool:
    stack: list[_pm.Val] = [value]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if len(node.children) > 0:
            stack.extend(node.children)
    return False


# Temporary aliases during rename to the walk* family.
deep_iter = walk
iter_leafs = walk_leafs
iter_branches = walk_branches
deep_map = walk_map
deep_subst = walk_subst
deep_search = walk_search
