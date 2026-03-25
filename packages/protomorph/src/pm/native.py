from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import Any, Callable, TypeVar, TypeVarTuple, Union, Unpack, cast, get_args, get_origin

from protobase import Consed, attr_info_of, flux, frozendict

import pm
from .foundation import _ALL_BUILTINS
from .hosted import Host, Spec

type PythonTransform = Callable[..., pm.Type]

_NATIVE_SPECS: dict[type, Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}
_BOOTSTRAPPED = False


def _host_singleton() -> NativeHost:
    return pm.NATIVE_HOST
    import protomorph.core as core_pkg  # type: ignore[import-not-found]
    return cast(NativeHost, getattr(core_pkg, "NATIVE_HOST"))


def spec_name(cls: type[pm.Builtin]) -> str:
    """Canonical anchor string for a Builtin class."""
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


class NativeHost(Host, Consed):
    @flux.property
    def all_builtins(self) -> frozenset[type[pm.Builtin]]:
        return frozenset(_ALL_BUILTINS)

    @flux.property
    def native_specs(self) -> frozendict[type, Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def template_for(self, builtin_cls: type[pm.Builtin]) -> pm.NativeType:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return pm.NativeType(builtin_cls, pm.VaryingType(pm.Index.Empty, ()))

        names = list(attrs.keys())
        types = tuple(
            self.type_from_annotation(info.type)
            for info in attrs.values()
        )
        schema = pm.VaryingType(
            pm.Index(tuple(pm.Id(n) for n in names)),
            types,
        )
        return pm.NativeType(builtin_cls, schema)

    @flux.property
    def template_by_spec_name(self) -> frozendict[str, pm.NativeType]:
        def _is_reflectable(cls: type[pm.Builtin]) -> bool:
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
        template: pm.NativeType | None = None,
    ) -> pm.Type:
        if isinstance(annotation, pm.Type):
            return annotation

        if annotation is pm.Type:
            return pm.Spec.of("std.metas.Type")

        if isinstance(annotation, TypeVar):
            return pm.Placeholder(template, annotation.__name__)

        if isinstance(annotation, TypeVarTuple):
            return pm.Placeholder(template, f"*{annotation.__name__}")

        scalar_spec = self.native_specs.get(annotation)
        if scalar_spec is not None:
            return scalar_spec

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union or isinstance(annotation, PEP604Union):
            return pm.UnionType.of(
                *(self.type_from_annotation(arg, template=template) for arg in args)
            )

        if origin is Unpack and args:
            return self.type_from_annotation(args[0], template=template)

        if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
            return pm.UniformType(
                self.type_from_annotation(args[0], template=template),
                pm.Index.Empty,
            )

        if origin is tuple and args:
            converted = tuple(
                self.type_from_annotation(arg, template=template) for arg in args
            )
            if (
                len(converted) == 1
                and isinstance(converted[0], pm.Placeholder)
                and converted[0].id.startswith("*")
            ):
                return converted[0]
            return cast(pm.Type, pm.VaryingType(pm.Index.Empty, converted))

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

            if isinstance(typed_origin, type) and issubclass(typed_origin, pm.Builtin):
                base = self.template_for(typed_origin)
                param_types = tuple(
                    self.type_from_annotation(arg, template=template) for arg in args
                )
                cls_params = getattr(typed_origin, "__type_params__", ())
                mapping: dict[pm.Placeholder, pm.Type] = {}
                for param, concrete in zip(cls_params, param_types):
                    if isinstance(param, TypeVarTuple):
                        mapping[pm.Placeholder(template, f"*{param.__name__}")] = (
                            cast(
                                pm.Type,
                                pm.VaryingType(pm.Index.Empty, param_types[len(mapping):]),
                            )
                        )
                        break
                    mapping[pm.Placeholder(template, param.__name__)] = concrete
                return base.specialize(mapping)

        if isinstance(annotation, type) and issubclass(annotation, pm.Builtin):
            return self.template_for(annotation)

        return pm.Spec.of("std.types.Any")

    def schema_for(self, spec: Spec) -> pm.VaryingType | None:
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: Spec) -> pm.VaryingType | None:
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
        mapping: dict[pm.Placeholder, pm.Type] = {}
        for param, arg_type in zip(cls_params, arg_types):
            if isinstance(param, TypeVarTuple):
                ph = pm.Placeholder(None, f"*{param.__name__}")
                remaining = arg_types[len(mapping):]
                mapping[ph] = cast(pm.Type, pm.VaryingType(pm.Index.Empty, remaining))
                break
            ph = pm.Placeholder(None, param.__name__)
            mapping[ph] = arg_type

        return template.specialize(mapping).schema


def register(cls: type[pm.Builtin]) -> Spec:
    return Spec.of(spec_name(cls))


def register_native_spec(python_type: type, spec: Spec) -> None:
    _NATIVE_SPECS[python_type] = spec
    try:
        NativeHost.native_specs.invalidate_for(pm.NATIVE_HOST)
    except AttributeError:
        pass


def register_python_transform(origin: type, transform: PythonTransform) -> None:
    _PYTHON_TRANSFORMS[origin] = transform
    try:
        NativeHost.python_transforms.invalidate_for(pm.NATIVE_HOST)
    except AttributeError:
        pass


def type_from_annotation(
    annotation: Any,
    *,
    template: pm.NativeType | None = None,
) -> pm.Type:
    return pm.NATIVE_HOST.type_from_annotation(annotation, template=template)


def native_type(cls: type[pm.Builtin]) -> pm.NativeType:
    return _host_singleton().template_for(cls)


def wrap(obj: Any):
    """Canonical core entry point.

    - wrap(annotation/type) -> projected core descriptor
    - wrap(value) -> carrier built from the projected descriptor
    """
    if isinstance(obj, pm.Type):
        return native_type(type(obj)).make(obj)

    if isinstance(obj, type):
        if issubclass(obj, pm.Builtin):
            return native_type(cast(type[pm.Builtin], obj))
        return type_from_annotation(obj)

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        return type_from_annotation(obj)

    if isinstance(obj, pm.Builtin):
        return native_type(type(obj)).make(obj)

    descriptor = wrap(type(obj))
    if isinstance(descriptor, pm.Type):
        return descriptor.make(obj)
    raise TypeError(f"Cannot wrap value {obj!r} with inferred descriptor")


def _set_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, Spec.of("std.qualifiers.Set")))


def _map_transform(key_type: pm.Type, value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, Spec.of("std.qualifiers.Map", key_type)))


def _list_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, Spec.of("std.qualifiers.List")))


def _frozenset_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, Spec.of("std.qualifiers.FrozenSet")))


def _tuple_transform(*types: pm.Type | object) -> pm.Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(
            pm.Type,
            pm.Qual.of(cast(pm.Type, types[0]), Spec.of("std.qualifiers.List")),
        )
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(pm.Type, Spec.of("std.types.Tuple", *cast(tuple[pm.Type, ...], types)))


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
