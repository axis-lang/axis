from __future__ import annotations

from types import UnionType as PEP604Union
from typing import Any, TypeVar, TypeVarTuple, Union, Unpack, get_args, get_origin

from .. import core as mp


def type_from_annotation(
    annotation: Any, *, template: mp.NativeType | None = None
) -> mp.Type:
    """Map a Python type annotation to a Type."""

    if isinstance(annotation, mp.Type):
        return annotation

    # Type itself → OMEGA (the classifier of types)
    if annotation is mp.Type:
        return mp.OMEGA

    # TypeVar → Placeholder
    if isinstance(annotation, TypeVar):
        return mp.Placeholder(template, annotation.__name__)

    # TypeVarTuple → Placeholder (will expand to VaryingType on specialization)
    if isinstance(annotation, TypeVarTuple):
        return mp.Placeholder(template, f"*{annotation.__name__}")

    scalar = mp._SCALAR_TYPES.get(annotation)
    if scalar is not None:
        return scalar

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Union / X | Y
    if origin is Union or isinstance(annotation, PEP604Union):
        return mp.UnionType.of(*(type_from_annotation(a, template=template) for a in args))

    # Unpack[T] (from tuple[*T]) → delegate to the TypeVarTuple inside
    if origin is Unpack and args:
        return type_from_annotation(args[0], template=template)

    # tuple[T, ...] → UniformType
    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return mp.UniformType(type_from_annotation(args[0], template=template))

    # tuple[*T] → Placeholder (single Unpack arg)
    # tuple[A, B, C] → VaryingType
    if origin is tuple and args:
        converted = tuple(type_from_annotation(a, template=template) for a in args)
        # If single element and it's a spread placeholder (*T), return it directly
        if len(converted) == 1 and isinstance(converted[0], mp.Placeholder) and converted[0].id.startswith("*"):
            return converted[0]
        return mp.VaryingType.make(*converted)

    # Parameterized Builtin: B[int, str, float]
    if isinstance(origin, type) and issubclass(origin, mp.Builtin):
        base = native_type(origin, template=template)
        param_types = tuple(type_from_annotation(a, template=template) for a in args)
        # Build mapping from class type params to concrete types
        cls_params = getattr(origin, "__type_params__", ())
        mapping: dict[mp.Placeholder, mp.Type] = {}
        for param, concrete in zip(cls_params, param_types):
            if isinstance(param, TypeVarTuple):
                # Spread: *T → VaryingType of the remaining args
                mapping[mp.Placeholder(template, f"*{param.__name__}")] = mp.VaryingType.make(*param_types[len(mapping):])
                break
            else:
                mapping[mp.Placeholder(template, param.__name__)] = concrete
        return base.specialize(mapping)

    if isinstance(annotation, type) and issubclass(annotation, mp.Builtin):
        return native_type(annotation, template=template)

    return mp.OMEGA  # fallback for unresolvable annotations


def native_type(
    cls: type[mp.Builtin], *, template: mp.NativeType | None = None
) -> mp.NativeType:
    """Build a NativeType with a reflected schema from class annotations."""
    from protobase import attr_info_of

    attrs = attr_info_of(cls)
    if not attrs:
        return mp.NativeType(cls, mp.VaryingType.make())

    names = list(attrs.keys())
    types = tuple(
        type_from_annotation(info.type, template=template)
        for info in attrs.values()
    )
    schema = mp.VaryingType.make(**{n: t for n, t in zip(names, types)})
    return mp.NativeType(cls, schema)


def wrap(obj: mp.Builtin) -> mp.NativeObjectCarrier:
    """Wrap a Builtin instance in a carrier with its reflected type."""
    return mp.NativeObjectCarrier(native_type(type(obj)), obj)
