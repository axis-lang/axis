from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import (
    Any,
    Callable,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    cast,
    get_args,
    get_origin,
)

from protobase import Consed, attr_info_of, flux, frozendict

import pm
from .foundation import _ALL_BUILTINS
from .hosted import Host

type PythonTransform = Callable[..., pm.Type]

_NATIVE_SPECS: dict[type, pm.Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}
_BOOTSTRAPPED = False


def spec_name(cls: type[pm.Builtin]) -> str:
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


class NativeVar(pm.Var[str | None, str]):
    ctx: str | None
    id: str


def _native_ctx(template: object | None) -> str | None:
    if template is None:
        return None
    if isinstance(template, str):
        return template
    if isinstance(template, type) and issubclass(template, pm.Builtin):
        return spec_name(template)
    if isinstance(template, pm.Spec):
        return str(template.anchor)
    return str(template)


class NativeHost(Host, Consed):
    @flux.property
    def all_builtins(self) -> frozenset[type[pm.Builtin]]:
        return frozenset(_ALL_BUILTINS)

    @flux.property
    def native_specs(self) -> frozendict[type, pm.Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def schema_template_for(self, builtin_cls: type[pm.Builtin]) -> pm.TupleLikeType:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return pm.VaryingType(())

        names = list(attrs.keys())
        types = tuple(self.project_type(info.type, template=builtin_cls) for info in attrs.values())
        indexed_type = cast(Any, getattr(pm, "IndexedType"))
        return indexed_type(
            pm.VaryingType(types), pm.Index.of(*(pm.Id(name) for name in names))
        )

    @flux.property
    def builtin_by_spec_name(self) -> frozendict[str, type[pm.Builtin]]:
        return frozendict({spec_name(cls): cls for cls in self.all_builtins})

    @flux.method
    def project_type(
        self,
        annotation: Any,
        *,
        template: object | None = None,
    ) -> pm.Type:
        if isinstance(annotation, pm.Type):
            return annotation

        if annotation is pm.Type:
            return pm.Spec.of("std.metas.Type")

        if annotation is pm.Tuple:
            return pm.Spec.of("std.types.Tuple")

        if annotation is pm.Index:
            return pm.Spec.of("std.types.Tuple")

        if isinstance(annotation, TypeVar):
            return NativeVar(_native_ctx(template), annotation.__name__)

        if isinstance(annotation, TypeVarTuple):
            return NativeVar(_native_ctx(template), f"*{annotation.__name__}")

        scalar_spec = self.native_specs.get(annotation)
        if scalar_spec is not None:
            return scalar_spec

        if annotation is str:
            return pm.Spec.of("std.types.Anchor")

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union or isinstance(annotation, PEP604Union):
            return pm.UnionType.of(
                *(self.project_type(arg, template=template) for arg in args)
            )

        if origin is Unpack and args:
            return self.project_type(args[0], template=template)

        if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
            return pm.UniformType(self.project_type(args[0], template=template))

        if origin is tuple and args:
            converted = tuple(self.project_type(arg, template=template) for arg in args)
            if (
                len(converted) == 1
                and isinstance(converted[0], pm.Placeholder)
                and cast(pm.Var, converted[0]).id.startswith("*")
            ):
                return converted[0]
            return cast(pm.Type, pm.VaryingType(converted))

        if isinstance(origin, type):
            typed_origin = cast(type, origin)
            transform = self.python_transforms.get(typed_origin)
            if transform is not None:
                converted = tuple(
                    (
                        self.project_type(arg, template=template)
                        if arg is not Ellipsis
                        else arg
                    )
                    for arg in args
                )
                return transform(*converted)

            if issubclass(typed_origin, pm.Builtin):
                arg_types = tuple(
                    self.project_type(arg, template=template) for arg in args
                )
                return self._spec_for_builtin(typed_origin, arg_types)

        if isinstance(annotation, type) and issubclass(annotation, pm.Builtin):
            return self._spec_for_builtin(annotation, ())

        if isinstance(annotation, type) and issubclass(annotation, pm.Tuple):
            return pm.Spec.of("std.types.Tuple")

        raise ValueError(f"Unsupported annotation: {annotation!r}")

    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        builtin_cls = self.builtin_by_spec_name.get(str(spec.anchor))
        if builtin_cls is None:
            return None

        schema = self.schema_template_for(builtin_cls)
        cls_params = getattr(builtin_cls, "__type_params__", ())
        if not cls_params or len(spec.args) == 0:
            return schema

        mapping = self._mapping_for_spec(spec, cls_params, builtin_cls)
        return self._specialize_schema(schema, mapping)

    def _spec_for_builtin(
        self,
        builtin_cls: type[pm.Builtin],
        arg_types: tuple[pm.Type, ...],
    ) -> pm.Spec:
        return pm.Spec.of(spec_name(builtin_cls), *arg_types)

    def _mapping_for_spec(
        self,
        spec: pm.Spec,
        cls_params: tuple[object, ...],
        builtin_cls: type[pm.Builtin],
    ) -> dict[pm.Placeholder, pm.Type]:
        arg_types = tuple(cast(pm.Type, child.fetch()) for child in spec.args)
        mapping: dict[pm.Placeholder, pm.Type] = {}
        for index, (param, arg_type) in enumerate(zip(cls_params, arg_types)):
            if isinstance(param, TypeVarTuple):
                remaining = arg_types[index:]
                mapping[NativeVar(spec_name(builtin_cls), f"*{param.__name__}")] = cast(
                    pm.Type,
                    pm.VaryingType(remaining),
                )
                break
            mapping[NativeVar(spec_name(builtin_cls), cast(TypeVar, param).__name__)] = arg_type
        return mapping

    def _specialize_schema(
        self,
        schema: pm.TupleLikeType,
        mapping: dict[pm.Placeholder, pm.Type],
    ) -> pm.TupleLikeType:
        indexed_type = getattr(pm, "IndexedType", None)
        if indexed_type is not None and isinstance(schema, indexed_type):
            indexed_schema = cast(Any, schema)
            inner = cast(
                pm.TupleLikeType,
                self._specialize_schema(
                    cast(pm.TupleLikeType, indexed_schema.inner), mapping
                ),
            )
            index = indexed_schema.index.splice()
            return indexed_type(cast(pm.Type, inner), index)

        def _make_replacement(ph: pm.Placeholder) -> object:
            replacement = mapping[ph]
            if cast(pm.Var, ph).id.startswith("*") and isinstance(replacement, pm.VaryingType):
                return pm.Spread(replacement.values)
            return replacement

        new_types: list[pm.Type] = []
        varying_schema = cast(pm.VaryingType, schema)
        for field_type in varying_schema.values:
            if isinstance(field_type, pm.Placeholder) and field_type in mapping:
                new_types.append(cast(pm.Type, _make_replacement(field_type)))
                continue
            if isinstance(field_type, pm.UniformType):
                element_type = field_type.element_type
                if isinstance(element_type, pm.Placeholder) and element_type in mapping:
                    replacement = mapping[element_type]
                    if isinstance(replacement, pm.VaryingType):
                        new_types.append(replacement)
                    else:
                        new_types.append(pm.UniformType(replacement))
                    continue
            if isinstance(field_type, pm.VaryingType):
                replaced_values = []
                changed = False
                for item_type in field_type.values:
                    if isinstance(item_type, pm.Placeholder) and item_type in mapping:
                        replacement = mapping[item_type]
                        if isinstance(replacement, pm.VaryingType):
                            replaced_values.extend(replacement.values)
                        else:
                            replaced_values.append(replacement)
                        changed = True
                    else:
                        replaced_values.append(item_type)
                if changed:
                    new_types.append(
                        cast(
                            pm.Type,
                            pm.VaryingType(tuple(replaced_values)).splice(),
                        )
                    )
                    continue
            field_carrier = wrap(field_type)
            carrier_mapping: dict[pm.Carrier, pm.Carrier] = {}
            for leaf in field_carrier.deep_iter():
                data = leaf.fetch()
                if data in mapping:
                    carrier_mapping[leaf] = pm.LeafCarrier(
                        leaf.descriptor,
                        _make_replacement(cast(pm.Placeholder, data)),
                    )
            if carrier_mapping:
                result = field_carrier.subst(carrier_mapping).fetch()
                if isinstance(result, pm.TupleLikeType):
                    result = result.splice()
                new_types.append(cast(pm.Type, result))
            else:
                new_types.append(field_type)
        return cast(
            pm.TupleLikeType,
            pm.VaryingType(tuple(new_types)).splice(),
        )


def register_native_spec(python_type: type, spec: pm.Spec) -> None:
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


def _project_type(
    annotation: Any,
    *,
    template: object | None = None,
) -> pm.Type:
    return pm.NATIVE_HOST.project_type(annotation, template=template)


def wrap(*args, **kwargs) -> pm.Carrier:

    if not args and not kwargs:
        raise TypeError("wrap() requires at least one argument")

    if len(args) > 1 or kwargs:
        return pm.VaryingType.new(
            *(wrap(arg) for arg in args),
            **{key: wrap(value) for key, value in kwargs.items()},
        )

    obj = args[0] # type: ignore

    if isinstance(obj, pm.Carrier):
        return obj

    if isinstance(obj, pm.Type):
        if isinstance(obj, (pm.Spec, pm.Qual, pm.VaryingType)):
            return pm.NativeObjectCarrier(_project_type(type(obj)), obj)
        return obj.metatype().make(obj)

    if isinstance(obj, type):
        return _project_type(obj).metatype().make(_project_type(obj))

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        descriptor = _project_type(obj)
        return descriptor.metatype().make(descriptor)

    if isinstance(obj, pm.Builtin):
        descriptor = _project_type(type(obj))
        return descriptor.make(obj)

    descriptor = cast(pm.Type, wrap(type(obj)).fetch())
    return descriptor.make(obj)


def _set_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, pm.Spec.of("std.qualifiers.Set")))


def _map_transform(key_type: pm.Type, value_type: pm.Type) -> pm.Type:
    return cast(
        pm.Type, pm.Qual.of(value_type, pm.Spec.of("std.qualifiers.Map", key_type))
    )


def _list_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, pm.Spec.of("std.qualifiers.List")))


def _frozenset_transform(value_type: pm.Type) -> pm.Type:
    return cast(pm.Type, pm.Qual.of(value_type, pm.Spec.of("std.qualifiers.FrozenSet")))


def _tuple_transform(*types: pm.Type | object) -> pm.Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(
            pm.Type,
            pm.Qual.of(cast(pm.Type, types[0]), pm.Spec.of("std.qualifiers.List")),
        )
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(
        pm.Type, pm.Spec.of("std.types.Tuple", *cast(tuple[pm.Type, ...], types))
    )


def _bootstrap_defaults() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    register_native_spec(int, pm.Spec.of("std.types.Integer"))
    register_native_spec(str, pm.Spec.of("std.types.Text"))
    register_native_spec(float, pm.Spec.of("std.types.Decimal"))
    register_native_spec(Decimal, pm.Spec.of("std.types.Decimal"))
    register_native_spec(bool, pm.Spec.of("std.types.Boolean"))
    register_native_spec(NoneType, pm.Spec.of("std.types.Empty"))
    register_native_spec(type(pm.Id("x")), pm.Spec.of("std.types.Id"))
    register_python_transform(dict, _map_transform)
    register_python_transform(list, _list_transform)
    register_python_transform(set, _set_transform)
    register_python_transform(frozenset, _frozenset_transform)
    register_python_transform(tuple, _tuple_transform)

    _BOOTSTRAPPED = True
