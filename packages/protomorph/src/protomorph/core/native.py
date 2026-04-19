from __future__ import annotations

from decimal import Decimal
from types import NoneType
from types import UnionType as PEP604Union
from typing import (
    Any,
    Callable,
    TypeAliasType,
    TypeVar,
    TypeVarTuple,
    Union as _TypingUnion,
    Unpack,
    cast,
    get_args,
    get_origin,
)

import protomorph.core as _pm
from protobase import Consed, attr_info_of, flux, frozendict

from .foundation import Id, all_builtins
from .types import Var
from .realm import OverlayRealm, Realm

type PythonTransform = Callable[..., _pm.Type]

_NATIVE_SPECS: dict[Any, _pm.Spec] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}

class _Spread[V]:
    __slots__ = ("values",)

    def __init__(self, values: tuple[V, ...]):
        self.values = values


def spec_name(cls: type[_pm.Builtin]) -> str:
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
    if isinstance(template, type) and issubclass(template, _pm.Builtin):
        return spec_name(template)
    if isinstance(template, _pm.Spec):
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
    qualifier: _pm.Spec,
    *,
    index: int,
    name: str,
) -> _pm.Type:
    if len(qualifier.args) <= index:
        raise TypeError(f"{name} qualifier must provide type argument {index}")
    return cast(_pm.Type, qualifier.args[index].content)


def _type_params_of(builtin_cls: type[_pm.Builtin]) -> tuple[object, ...]:
    return getattr(builtin_cls, "__type_params__", ())


def _placeholder_id(placeholder: _pm.Placeholder) -> str | None:
    ident = getattr(placeholder, "id", None)
    return ident if isinstance(ident, str) else None


def _make_schema(
    types: tuple[_pm.Type, ...],
    index: _pm.Index | None = None,
) -> _pm.Schema:
    if index is None:
        return cast(_pm.Schema, _pm.Tuple(_pm.Varying(types), types))
    return cast(
        _pm.Schema,
        _pm.Tuple(
            _pm.Indexed(_pm.Varying(types), index),
            types,
        ),
    )


def _spec_arg_types(spec: _pm.Spec) -> tuple[_pm.Type, ...]:
    return tuple(cast(_pm.Type, child.content) for child in spec.args)


def _type_param_name(param: object) -> str:
    assert isinstance(param, TypeVar)
    return param.__name__


def _variadic_type(values: tuple[_pm.Type, ...]) -> _pm.Varying:
    return _pm.Varying(values)


def normalize_spreads(value: Any) -> Any:
    if isinstance(value, _Spread):
        return _pm.Varying(cast(tuple[_pm.Type, ...], value.values))
    if isinstance(value, _pm.Index):
        normalized_index_values: list[_pm.Id | None] = []
        for item in value.content:
            if isinstance(item, _Spread):
                normalized_index_values.extend(cast(tuple[_pm.Id | None, ...], item.values))
            else:
                normalized_index_values.append(item)
        return _pm.Index.of(*normalized_index_values)
    if isinstance(value, _pm.Varying):
        normalized_slot_values: list[_pm.Type] = []
        for item in value.element_types:
            if isinstance(item, _Spread):
                normalized_slot_values.extend(cast(tuple[_pm.Type, ...], item.values))
            else:
                normalized_slot_values.append(item)
        return _pm.Varying(tuple(normalized_slot_values))
    if isinstance(value, _pm.Indexed):
        slots = value.slots
        if isinstance(slots, _pm.Varying):
            raw_slots = slots.element_types
        else:
            raw_slots = (slots.element_type,) * len(value.index)

        flat_slots: list[_pm.Type] = []
        flat_keys: list[_pm.Id | None] = []
        keys = tuple(value.index.content)
        for key, slot in zip(keys, raw_slots, strict=True):
            if isinstance(slot, _Spread):
                spread_values = cast(tuple[_pm.Type, ...], slot.values)
                flat_slots.extend(spread_values)
                flat_keys.extend((None,) * len(spread_values))
                continue
            flat_slots.append(slot)
            flat_keys.append(key)
        return _pm.Indexed(_pm.Varying(tuple(flat_slots)), _pm.Index.of(*flat_keys))
    if isinstance(value, _pm.Tuple):
        normalized_content: list[Any] = []
        for item in value.content:
            if isinstance(item, _Spread):
                normalized_content.extend(item.values)
            else:
                normalized_content.append(item)
        descriptor = normalize_spreads(value.descriptor)
        return _pm.Tuple(descriptor, tuple(normalized_content))
    return value


def _single_value(args: tuple[object, ...]) -> object:
    if len(args) != 1:
        raise AssertionError(
            "wrap() expected exactly one value after variadic handling"
        )
    return args[0]


def _descriptor_item(
    tuple_args: _pm.Tuple, name: str, offset: int, *, wants_carrier: bool
) -> object:
    has_named_item = (
        isinstance(tuple_args.descriptor, _pm.Indexed)
        and _pm.Id(name) in tuple_args.descriptor.index.content
    )
    if wants_carrier:
        return tuple_args.attr(_pm.Id(name)) if has_named_item else tuple_args[offset]
    entry = tuple_args.entry_at(offset)
    return (
        tuple_args[offset].content
        if entry.key is None
        else tuple_args.attr(_pm.Id(name)).content
    )


def _descriptor_for_value(obj: object) -> _pm.Type:
    return cast(_pm.Type, val(type(obj)).content)


def _first_arg_type(args: tuple[Any, ...], *, template: Any | None) -> _pm.Type:
    if not args:
        return _pm.types.any
    return project_type(args[0], template=template)


def _tuple_generic_type(args: tuple[Any, ...], *, template: Any | None) -> _pm.Type:
    if not args:
        return _pm.types.any
    if len(args) == 1:
        return project_type(args[0], template=template)
    return _tuple_annotation_type(args, template=template)


def _any_type() -> _pm.Spec:
    return _pm.types.any


def _type_metatype() -> _pm.Spec:
    return _pm.Spec.of(_pm.anchors.type)


def _index_type() -> _pm.Spec:
    return _pm.types.index


def _is_variadic_placeholder(tp: _pm.Type) -> bool:
    return isinstance(tp, _pm.Placeholder) and (_placeholder_id(tp) or "").startswith(
        "*"
    )

def _optional_type(inner: _pm.Type) -> _pm.Type:
    return cast(_pm.Type, _pm.types.optional(inner))


def _tuple_annotation_type(args: tuple[Any, ...], *, template: Any | None) -> _pm.Type:
    if len(args) == 2 and args[1] is Ellipsis:
        return _pm.Uniform(project_type(args[0], template=template))

    converted = tuple(project_type(arg, template=template) for arg in args)
    if len(converted) == 1 and _is_variadic_placeholder(converted[0]):
        return converted[0]
    return cast(_pm.Type, _variadic_type(converted))


def _specialize_placeholder_type(
    field_type: _pm.Type,
    mapping: dict[_pm.Placeholder, _pm.Type],
    make_replacement: Callable[[_pm.Placeholder], Any],
) -> _pm.Type | None:
    if isinstance(field_type, _pm.Placeholder) and field_type in mapping:
        return cast(_pm.Type, make_replacement(field_type))
    if isinstance(field_type, _pm.Uniform):
        element_type = field_type.element_type
        if isinstance(element_type, _pm.Placeholder) and element_type in mapping:
            replacement = mapping[element_type]
            if isinstance(replacement, _pm.Varying):
                return replacement
            return _pm.Uniform(replacement)
    if isinstance(field_type, _pm.Varying):
        replaced_values: list[_pm.Type] = []
        changed = False
        for item_type in field_type.element_types:
            if isinstance(item_type, _pm.Placeholder) and item_type in mapping:
                replacement = mapping[item_type]
                if isinstance(replacement, _pm.Varying):
                    replaced_values.extend(replacement.element_types)
                else:
                    replaced_values.append(replacement)
                changed = True
            else:
                replaced_values.append(item_type)
        if changed:
            return cast(_pm.Type, normalize_spreads(_variadic_type(tuple(replaced_values))))
    return None


def _transformed_python_type(
    origin: type,
    args: tuple[Any, ...],
    *,
    template: Any | None,
) -> _pm.Type | None:
    transform = _PYTHON_TRANSFORMS.get(origin)
    if transform is not None:
        converted = tuple(
            project_type(arg, template=template) if arg is not Ellipsis else arg
            for arg in args
        )
        return transform(*converted)

    if issubclass(origin, _pm.Builtin):
        arg_types = tuple(project_type(arg, template=template) for arg in args)
        return _pm.Spec.of(spec_name(origin), *arg_types)

    return None


class NativeRealm(Realm, Consed):
    @flux.property
    def native_specs(self) -> frozendict[Any, _pm.Spec]:
        return frozendict(_NATIVE_SPECS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def schema_template_for(self, builtin_cls: type[_pm.Builtin]) -> _pm.Schema:
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return cast(_pm.Schema, _pm.Tuple.Empty)

        names = list(attrs.keys())
        types = tuple(
            _project_type(info.type, template=builtin_cls) for info in attrs.values()
        )
        return _make_schema(types, _pm.Index.of(*(_pm.Id(name) for name in names)))

    @flux.property
    def builtin_by_spec_name(self) -> frozendict[str, type[_pm.Builtin]]:
        return frozendict({spec_name(cls): cls for cls in all_builtins()})

    @flux.method
    def schema_for(self, spec: Any) -> Any | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._schema_for_cached(spec)

    @flux.method
    def _schema_for_cached(self, spec: _pm.Spec) -> _pm.Schema | None:
        builtin_cls = self.builtin_by_spec_name.get(str(spec.anchor))
        if builtin_cls is None:
            return None

        schema = self.schema_template_for(builtin_cls)
        cls_params = _type_params_of(builtin_cls)
        if not cls_params or len(spec.args) == 0:
            return schema

        mapping = self._mapping_for_spec(spec, cls_params, builtin_cls)
        return self._specialize_schema(schema, mapping)

    def _spec_for_builtin(
        self,
        builtin_cls: type[_pm.Builtin],
        arg_types: tuple[_pm.Type, ...],
    ) -> _pm.Spec:
        return _pm.Spec.of(spec_name(builtin_cls), *arg_types)

    def _mapping_for_spec(
        self,
        spec: _pm.Spec,
        cls_params: tuple[object, ...],
        builtin_cls: type[_pm.Builtin],
    ) -> dict[_pm.Placeholder, _pm.Type]:
        arg_types = _spec_arg_types(spec)

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

        mapping: dict[_pm.Placeholder, _pm.Type] = {}
        for index, (param, arg_type) in enumerate(zip(cls_params, arg_types)):
            if isinstance(param, TypeVarTuple):
                remaining = arg_types[index:]
                mapping[NativeVar(spec_name(builtin_cls), f"*{param.__name__}")] = cast(
                    _pm.Type, _pm.Varying(remaining)
                )
                break
            mapping[NativeVar(spec_name(builtin_cls), _type_param_name(param))] = (
                arg_type
            )
        return mapping

    def _specialize_schema(
        self,
        schema: _pm.Schema,
        mapping: dict[_pm.Placeholder, _pm.Type],
    ) -> _pm.Schema:
        descriptor = schema.descriptor
        if isinstance(descriptor, _pm.Indexed):
            index = cast(_pm.Index, normalize_spreads(descriptor.index))
        else:
            index = None

        def _make_replacement(ph: _pm.Placeholder) -> Any:
            replacement = mapping[ph]
            ident = _placeholder_id(ph)
            if (
                isinstance(ident, str)
                and ident.startswith("*")
                and isinstance(replacement, _pm.Varying)
            ):
                return _Spread(replacement.element_types)
            return replacement

        new_types: list[_pm.Type] = []
        for field in schema:
            field_type = cast(_pm.Type, field.content)
            specialized_type = _specialize_placeholder_type(
                field_type, mapping, _make_replacement
            )
            if specialized_type is not None:
                new_types.append(cast(_pm.Type, normalize_spreads(specialized_type)))
                continue
            field_carrier = val(field_type)
            carrier_mapping: dict[_pm.Val, _pm.Val] = {}
            for leaf in _pm.walk_leafs(field_carrier):
                data = leaf.content
                if data in mapping:
                    carrier_mapping[leaf] = _pm.make_value(
                        leaf.descriptor,
                        _make_replacement(data),
                    )
            if carrier_mapping:
                result = _pm.walk_subst(field_carrier, carrier_mapping).content
                result = normalize_spreads(result)
                new_types.append(cast(_pm.Type, result))
            else:
                new_types.append(field_type)
        return _make_schema(tuple(new_types), index)

    def with_rules(self, *rules: _pm.Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self, rules=rules, facts=(), impls=(), coinductive_anchors=frozenset()
        )

    def with_facts(self, *facts: _pm.Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self, rules=(), facts=facts, impls=(), coinductive_anchors=frozenset()
        )

    def with_impls(self, *impls: _pm.Builtin) -> OverlayRealm:
        return OverlayRealm(
            base=self, rules=(), facts=(), impls=impls, coinductive_anchors=frozenset()
        )


def register_native_spec(python_type: Any, spec: _pm.Spec) -> None:
    _NATIVE_SPECS[python_type] = spec
    try:
        NativeRealm.native_specs.invalidate_for(_pm.NATIVE_REALM)
    except AttributeError:
        pass


def register_python_transform(origin: type, transform: PythonTransform) -> None:
    _PYTHON_TRANSFORMS[origin] = transform
    try:
        NativeRealm.python_transforms.invalidate_for(_pm.NATIVE_REALM)
    except AttributeError:
        pass


def instantiate_builtin(
    anchor: _pm.Anchor | str,
    args: _pm.Tuple | None = None,
) -> _pm.Builtin | None:
    if isinstance(anchor, str):
        anchor = _pm.Anchor(anchor)

    builtin_cls = _pm.NATIVE_REALM.builtin_by_spec_name.get(str(anchor))
    if builtin_cls is None:
        return None

    tuple_args = args or _pm.Tuple.Empty
    attrs = list(attr_info_of(builtin_cls).keys())
    index_keys = (
        tuple(tuple_args.descriptor.index.content)
        if isinstance(tuple_args.descriptor, _pm.Indexed)
        else ()
    )

    kwargs: dict[str, object] = {}
    for offset, name in enumerate(attrs):
        info = attr_info_of(builtin_cls)[name]
        wants_carrier = info.type is _pm.Val or repr(info.type).startswith(
            "protomorph.carriers.base.Carrier"
        )
        if name not in {
            str(key) for key in index_keys if key is not None
        } and offset >= len(tuple_args):
            break
        kwargs[name] = _descriptor_item(
            tuple_args, name, offset, wants_carrier=wants_carrier
        )

    try:
        return builtin_cls(**kwargs)
    except TypeError:
        return None


def project_type(
    annotation: Any,
    *,
    template: Any | None = None,
) -> _pm.Type:
    annotation = _resolve_type_alias(annotation)

    if isinstance(annotation, _pm.Type):
        return annotation

    if annotation is _pm.Type:
        return _type_metatype()

    if annotation is _pm.Val:
        return _any_type()

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is _pm.Val:
        return _first_arg_type(args, template=template)

    if origin is _pm.Type:
        return _type_metatype()

    if annotation is Any:
        return _any_type()

    if annotation is _pm.AnyData or repr(annotation) in {"Datum", "AnyData"}:
        return _any_type()

    if annotation is _pm.Tuple:
        return _pm.types.any

    if annotation is _pm.Index:
        return _index_type()

    if isinstance(annotation, TypeVar):
        return NativeVar(_native_ctx(template), annotation.__name__)

    if isinstance(annotation, TypeVarTuple):
        return NativeVar(_native_ctx(template), f"*{annotation.__name__}")

    scalar_spec = _NATIVE_SPECS.get(annotation)
    if scalar_spec is not None:
        return scalar_spec

    if origin is _TypingUnion:
        # typing.Optional[T] == Union[T, None] with exactly two args → Optional qualifier
        if len(args) == 2 and NoneType in args:
            inner = next(a for a in args if a is not NoneType)
            return _optional_type(project_type(inner, template=template))
        return _pm.types.Union.of(*(project_type(arg, template=template) for arg in args))

    if isinstance(annotation, PEP604Union):
        return _pm.types.Union.of(*(project_type(arg, template=template) for arg in args))

    if origin is Unpack and len(args) == 1:
        return project_type(args[0], template=template)

    if origin is tuple and args:
        return _tuple_annotation_type(args, template=template)

    if origin is _pm.Tuple:
        return _tuple_generic_type(args, template=template)

    if isinstance(origin, type):
        typed_origin = cast(type, origin)
        transformed = _transformed_python_type(typed_origin, args, template=template)
        if transformed is not None:
            return transformed

    if isinstance(annotation, type) and issubclass(annotation, _pm.Builtin):
        return _pm.Spec.of(spec_name(annotation))

    if isinstance(annotation, type) and issubclass(annotation, _pm.Tuple):
        return _pm.types.any

    raise ValueError(f"Unsupported annotation: {annotation!r}")


def val(*args, **kwargs) -> _pm.Val:
    values = cast(tuple[object, ...], args)

    if not values and not kwargs:
        raise TypeError("wrap() requires at least one argument")

    if len(values) > 1 or kwargs:
        return _pm.Varying.new(
            *(val(arg) for arg in values),
            **{key: val(value) for key, value in kwargs.items()},
        )

    obj = _single_value(values)

    if isinstance(obj, _pm.Val):
        return obj

    if isinstance(obj, _pm.types.Type):
        if isinstance(obj, (_pm.Spec, _pm.Qual)):
            return _pm.NativeObjectCarrier(_project_type(type(obj)), obj)
        return obj.metatype().make(obj)

    if isinstance(obj, type):
        descriptor = project_type(obj)
        return descriptor.metatype().make(descriptor)

    if get_origin(obj) is not None or isinstance(obj, PEP604Union):
        descriptor = project_type(obj)
        return descriptor.metatype().make(descriptor)

    if isinstance(obj, _pm.Builtin):
        descriptor = project_type(type(obj))
        return descriptor.make(obj)

    descriptor = _descriptor_for_value(obj)
    return descriptor.make(obj)


_project_type = project_type
