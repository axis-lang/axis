from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import (
    Any,
    Callable,
    TypeAliasType,
    TypeVar,
    TypeVarTuple,
    Union,
    Unpack,
    cast,
    get_args,
    get_origin,
)

from protobase import Consed, attr_info_of, flux, frozendict

import protomorph
from .foundation import _ALL_BUILTINS, Anchor, Id
from .realm import OverlayRealm, Realm

type PythonTransform = Callable[..., protomorph.Type]

_NATIVE_SPECS: dict[Any, protomorph.Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}
_BOOTSTRAPPED = False


def spec_name(cls: type[protomorph.Builtin]) -> str:
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


class NativeVar(protomorph.Var):
    ctx: str | None
    id: str

    def display_label(self) -> str | None:
        return self.id


def _native_ctx(template: Any | None) -> str | None:
    if template is None:
        return None
    if isinstance(template, str):
        return template
    if isinstance(template, type) and issubclass(template, protomorph.Builtin):
        return spec_name(template)
    if isinstance(template, protomorph.Spec):
        return str(template.anchor)
    return str(template)


def _resolve_type_alias(annotation: Any) -> Any:
    seen: set[int] = set()
    current = annotation
    while isinstance(current, TypeAliasType):
        marker = id(current)
        if marker in seen:
            break
        seen.add(marker)
        current = current.__value__
    return current


class NativeRealm(Realm, Consed):
    @flux.property
    def all_builtins(self) -> frozenset[type[protomorph.Builtin]]:
        return frozenset(_ALL_BUILTINS)

    @flux.property
    def native_specs(self) -> frozendict[Any, protomorph.Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method  # pyright: ignore[reportIncompatibleMethodOverride]
    def schema_template_for(self, builtin_cls: type[protomorph.Builtin]) -> protomorph.TupleLikeType:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return protomorph.VaryingType(())

        names = list(attrs.keys())
        types = tuple(_project_type(info.type, template=builtin_cls) for info in attrs.values())
        indexed_type = cast(Any, getattr(protomorph, "IndexedType"))
        return indexed_type(
            protomorph.VaryingType(types), protomorph.Index.of(*(protomorph.Id(name) for name in names))
        )

    @flux.property
    def builtin_by_spec_name(self) -> frozendict[str, type[protomorph.Builtin]]:
        return frozendict({spec_name(cls): cls for cls in self.all_builtins})

    @flux.method
    def schema_for(self, spec: protomorph.Spec) -> protomorph.TupleLikeType | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: protomorph.Spec) -> protomorph.TupleLikeType | None:
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
        builtin_cls: type[protomorph.Builtin],
        arg_types: tuple[protomorph.Type, ...],
    ) -> protomorph.Spec:
        return protomorph.Spec.of(spec_name(builtin_cls), *arg_types)

    def _mapping_for_spec(
        self,
        spec: protomorph.Spec,
        cls_params: tuple[object, ...],
        builtin_cls: type[protomorph.Builtin],
    ) -> dict[protomorph.Placeholder, protomorph.Type]:
        arg_types = tuple(cast(protomorph.Type, child.fetch()) for child in spec.args)

        variadic_index = next(
            (i for i, p in enumerate(cls_params) if isinstance(p, TypeVarTuple)), None
        )
        if variadic_index is None:
            if len(arg_types) != len(cls_params):
                raise TypeError(
                    f"{spec_name(builtin_cls)} expects {len(cls_params)} type argument(s), "
                    f"got {len(arg_types)}"
                )
        else:
            required = len(cls_params) - 1  # all params except the TypeVarTuple
            if len(arg_types) < required:
                raise TypeError(
                    f"{spec_name(builtin_cls)} expects at least {required} type argument(s), "
                    f"got {len(arg_types)}"
                )

        mapping: dict[protomorph.Placeholder, protomorph.Type] = {}
        for index, (param, arg_type) in enumerate(zip(cls_params, arg_types)):
            if isinstance(param, TypeVarTuple):
                remaining = arg_types[index:]
                mapping[NativeVar(spec_name(builtin_cls), f"*{param.__name__}")] = cast(
                    protomorph.Type,
                    protomorph.VaryingType(remaining),
                )
                break
            mapping[NativeVar(spec_name(builtin_cls), cast(TypeVar, param).__name__)] = arg_type
        return mapping

    def _specialize_schema(
        self,
        schema: protomorph.TupleLikeType,
        mapping: dict[protomorph.Placeholder, protomorph.Type],
    ) -> protomorph.TupleLikeType:
        indexed_type = getattr(protomorph, "IndexedType", None)
        if indexed_type is not None and isinstance(schema, indexed_type):
            indexed_schema = cast(Any, schema)
            inner = cast(
                protomorph.TupleLikeType,
                self._specialize_schema(
                    cast(protomorph.TupleLikeType, indexed_schema.inner), mapping
                ),
            )
            index = indexed_schema.index.splice()
            return indexed_type(cast(protomorph.Type, inner), index)

        def _make_replacement(ph: protomorph.Placeholder) -> Any:
            replacement = mapping[ph]
            if (protomorph.placeholder_name(ph) or "").startswith("*") and isinstance(replacement, protomorph.VaryingType):
                return protomorph.Spread(replacement.values)
            return replacement

        new_types: list[protomorph.Type] = []
        varying_schema = cast(protomorph.VaryingType, schema)
        for field_type in varying_schema.values:
            if isinstance(field_type, protomorph.Placeholder) and field_type in mapping:
                new_types.append(cast(protomorph.Type, _make_replacement(field_type)))
                continue
            if isinstance(field_type, protomorph.UniformType):
                element_type = field_type.element_type
                if isinstance(element_type, protomorph.Placeholder) and element_type in mapping:
                    replacement = mapping[element_type]
                    if isinstance(replacement, protomorph.VaryingType):
                        new_types.append(replacement)
                    else:
                        new_types.append(protomorph.UniformType(replacement))
                    continue
            if isinstance(field_type, protomorph.VaryingType):
                replaced_values = []
                changed = False
                for item_type in field_type.values:
                    if isinstance(item_type, protomorph.Placeholder) and item_type in mapping:
                        replacement = mapping[item_type]
                        if isinstance(replacement, protomorph.VaryingType):
                            replaced_values.extend(replacement.values)
                        else:
                            replaced_values.append(replacement)
                        changed = True
                    else:
                        replaced_values.append(item_type)
                if changed:
                    new_types.append(
                        cast(
                            protomorph.Type,
                            protomorph.VaryingType(tuple(replaced_values)).splice(),
                        )
                    )
                    continue
            field_carrier = wrap(field_type)
            carrier_mapping: dict[protomorph.Carrier, protomorph.Carrier] = {}
            for leaf in field_carrier.deep_iter():
                data = leaf.fetch()
                if data in mapping:
                    carrier_mapping[leaf] = protomorph.LeafCarrier(
                        leaf.descriptor,
                        _make_replacement(cast(protomorph.Placeholder, data)),
                    )
            if carrier_mapping:
                result = field_carrier.subst(carrier_mapping).fetch()
                if isinstance(result, protomorph.TupleLikeType):
                    result = result.splice()
                new_types.append(cast(protomorph.Type, result))
            else:
                new_types.append(field_type)
        return cast(
            protomorph.TupleLikeType,
            protomorph.VaryingType(tuple(new_types)).splice(),
        )

    def with_rules(self, *rules: protomorph.Builtin) -> OverlayRealm:
        return OverlayRealm(base=self, rules=rules, facts=(), impls=(), coinductive_anchors=frozenset())

    def with_facts(self, *facts: protomorph.Builtin) -> OverlayRealm:
        return OverlayRealm(base=self, rules=(), facts=facts, impls=(), coinductive_anchors=frozenset())

    def with_impls(self, *impls: protomorph.Builtin) -> OverlayRealm:
        return OverlayRealm(base=self, rules=(), facts=(), impls=impls, coinductive_anchors=frozenset())


def register_native_spec(python_type: Any, spec: protomorph.Spec) -> None:
    _NATIVE_SPECS[python_type] = spec
    try:
        NativeRealm.native_specs.invalidate_for(protomorph.NATIVE_REALM)
    except AttributeError:
        pass


def register_python_transform(origin: type, transform: PythonTransform) -> None:
    _PYTHON_TRANSFORMS[origin] = transform
    try:
        NativeRealm.python_transforms.invalidate_for(protomorph.NATIVE_REALM)
    except AttributeError:
        pass


def instantiate_builtin(
    anchor: protomorph.Anchor | str,
    args: protomorph.Tuple | None = None,
) -> protomorph.Builtin | None:
    if isinstance(anchor, str):
        anchor = protomorph.Anchor(anchor)

    builtin_cls = protomorph.NATIVE_REALM.builtin_by_spec_name.get(str(anchor))
    if builtin_cls is None:
        return None

    tuple_args = args or protomorph.Tuple.Empty
    arg_values: list[object] = []
    arg_nominal: dict[str, object] = {}
    for i in range(len(tuple_args)):
        item = tuple_args.descriptor.item_at(i)
        value = tuple_args[i].fetch()
        if item.key is None:
            arg_values.append(value)
        else:
            arg_nominal[str(item.key)] = value

    attrs = list(attr_info_of(builtin_cls).keys())

    kwargs: dict[str, object] = {}
    remaining = iter(arg_values)
    for name in attrs:
        info = attr_info_of(builtin_cls)[name]
        wants_carrier = info.type is protomorph.Carrier or repr(info.type).startswith("protomorph.carrier.Carrier")
        if name in arg_nominal:
            kwargs[name] = tuple_args.attr(protomorph.Id(name)) if wants_carrier else arg_nominal[name]
            continue
        try:
            value = next(remaining)
            kwargs[name] = tuple_args[len(kwargs)] if wants_carrier else value
        except StopIteration:
            break

    try:
        return builtin_cls(**kwargs)
    except TypeError:
        return None


def _project_type(
    annotation: Any,
    *,
    template: Any | None = None,
) -> protomorph.Type:
    annotation = _resolve_type_alias(annotation)

    if isinstance(annotation, protomorph.Type):
        return annotation

    if annotation is protomorph.Type:
        return protomorph.Spec.of("std.metas.Type")

    if annotation is protomorph.Carrier:
        return protomorph.Spec.of("std.types.Any")

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is protomorph.Carrier:
        return protomorph.Spec.of("std.types.Any")

    if origin is protomorph.Type:
        return protomorph.Spec.of("std.metas.Type")

    if annotation is Any:
        return protomorph.Spec.of("std.types.Any")

    if annotation is protomorph.Datum or repr(annotation) == "Datum":
        return protomorph.Spec.of("std.types.Any")

    if annotation is protomorph.Tuple:
        return protomorph.Spec.of("std.types.Tuple")

    if annotation is protomorph.Index:
        return protomorph.Spec.of("std.types.Index")

    if isinstance(annotation, TypeVar):
        return NativeVar(_native_ctx(template), annotation.__name__)

    if isinstance(annotation, TypeVarTuple):
        return NativeVar(_native_ctx(template), f"*{annotation.__name__}")

    scalar_spec = _NATIVE_SPECS.get(annotation)
    if scalar_spec is not None:
        return scalar_spec

    if origin is Union or isinstance(annotation, PEP604Union):
        return protomorph.UnionType.of(
            *(_project_type(arg, template=template) for arg in args)
        )

    if origin is Unpack and len(args) == 1:
        return _project_type(args[0], template=template)

    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return protomorph.UniformType(_project_type(args[0], template=template))

    if origin is tuple and args:
        converted = tuple(_project_type(arg, template=template) for arg in args)
        if (
            len(converted) == 1
            and isinstance(converted[0], protomorph.Placeholder)
            and (protomorph.placeholder_name(cast(protomorph.Placeholder, converted[0])) or "").startswith("*")
        ):
            return converted[0]
        return cast(protomorph.Type, protomorph.VaryingType(converted))

    if isinstance(origin, type):
        typed_origin = cast(type, origin)
        transform = _PYTHON_TRANSFORMS.get(typed_origin)
        if transform is not None:
            converted = tuple(
                (
                    _project_type(arg, template=template)
                    if arg is not Ellipsis
                    else arg
                )
                for arg in args
            )
            return transform(*converted)

        if issubclass(typed_origin, protomorph.Builtin):
            arg_types = tuple(_project_type(arg, template=template) for arg in args)
            return protomorph.Spec.of(spec_name(typed_origin), *arg_types)

    if isinstance(annotation, type) and issubclass(annotation, protomorph.Builtin):
        return protomorph.Spec.of(spec_name(annotation))

    if isinstance(annotation, type) and issubclass(annotation, protomorph.Tuple):
        return protomorph.Spec.of("std.types.Tuple")

    raise ValueError(f"Unsupported annotation: {annotation!r}")


def wrap(*args, **kwargs) -> protomorph.Carrier:

    if not args and not kwargs:
        raise TypeError("wrap() requires at least one argument")

    if len(args) > 1 or kwargs:
        return protomorph.VaryingType.new(
            *(wrap(arg) for arg in args),
            **{key: wrap(value) for key, value in kwargs.items()},
        )

    obj = args[0] # type: ignore

    if isinstance(obj, protomorph.Carrier):
        return obj

    if isinstance(obj, protomorph.Type):
        if isinstance(obj, (protomorph.Spec, protomorph.Qual, protomorph.VaryingType)):
            return protomorph.NativeObjectCarrier(_project_type(type(obj)), obj)
        return obj.metatype().make(obj)

    if isinstance(obj, type):
        return _project_type(obj).metatype().make(_project_type(obj))

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        descriptor = _project_type(obj)
        return descriptor.metatype().make(descriptor)

    if isinstance(obj, protomorph.Builtin):
        descriptor = _project_type(type(obj))
        return descriptor.make(obj)

    descriptor = cast(protomorph.Type, wrap(type(obj)).fetch())
    return descriptor.make(obj)


def _set_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.Set")))


def _map_transform(key_type: protomorph.Type, value_type: protomorph.Type) -> protomorph.Type:
    return cast(
        protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.Map", key_type))
    )


def _list_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.List")))


def _frozenset_transform(value_type: protomorph.Type) -> protomorph.Type:
    return cast(protomorph.Type, protomorph.Qual.of(value_type, protomorph.Spec.of("std.qualifiers.FrozenSet")))


def _tuple_transform(*types: protomorph.Type | object) -> protomorph.Type:
    if len(types) == 2 and types[1] is Ellipsis:
        return cast(protomorph.Type, protomorph.UniformType(cast(protomorph.Type, types[0])))
    if any(type_ is Ellipsis for type_ in types):
        raise TypeError("Only tuple[T, ...] homogeneous tuples are supported")
    return cast(protomorph.Type, protomorph.VaryingType(cast(tuple[protomorph.Type, ...], types)))


def _result_transform(err_type: protomorph.Type, ok_type: protomorph.Type) -> protomorph.Type:
    return cast(
        protomorph.Type,
        protomorph.Qual.of(ok_type, protomorph.Spec.of("std.qualifiers.Result", err_type)),
    )


def _bootstrap_defaults() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    register_native_spec(int, protomorph.Spec.of("std.types.Integer"))
    register_native_spec(str, protomorph.Spec.of("std.types.Text"))
    register_native_spec(float, protomorph.Spec.of("std.types.Decimal"))
    register_native_spec(Decimal, protomorph.Spec.of("std.types.Decimal"))
    register_native_spec(bool, protomorph.Spec.of("std.types.Boolean"))
    register_native_spec(NoneType, protomorph.Spec.of("std.types.Empty"))
    register_native_spec(Id, protomorph.Spec.of("std.types.Id"))
    register_native_spec(Anchor, protomorph.Spec.of("std.types.Anchor"))
    register_python_transform(dict, _map_transform)
    register_python_transform(list, _list_transform)
    register_python_transform(set, _set_transform)
    register_python_transform(frozenset, _frozenset_transform)
    register_python_transform(tuple, _tuple_transform)
    register_python_transform(protomorph.Result, _result_transform)

    _BOOTSTRAPPED = True
