from __future__ import annotations

from decimal import Decimal
from types import NoneType
from types import UnionType as PEP604Union
from typing import (Any, Callable, TypeAliasType, TypeVar, TypeVarTuple, Union,
                    Unpack, cast, get_args, get_origin)

import protomorph
from protobase import Consed, attr_info_of, flux, frozendict

from .domain import ALL_BUILTINS, Anchor, Id, Var
from .realm import OverlayRealm, Realm

type PythonTransform = Callable[..., protomorph.Type]

_NATIVE_SPECS: dict[Any, protomorph.Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}

_OPTIONAL_QUALIFIER = Anchor("std.qualifiers.Optional")
_RESULT_QUALIFIER = Anchor("std.qualifiers.Result")
_SET_QUALIFIER = Anchor("std.qualifiers.Set")
_LIST_QUALIFIER = Anchor("std.qualifiers.List")
_MAP_QUALIFIER = Anchor("std.qualifiers.Map")


def spec_name(cls: type[protomorph.Builtin]) -> str:
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


class NativeVar(Var):
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


def _qualifier_arg_type(
    qualifier: protomorph.Spec,
    *,
    index: int,
    name: str,
) -> protomorph.Type:
    if len(qualifier.args) <= index:
        raise TypeError(f"{name} qualifier must provide type argument {index}")
    return cast(protomorph.Type, qualifier.args[index].fetch())


class NativeRealm(Realm, Consed):
    @flux.property
    def all_builtins(self) -> frozenset[type[protomorph.Builtin]]:
        return frozenset(ALL_BUILTINS)

    @flux.property
    def native_specs(self) -> frozendict[Any, protomorph.Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def schema_template_for(self, builtin_cls: type[protomorph.Builtin]) -> protomorph.Schema:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return cast(protomorph.Schema, protomorph.Tuple.Empty)

        names = list(attrs.keys())
        types = tuple(_project_type(info.type, template=builtin_cls) for info in attrs.values())
        return cast(
            protomorph.Schema,
            protomorph.Tuple(
                protomorph.IndexedType(
                    protomorph.VaryingType(types),
                    protomorph.Index.of(*(protomorph.Id(name) for name in names)),
                ),
                types,
            ),
        )

    @flux.property
    def builtin_by_spec_name(self) -> frozendict[str, type[protomorph.Builtin]]:
        return frozendict({spec_name(cls): cls for cls in self.all_builtins})

    @flux.method
    def schema_for(self, spec: protomorph.Spec) -> protomorph.Schema | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: protomorph.Spec) -> protomorph.Schema | None:
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
        schema: protomorph.Schema,
        mapping: dict[protomorph.Placeholder, protomorph.Type],
    ) -> protomorph.Schema:
        descriptor = schema.descriptor
        if isinstance(descriptor, protomorph.IndexedType):
            index = descriptor.index.splice()
        else:
            index = None

        def _make_replacement(ph: protomorph.Placeholder) -> Any:
            replacement = mapping[ph]
            if (protomorph.placeholder_name(ph) or "").startswith("*") and isinstance(replacement, protomorph.VaryingType):
                return protomorph.Spread(replacement.values)
            return replacement

        new_types: list[protomorph.Type] = []
        for field in schema:
            field_type = cast(protomorph.Type, field.fetch())
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
            field_carrier = val(field_type)
            carrier_mapping: dict[protomorph.Val, protomorph.Val] = {}
            for leaf in field_carrier.iter_leafs():
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
        if index is None:
            return cast(
                protomorph.Schema,
                protomorph.Tuple(protomorph.VaryingType(tuple(new_types)), tuple(new_types)),
            )
        return cast(
            protomorph.Schema,
            protomorph.Tuple(
                protomorph.IndexedType(protomorph.VaryingType(tuple(new_types)), index),
                tuple(new_types),
            ),
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
        item = tuple_args.payload_item_at(i)
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
        wants_carrier = info.type is protomorph.Val or repr(info.type).startswith("protomorph.carriers.base.Carrier")
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


def project_type(
    annotation: Any,
    *,
    template: Any | None = None,
) -> protomorph.Type:
    annotation = _resolve_type_alias(annotation)

    if isinstance(annotation, protomorph.Type):
        return annotation

    if annotation is protomorph.Type:
        return protomorph.Spec.of("std.metas.Type")

    if annotation is protomorph.Val:
        return protomorph.Spec.of("std.types.Any")

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is protomorph.Val:
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

    if origin is Union:
        # typing.Optional[T] == Union[T, None] with exactly two args → Optional qualifier
        if len(args) == 2 and NoneType in args:
            inner = next(a for a in args if a is not NoneType)
            return cast(
                protomorph.Type,
                protomorph.Qual.of(
                    project_type(inner, template=template),
                    protomorph.Spec.of("std.qualifiers.Optional"),
                ),
            )
        return protomorph.UnionType.of(*(project_type(arg, template=template) for arg in args))

    if isinstance(annotation, PEP604Union):
        return protomorph.UnionType.of(*(project_type(arg, template=template) for arg in args))

    if origin is Unpack and len(args) == 1:
        return project_type(args[0], template=template)

    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return protomorph.UniformType(project_type(args[0], template=template))

    if origin is tuple and args:
        converted = tuple(project_type(arg, template=template) for arg in args)
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
                    project_type(arg, template=template)
                    if arg is not Ellipsis
                    else arg
                )
                for arg in args
            )
            return transform(*converted)

        if issubclass(typed_origin, protomorph.Builtin):
            arg_types = tuple(project_type(arg, template=template) for arg in args)
            return protomorph.Spec.of(spec_name(typed_origin), *arg_types)

    if isinstance(annotation, type) and issubclass(annotation, protomorph.Builtin):
        return protomorph.Spec.of(spec_name(annotation))

    if isinstance(annotation, type) and issubclass(annotation, protomorph.Tuple):
        return protomorph.Spec.of("std.types.Tuple")

    raise ValueError(f"Unsupported annotation: {annotation!r}")


def val(*args, **kwargs) -> protomorph.Val:
    values = cast(tuple[object, ...], args)

    if not values and not kwargs:
        raise TypeError("wrap() requires at least one argument")

    if len(values) > 1 or kwargs:
        return protomorph.VaryingType.new(
            *(val(arg) for arg in values),
            **{key: val(value) for key, value in kwargs.items()},
        )

    if len(values) != 1:
        raise AssertionError("wrap() expected exactly one value after variadic handling")
    obj = values[0]

    if isinstance(obj, protomorph.Val):
        return obj

    if isinstance(obj, protomorph.Type):
        if isinstance(obj, (protomorph.Spec, protomorph.Qual, protomorph.VaryingType)):
            return protomorph.NativeObjectCarrier(_project_type(type(obj)), obj)
        return obj.metatype().make(obj)

    if isinstance(obj, type):
        return project_type(obj).metatype().make(project_type(obj))

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        descriptor = project_type(obj)
        return descriptor.metatype().make(descriptor)

    if isinstance(obj, protomorph.Builtin):
        descriptor = project_type(type(obj))
        return descriptor.make(obj)

    descriptor = cast(protomorph.Type, val(type(obj)).fetch())
    return descriptor.make(obj)


_project_type = project_type
