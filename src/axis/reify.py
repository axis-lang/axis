from functools import singledispatch
from types import NoneType
from typing import Any
from protobase import Object

type ReificationCtx = dict[Any, Any]


@singledispatch
def _reify[T](object: T, ctx: ReificationCtx = {}) -> T:
    raise NotImplementedError(f"No reification for {type(object)}")


def reify[T](object: T, ctx: ReificationCtx) -> T:
    if object in ctx:
        return ctx[object]
    return _reify(object, ctx)


def reifier():
    def reifier_decorator(fn):
        return _reify.register(fn)

    return reifier_decorator


@reifier()
def _reify_atom(atom: int | float | bool | NoneType, _: ReificationCtx) -> Any:
    return atom


@reifier()
def _reify_seq(seq: tuple | list | set | frozenset, ctx: ReificationCtx) -> Any:
    return seq.__class__(reify(item, ctx) for item in seq)


@reifier()
def _reify_map(map: dict, ctx: ReificationCtx) -> Any:
    return map.__class__((reify(k), reify(v)) for k, v in map.items())


@reifier()
def _reify_object(obj: Object, ctx: ReificationCtx) -> Any:
    args, kwargs = obj.__getnewargs_ex__()
    args = _reify_seq(args, ctx)
    kwargs = _reify_map(kwargs, ctx)
    return obj.__class__(*args, **kwargs)
