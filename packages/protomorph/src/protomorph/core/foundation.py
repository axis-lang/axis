from __future__ import annotations

from typing import Any, Iterator, Self

from protobase import Consed, frozendict
from protomorph import core

ITERATIVE_TRAVERSAL = True
_RECONSTRUCT = object()
_default_is_leaf = lambda v: v.is_leaf


# ── Foundation ──────────────────────────────────────────────────────────


_ALL_BUILTINS: set[type[Builtin]] = set()


class Builtin(Consed):
    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not abstract:
            _ALL_BUILTINS.add(cls)


type Discriminant = Meta

type Data = (
    int
    | str
    | float
    | bool
    | None
    | Builtin
    | Discriminant
    | tuple["Data", ...]
    | frozenset["Data"]
    | frozendict["Data", "Data"]
    | frozendict[Discriminant, "Data"]
    # | Callable[[Meta, Data], Meta]] # Ground payloads are callables that take the ground meta and the data and produce a new meta
    | type[Meta]
)


class Pure[M: Meta = Any, D: Data = Any](Builtin, abstract=True):
    __meta__: M
    __data__: D


class Val[M: Meta = Any, D: Data = Any](Pure[M, D], abstract=True):


    def meta_chain(self) -> Iterator[Meta]:
        m = self.__meta__
        while m is not OMEGA:
            yield m
            m = m.__meta__
        yield OMEGA

    def restructure(self, f) -> Self:
        def _walk(meta: Meta) -> Meta:
            result = f(meta)
            if result is not meta:
                return result
            if meta is OMEGA:
                return meta
            return meta.__class__(_walk(meta.__meta__), meta.__data__)

        return self.__class__(_walk(self.__meta__), self.__data__)

    # ── Structural algebra ──────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return True

    def children(self) -> tuple[Val, ...]:
        return ()

    def reconstruct(self, children: tuple[Val, ...]) -> Self:
        return self

    # ── Derived traversals ──────────────────────────────────────────

    if ITERATIVE_TRAVERSAL:

        def deep_iter(self, is_leaf=None) -> Iterator[Val]:
            _is_leaf = is_leaf or _default_is_leaf
            stack = [self]
            while stack:
                node = stack.pop()
                if _is_leaf(node):
                    yield node
                else:
                    stack.extend(reversed(node.children()))

        def deep_map(self, f, is_leaf=None) -> Val:
            _is_leaf = is_leaf or _default_is_leaf
            stack: list = [self]
            results: list[Val] = []
            while stack:
                item = stack.pop()
                if item is _RECONSTRUCT:
                    node, n = stack.pop()
                    new_children = tuple(results[len(results) - n :])
                    del results[len(results) - n :]
                    results.append(node.reconstruct(new_children))
                elif _is_leaf(item):
                    results.append(f(item))
                else:
                    children = item.children()
                    stack.append((item, len(children)))
                    stack.append(_RECONSTRUCT)
                    stack.extend(reversed(children))
            return results[0]

        def search(self, target: Val) -> bool:
            stack = [self]
            while stack:
                node = stack.pop()
                if node == target:
                    return True
                if not node.is_leaf:
                    stack.extend(node.children())
            return False

    else:

        def deep_iter(self, is_leaf=None) -> Iterator[Val]:
            _is_leaf = is_leaf or _default_is_leaf
            if _is_leaf(self):
                yield self
            else:
                for child in self.children():
                    yield from child.deep_iter(is_leaf)

        def deep_map(self, f, is_leaf=None) -> Val:
            _is_leaf = is_leaf or _default_is_leaf
            if _is_leaf(self):
                return f(self)
            new_children = tuple(c.deep_map(f, is_leaf) for c in self.children())
            return self.reconstruct(new_children)

        def search(self, target: Val) -> bool:
            if self == target:
                return True
            if self.is_leaf:
                return False
            return any(c.search(target) for c in self.children())

    def subst(self, mapping) -> Val:
        def _is_leaf(v):
            return v in mapping or v.is_leaf

        return self.deep_map(lambda v: mapping.get(v, v), is_leaf=_is_leaf)


class Meta[M: Meta = Any, D: Data = Any](Val[M, D], abstract=True):

    def wrap(self, data: Data) -> Val:
        raise NotImplementedError(f"{type(self).__name__}.wrap not implemented")

    def accepts(self, data: Data) -> bool:
        try:
            self.wrap(data)
            return True
        except (TypeError, ValueError, AssertionError, NotImplementedError):
            return False

    def is_subtype(self, other: Meta) -> bool:
        from .variant import Union

        if self is other or self == other:
            return True
        if isinstance(other, Union):
            if isinstance(self, Union):
                return self.variants <= other.variants
            return self in other.variants
        return False


# ── Omega ──────────────────────────────────────────────────────────


class Omega(Meta["Omega", None]):
    def __repr__(self) -> str:
        return "<Omega>"

    def wrap(self, data: Data) -> Val:
        return Ground(self, data)


OMEGA = object.__new__(Omega)
object.__setattr__(OMEGA, "__meta__", OMEGA)
object.__setattr__(OMEGA, "__data__", None)
object.__setattr__(OMEGA, "__hash_cache__", hash((id(OMEGA), None)))
OMEGA.__consign__[(OMEGA, None)] = OMEGA

# ── Ground ─────────────────────────────────────────────────────────────


class Ground(Meta[Omega, type[Meta]]):
    def wrap(self, data: Data) -> Val:
        return self.__data__(self, data)


def ground(carrier: type[Meta]) -> Ground:
    return Ground(OMEGA, carrier)
