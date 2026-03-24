from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import Any, Callable, TypeVar, TypeVarTuple, Union, Unpack, cast, get_args, get_origin

from protobase import Consed, attr_info_of, flux, frozendict

from .. import core as mp
from .foundation import _ALL_BUILTINS
from .hosted import Host, Spec

type PythonTransform = Callable[..., mp.Type]

_NATIVE_SPECS: dict[type, Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}
_BOOTSTRAPPED = False


def _host_singleton() -> NativeHost:
    import protomorph.core as core_pkg  # type: ignore[import-not-found]

    return cast(NativeHost, getattr(core_pkg, "NATIVE_HOST"))


def spec_name(cls: type[mp.Builtin]) -> str:
    """Canonical anchor string for a Builtin class."""
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


class NativeHost(Host, Consed):
    @flux.property
    def all_builtins(self) -> frozenset[type[mp.Builtin]]:
        return frozenset(_ALL_BUILTINS)

    @flux.property
    def native_specs(self) -> frozendict[type, Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def template_for(self, builtin_cls: type[mp.Builtin]) -> mp.NativeType:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return mp.NativeType(builtin_cls, mp.VaryingType(mp.Index.Empty, ()))

        names = list(attrs.keys())
        types = tuple(
            self.type_from_annotation(info.type)
            for info in attrs.values()
        )
        schema = mp.VaryingType(
            mp.Index(tuple(mp.Id(n) for n in names)),
            types,
        )
        return mp.NativeType(builtin_cls, schema)

    @flux.property
    def template_by_spec_name(self) -> frozendict[str, mp.NativeType]:
        def _is_reflectable(cls: type[mp.Builtin]) -> bool:
            return not cls.__module__.startswith("protomorph.core")

        return frozendict(
            {
                spec_name(cls): self.template_for(cls)
                for cls in self.all_builtins
                if _is_reflectable(cls)
            }
        )

    @flux.method
    def type_from_annotation(
        self,
        annotation: Any,
        *,
        template: mp.NativeType | None = None,
    ) -> mp.Type:
        if isinstance(annotation, mp.Type):
            return annotation

        if annotation is mp.Type:
            return mp.Spec.of("std.metas.Type")

        if isinstance(annotation, TypeVar):
            return mp.Placeholder(template, annotation.__name__)

        if isinstance(annotation, TypeVarTuple):
            return mp.Placeholder(template, f"*{annotation.__name__}")

        scalar_spec = self.native_specs.get(annotation)
        if scalar_spec is not None:
            return scalar_spec

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union or isinstance(annotation, PEP604Union):
            return mp.UnionType.of(
                *(self.type_from_annotation(arg, template=template) for arg in args)
            )

        if origin is Unpack and args:
            return self.type_from_annotation(args[0], template=template)

        if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
            return mp.UniformType(
                self.type_from_annotation(args[0], template=template),
                mp.Index.Empty,
            )

        if origin is tuple and args:
            converted = tuple(
                self.type_from_annotation(arg, template=template) for arg in args
            )
            if (
                len(converted) == 1
                and isinstance(converted[0], mp.Placeholder)
                and converted[0].id.startswith("*")
            ):
                return converted[0]
            return cast(mp.Type, mp.VaryingType(mp.Index.Empty, converted))

        if isinstance(origin, type):
            typed_origin = cast(type, origin)
            transform = self.python_transforms.get(typed_origin)
            if transform is not None:
                converted = tuple(
                    self.type_from_annotation(arg, template=template)
                    if arg is not Ellipsis
                    else arg
                    for arg in args
                )
                return transform(*converted)

            if isinstance(typed_origin, type) and issubclass(typed_origin, mp.Builtin):
                base = self.template_for(typed_origin)
                param_types = tuple(
                    self.type_from_annotation(arg, template=template) for arg in args
                )
                cls_params = getattr(typed_origin, "__type_params__", ())
                mapping: dict[mp.Placeholder, mp.Type] = {}
                for param, concrete in zip(cls_params, param_types):
                    if isinstance(param, TypeVarTuple):
                        mapping[mp.Placeholder(template, f"*{param.__name__}")] = (
                            cast(
                                mp.Type,
                                mp.VaryingType(mp.Index.Empty, param_types[len(mapping):]),
                            )
                        )
                        break
                    mapping[mp.Placeholder(template, param.__name__)] = concrete
                return base.specialize(mapping)

        if isinstance(annotation, type) and issubclass(annotation, mp.Builtin):
            return self.template_for(annotation)

        return mp.Spec.of("std.types.Any")

    def schema_for(self, spec: Spec) -> mp.VaryingType | None:
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: Spec) -> mp.VaryingType | None:
        template = self.template_by_spec_name.get(str(spec.anchor))
        if template is None:
            return None

        cls_params = getattr(template.builtin_cls, "__type_params__", ())
        if not cls_params:
            return template.schema

        args = spec.args
        if len(args) == 0:
            return template.schema

        arg_types = tuple(c.fetch() for c in args)
        mapping: dict[mp.Placeholder, mp.Type] = {}
        for param, arg_type in zip(cls_params, arg_types):
            if isinstance(param, TypeVarTuple):
                ph = mp.Placeholder(None, f"*{param.__name__}")
                remaining = arg_types[len(mapping):]
                mapping[ph] = cast(mp.Type, mp.VaryingType(mp.Index.Empty, remaining))
                break
            ph = mp.Placeholder(None, param.__name__)
            mapping[ph] = arg_type

        return template.specialize(mapping).schema


def register(cls: type[mp.Builtin]) -> Spec:
    return Spec.of(spec_name(cls))


def register_native_spec(python_type: type, spec: Spec) -> None:
    _NATIVE_SPECS[python_type] = spec
    try:
        NativeHost.native_specs.invalidate_for(mp.NATIVE_HOST)
    except AttributeError:
        pass


def register_python_transform(origin: type, transform: PythonTransform) -> None:
    _PYTHON_TRANSFORMS[origin] = transform
    try:
        NativeHost.python_transforms.invalidate_for(mp.NATIVE_HOST)
    except AttributeError:
        pass


def type_from_annotation(
    annotation: Any,
    *,
    template: mp.NativeType | None = None,
) -> mp.Type:
    return mp.NATIVE_HOST.type_from_annotation(annotation, template=template)


def native_type(cls: type[mp.Builtin]) -> mp.NativeType:
    return _host_singleton().template_for(cls)


def wrap(obj: Any):
    """Canonical core entry point.

    - wrap(annotation/type) -> projected core descriptor
    - wrap(value) -> carrier built from the projected descriptor
    """
    if isinstance(obj, mp.Type):
        return native_type(type(obj)).make(obj)

    if isinstance(obj, type):
        if issubclass(obj, mp.Builtin):
            return native_type(cast(type[mp.Builtin], obj))
        return type_from_annotation(obj)

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        return type_from_annotation(obj)

    if isinstance(obj, mp.Builtin):
        return native_type(type(obj)).make(obj)

    descriptor = wrap(type(obj))
    if isinstance(descriptor, mp.Type):
        return descriptor.make(obj)
    raise TypeError(f"Cannot wrap value {obj!r} with inferred descriptor")


def _set_transform(value_type: mp.Type) -> mp.Type:
    return cast(mp.Type, mp.Qual.of(value_type, Spec.of("std.qualifiers.Set")))


def _map_transform(key_type: mp.Type, value_type: mp.Type) -> mp.Type:
    return cast(mp.Type, mp.Qual.of(value_type, Spec.of("std.qualifiers.Map", key_type)))


def _list_transform(value_type: mp.Type) -> mp.Type:
    return cast(mp.Type, mp.Qual.of(value_type, Spec.of("std.qualifiers.List")))


def _frozenset_transform(value_type: mp.Type) -> mp.Type:
    return cast(mp.Type, mp.Qual.of(value_type, Spec.of("std.qualifiers.FrozenSet")))


def _tuple_transform(*types: mp.Type | object) -> mp.Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(
            mp.Type,
            mp.Qual.of(cast(mp.Type, types[0]), Spec.of("std.qualifiers.List")),
        )
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(mp.Type, Spec.of("std.types.Tuple", *cast(tuple[mp.Type, ...], types)))


def _bootstrap_defaults() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    register_native_spec(int, Spec.of("std.types.Integer"))
    register_native_spec(str, Spec.of("std.types.Text"))
    register_native_spec(float, Spec.of("std.types.Decimal"))
    register_native_spec(Decimal, Spec.of("std.types.Decimal"))
    register_native_spec(bool, Spec.of("std.types.Boolean"))
    register_native_spec(NoneType, Spec.of("std.types.Empty"))

    register_python_transform(dict, _map_transform)
    register_python_transform(list, _list_transform)
    register_python_transform(set, _set_transform)
    register_python_transform(frozenset, _frozenset_transform)
    register_python_transform(tuple, _tuple_transform)

    _BOOTSTRAPPED = True
