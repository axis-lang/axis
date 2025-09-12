# %%
from functools import singledispatch
from types import MappingProxyType
from typing import Any, DefaultDict, Dict, Iterable
from protobase import Object, Consed, attrs_of


class UnifyVar(Object):  # Entity
    "Unification Variable"

    name: str


type UnificationPair = tuple[UnifyVar, Any]


class NotUnifiable(Exception):
    pass


class Unification(Consed): ...


@singledispatch
def gen_unification(a, b) -> Iterable[UnificationPair]:
    raise NotImplementedError(f"No unification for {type(a)} and {type(b)}")


def unify(a, *objs) -> DefaultDict[UnifyVar, set]:
    unification = DefaultDict(set)

    for obj in objs:
        for var, val in gen_unification(a, obj):
            unification[var].add(val)

    return dict(unification)


def unifier():
    def unifier_decorator(fn):
        return gen_unification.register(fn)

    return unifier_decorator


@unifier()
def _unify_var(a: UnifyVar, b: Any) -> Iterable[UnificationPair]:
    yield a, b


@unifier()
def _unify_object(a: Object, b: Any):
    if a == b:
        return {}

    if not isinstance(b, type(a)):
        raise NotUnifiable(f"Cannot unify {type(a)} with {type(b)}")

    for attr in attrs_of(type(a)):

        x = getattr(a, attr)
        y = getattr(b, attr)

        if x != y:
            yield from gen_unification(x, y)  # debe hacer un merge de los sets


class MyType(Object):
    a: int
    b: str
    c: float


class MyType2(Object):
    a: int
    b: str
    c: float


print(unify(MyType(a=1, b=UnifyVar("Alpha"), c=3.0), MyType(a=1, b="hey", c=3.0)))
