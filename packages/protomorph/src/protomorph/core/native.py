from __future__ import annotations

from types import UnionType as PEP604Union
from typing import Any, Callable, TypeVar, Union, cast, get_args, get_origin

from protobase import Consed, attr_info_of, flux, frozendict

from .foundation import Builtin, Data, Meta, OMEGA, _ALL_BUILTINS
from .hosted import Host, Hosted, Qual, Spec, Bool, Float, Id, Integer, Text
from .placeholder import Placeholder, Var
from .schema import VaryingSchema
from .variant import Union as CoreUnion

__all__ = [
    "NativeVarContext",
    "NativeType",
    "NativeHost",
    "NATIVE_HOST",
    "register_native_meta",
    "register_python_transform",
    "meta_from_native",
]

type PythonTransform = Callable[..., Meta]

_NATIVE_METAS: dict[type, Meta] = {
    int: Integer,
    str: Text,
    float: Float,
    bool: Bool,
    type(None): OMEGA,
}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}


class NativeVarContext(Builtin):
    builtin_cls: type[Builtin] | None = None


class NativeType(Builtin):

    class Template(Builtin):
        builtin_cls: type[Builtin]

        @flux.property
        def spec_name(self) -> str:
            return _spec_name(self.builtin_cls)

        @flux.property
        def params(self) -> frozendict[str, Placeholder]:
            parameters = tuple(getattr(self.builtin_cls, "__parameters__", ()))
            ctx = NativeVarContext(builtin_cls=self.builtin_cls)
            var_meta = Var(Var.Ground, ctx)
            return frozendict(
                {tp.__name__: Placeholder(var_meta, tp.__name__) for tp in parameters}
            )

        @flux.property
        def fields(self) -> VaryingSchema[str]:
            attrs = attr_info_of(self.builtin_cls)
            if not attrs:
                return VaryingSchema.of(index=_field_index())
            names = tuple(attrs.keys())
            metas = tuple(
                meta_from_native(info.type, template=self)
                for info in attrs.values()
            )
            return VaryingSchema.of(*metas, index=_field_index(*names))

        def specialize(self, params) -> NativeType:
            return NativeType(template=self, specialization=params)

    template: Template
    specialization: Any


class NativeHost(Host, Consed):

    @flux.property
    def all_builtins(self) -> frozenset[type[Builtin]]:
        return frozenset(_ALL_BUILTINS)

    @flux.property
    def native_metas(self) -> frozendict[type, Meta]:
        return frozendict(_NATIVE_METAS)

    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        return frozendict(_PYTHON_TRANSFORMS)

    @flux.method
    def template_for(self, builtin_cls: type[Builtin]) -> NativeType.Template:
        return NativeType.Template(builtin_cls=builtin_cls)

    @flux.property
    def template_by_spec_name(self) -> frozendict[str, NativeType.Template]:
        result: dict[str, NativeType.Template] = {}
        for cls in self.all_builtins:
            template = self.template_for(cls)
            result[template.spec_name] = template
        return frozendict(result)

    @flux.method
    def meta_from_annotation(
        self,
        annotation: Any,
        *,
        template: NativeType.Template | None = None,
    ) -> Meta:
        if isinstance(annotation, Meta):
            return annotation

        if annotation is None:
            return OMEGA

        if isinstance(annotation, TypeVar):
            return _meta_from_typevar(annotation, template=template)

        if annotation is Any:
            return OMEGA

        scalar = self.native_metas.get(annotation)
        if scalar is not None:
            return scalar

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union or isinstance(annotation, PEP604Union):
            return _union_of(
                self.meta_from_annotation(arg, template=template)
                for arg in args
            )

        if origin is not None:
            transform = self.python_transforms.get(origin)
            if transform is not None:
                converted = tuple(
                    self.meta_from_annotation(arg, template=template)
                    if arg is not Ellipsis
                    else arg
                    for arg in args
                )
                return transform(*converted)

            if isinstance(origin, type) and issubclass(origin, Builtin):
                return _build_builtin_spec(origin, args, registry=self, template=template)

        if isinstance(annotation, type) and issubclass(annotation, Builtin):
            return Spec.of(_spec_name(annotation))

        return OMEGA

    @flux.method
    def fields_for_spec(self, spec: Spec) -> VaryingSchema[str]:
        template = self.template_by_spec_name.get(spec.path)
        if template is None:
            return VaryingSchema.of(index=_field_index())
        if not template.params:
            return template.fields
        if spec.args.arity != len(template.params):
            return VaryingSchema.of(index=_field_index())

        bindings = frozendict(
            {
                placeholder: arg
                for placeholder, arg in zip(template.params.values(), spec.args)
            }
        )
        return cast(VaryingSchema[str], template.fields.subst(bindings))

    @flux.property
    def type_by_spec_name(self) -> frozendict[str, NativeType.Template]:
        return self.template_by_spec_name

    def val_is_leaf(self, meta: Meta, data: Data) -> bool:
        if not isinstance(meta, Spec):
            return True
        return self.fields_for_spec(meta).arity == 0

    def val_children(self, meta: Meta, data: Data) -> tuple:
        if not isinstance(meta, Spec):
            return ()
        fields = self.fields_for_spec(meta)
        return fields.wrap_named(data)

    def val_reconstruct(self, meta: Meta, children: tuple) -> Hosted:
        if not isinstance(meta, Spec):
            raise NotImplementedError
        template = self.type_by_spec_name[meta.path]
        fields = self.fields_for_spec(meta)
        attrs = fields.attrs_from_children(children)
        return Hosted(meta, template.builtin_cls(**attrs))


def register_native_meta(native_type: type, meta: Meta) -> None:
    _NATIVE_METAS[native_type] = meta
    NativeHost.native_metas.invalidate_for(NATIVE_HOST)


def register_python_transform(origin: type, transform: PythonTransform) -> None:
    _PYTHON_TRANSFORMS[origin] = transform
    NativeHost.python_transforms.invalidate_for(NATIVE_HOST)


def meta_from_native(
    annotation: Any,
    *,
    template: NativeType.Template | None = None,
    registry: NativeHost | None = None,
) -> Meta:
    resolved_registry = registry or NATIVE_HOST
    return resolved_registry.meta_from_annotation(annotation, template=template)


def _spec_name(cls: type[Builtin]) -> str:
    name = getattr(cls, "SPEC_NAME", None)
    if isinstance(name, str):
        return name
    return f"{cls.__module__}.{cls.__qualname__}"


def _meta_from_typevar(
    annotation: TypeVar,
    *,
    template: NativeType.Template | None,
) -> Meta:
    name = annotation.__name__
    if template is not None and name in template.params:
        return cast(Meta, template.params[name])
    return cast(Meta, Placeholder(Var(Var.Ground, None), name))


def _union_of(metas) -> Meta:
    values = frozenset(metas)
    if len(values) == 1:
        return next(iter(values))
    return CoreUnion(CoreUnion.Ground, values)


def _build_builtin_spec(
    builtin_cls: type[Builtin],
    args: tuple[Any, ...],
    *,
    registry: NativeHost,
    template: NativeType.Template | None,
) -> Spec:
    if not args:
        return Spec.of(_spec_name(builtin_cls))
    params = [registry.meta_from_annotation(arg, template=template) for arg in args]
    return Spec.of(_spec_name(builtin_cls), *params)


def _list_transform(elem: Meta) -> Meta:
    return Qual.of(elem, Spec.of("std.qualifiers.List"))


def _set_transform(elem: Meta) -> Meta:
    return Qual.of(elem, Spec.of("std.qualifiers.Set"))


def _frozenset_transform(elem: Meta) -> Meta:
    return Qual.of(elem, Spec.of("std.qualifiers.FrozenSet"))


def _dict_transform(key: Meta, val: Meta) -> Meta:
    return Qual.of(val, Spec.of("std.qualifiers.Dict", K=key))


def _tuple_transform(*args: Meta | object) -> Meta:
    if len(args) == 2 and args[1] is Ellipsis:
        return Qual.of(cast(Meta, args[0]), Spec.of("std.qualifiers.List"))
    if any(arg is Ellipsis for arg in args):
        return OMEGA
    return Spec.of("std.core.Tuple", *cast(tuple[Meta, ...], args))


def _field_index(*names: str):
    from .index import INDEX_GROUND, Index, IndexKeyMeta

    return Index(IndexKeyMeta(INDEX_GROUND, Id), names)


NATIVE_HOST = NativeHost()

register_python_transform(list, _list_transform)
register_python_transform(set, _set_transform)
register_python_transform(frozenset, _frozenset_transform)
register_python_transform(dict, _dict_transform)
register_python_transform(tuple, _tuple_transform)
