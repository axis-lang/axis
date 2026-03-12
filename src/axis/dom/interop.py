"""Python <-> Axis DOM type interop."""

from __future__ import annotations

from types import UnionType as PEP604Union
from typing import Any, Callable, TypeVar, Union, cast, get_args, get_origin

from axis import dom
from .introspection import VarGenericType, drain_pending


_PY_TO_AX_TRANSFORMS: dict[object, Callable[..., dom.Type]] = {}


def register_py_to_ax(origin: object, transform: Callable[..., dom.Type]) -> None:
    _PY_TO_AX_TRANSFORMS[origin] = transform


def python_to_axis_type(
    annotation: Any,
    ctx: dom.ContextProto,
    vars: set[dom.Var] | None = None,
) -> dom.Type:
    if annotation is Any:
        return dom.ANY_TYPE

    if isinstance(annotation, TypeVar):
        var = dom.var(VarGenericType, ctx, annotation.__name__)  # type: ignore[arg-type]
        if vars is not None:
            vars.add(var)
        return var

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        return dom.union_type(*[python_to_axis_type(arg, ctx, vars) for arg in args])

    scalar = dom.TYPE_BY_NATIVE.get(annotation)
    if scalar is not None:
        return scalar

    if origin is not None:
        return _transform_generic(origin, args, ctx, vars)

    if isinstance(annotation, type):
        return _try_builtin_mapping(annotation)

    return dom.ANY_TYPE


class _TypeBuildContext(dom.ContextProto):
    def lookup_bound(self, name: str) -> dom.Type | None:
        return None


_TYPE_BUILD_CTX = _TypeBuildContext()


def _coerce_builtin_type_arg(arg: type | dom.Type) -> dom.Type:
    if isinstance(arg, dom.Type):
        return arg

    projected = python_to_axis_type(arg, ctx=_TYPE_BUILD_CTX)
    if projected is dom.ANY_TYPE and arg is not Any:
        raise TypeError(f"Cannot project Builtin type argument {arg!r} to dom.Type")
    return projected


def _validate_builtin_type_arg(
    param: TypeVar,
    raw_arg: type | dom.Type,
    projected_arg: dom.Type,
) -> None:
    _ = (param, raw_arg, projected_arg)


def build_builtin_type(
    builtin_cls: type[dom.Builtin],
    *args: type | dom.Type,
) -> dom.Type:
    parameters = tuple(getattr(builtin_cls, "__parameters__", ()))
    expected = len(parameters)
    received = len(args)

    if expected == 0:
        if received != 0:
            raise TypeError(
                f"{builtin_cls.__name__} expects no type arguments, got {received}"
            )
        return dom.nominal_type(builtin_cls._anchor_path())

    if received != expected:
        raise TypeError(
            f"{builtin_cls.__name__} expects {expected} type arguments, got {received}"
        )

    projected_args = tuple(_coerce_builtin_type_arg(arg) for arg in args)

    bindings: dict[str, dom.Type] = {}
    for param, raw_arg, projected_arg in zip(parameters, args, projected_args):
        if isinstance(param, TypeVar):
            _validate_builtin_type_arg(param, raw_arg, projected_arg)

        name = getattr(param, "__name__", None)
        if not isinstance(name, str):
            raise TypeError(
                f"Unsupported type parameter {param!r} in {builtin_cls.__name__}"
            )
        bindings[name] = projected_arg

    return dom.nominal_type(builtin_cls._anchor_path(), _spec_from_types(**bindings))


def builtin_runtime_type_args(value: dom.Builtin) -> tuple[type | dom.Type, ...] | None:
    orig_class = getattr(value, "__orig_class__", None)
    if orig_class is None:
        return None

    origin = get_origin(orig_class)
    if origin is None or not isinstance(origin, type) or origin is not value.__class__:
        return None

    runtime_args = get_args(orig_class)
    if not runtime_args:
        return ()

    extracted: list[type | dom.Type] = []
    for arg in runtime_args:
        if isinstance(arg, dom.Type) or isinstance(arg, type):
            extracted.append(arg)
        else:
            return None
    return tuple(extracted)


def _transform_generic(
    origin: object,
    args: tuple[Any, ...],
    ctx: dom.ContextProto,
    vars: set[dom.Var] | None,
) -> dom.Type:
    transform = _PY_TO_AX_TRANSFORMS.get(origin)
    if transform is not None:
        converted = tuple(
            python_to_axis_type(arg, ctx, vars) if arg is not Ellipsis else arg
            for arg in args
        )
        return transform(*converted)

    if isinstance(origin, type) and issubclass(origin, dom.Builtin):
        builtin_origin = cast(type[dom.Builtin], origin)
        return builtin_origin._type(*cast(tuple[type | dom.Type, ...], args))

    return dom.ANY_TYPE


def _try_builtin_mapping(annotation: type) -> dom.Type:
    drain_pending()
    if issubclass(annotation, dom.Builtin):
        return cast(type[dom.Builtin], annotation)._type()
    return dom.ANY_TYPE


def _spec_from_types(**bindings: dom.Type) -> dom.Const | None:
    if not bindings:
        return None
    return dom.struct(
        **{name: cast(dom.Const | dom.Var, dom.val(t)) for name, t in bindings.items()}
    )


def _tuple_transform(*args: dom.Type) -> dom.Type:
    if len(args) == 2 and args[1] is Ellipsis:
        return dom.nominal_qual("std.List", _spec_from_types(), underlying=args[0])
    return dom.StructType(meta_attrs=dom.Struct.new(*args))
