from __future__ import annotations

from types import UnionType as PEP604Union
from typing import Any, TypeVar, Union, get_args, get_origin

from protobase import attr_info_of, flux, frozendict

from .foundation import Builtin, Data, Meta, Val, OMEGA, _ALL_BUILTINS
#from .ground import Ground, Single, Integer, Id
from .placeholder import Var, Placeholder
from .hosted import Host, Spec, Qual, Hosted, Ground, Id, Integer, Text, Float, Bool
from .. import core


# ── Ground helper ──────────────────────────────────────────────────────


def _ground_for(cls: type[Builtin]) -> str:
    ground = getattr(cls, "GROUND", None)
    if ground is not None:
        return ground
    return f"{cls.__module__}.{cls.__qualname__}"


# ── NativeType ─────────────────────────────────────────────────────────


class NativeType(Builtin):

    class Template(Builtin):
        builtin_cls: type[Builtin]

        @flux.property
        def ground(self) -> str:
            return _ground_for(self.builtin_cls)

        @flux.property
        def params(self) -> frozendict[str, Placeholder]:
            parameters = getattr(self.builtin_cls, "__parameters__", ())
            ctx_var = Var(OMEGA, self)
            return frozendict(
                {tp.__name__: Placeholder(ctx_var, tp.__name__) for tp in parameters}
            )

        @flux.property
        def fields(self) -> frozendict[str, Meta]:
            attrs = attr_info_of(self.builtin_cls)
            if not attrs:
                return frozendict()
            return frozendict(
                {
                    name: meta_from_native(info.type, template=self)
                    for name, info in attrs.items()
                }
            )

        def specialize(self, params: core.Tuple) -> NativeType:
            return NativeType(template=self, specialization=params)

    template: Template
    specialization: core.Tuple


# ── Scalar meta registry ───────────────────────────────────────────────


_SCALAR_METAS: dict[type, Meta] = {
    int: Integer,
    str: Text,
    float: Float,
    bool: Bool,
    type(None): OMEGA,
}


# ── Qual helpers ───────────────────────────────────────────────────────

# Qualifier grounds for Python container types
_LIST_QUAL_GROUND = Ground(OMEGA, "std.qualifiers.List")
_SET_QUAL_GROUND = Ground(OMEGA, "std.qualifiers.Set")
_FROZENSET_QUAL_GROUND = Ground(OMEGA, "std.qualifiers.FrozenSet")
_DICT_QUAL_GROUND = Ground(OMEGA, "std.qualifiers.Dict")


def _raw_meta_tuple(*metas: Meta) -> core.Tuple:
    """Build a Tuple whose raw __data__ are Meta objects (for Qual internals).

    Each element's field schema is the Meta's own __meta__, so Tuple.at(i)
    reconstructs the original Meta via hash-consing — except for Anchors whose
    __meta__ is OMEGA (Omega has no Carrier). Access via __data__[i] is always
    safe; use Qual.underlying / Qual.qualifiers for typed projections.
    """
    schema_metas = tuple(m.__meta__ for m in metas)
    schema = core.VaryingSchema(OMEGA, schema_metas)
    return core.Tuple(schema, metas)


def _list_qual(elem: Meta) -> Qual:
    return Qual(OMEGA, _raw_meta_tuple(elem, Spec(_LIST_QUAL_GROUND, core.Tuple.empty())))


def _set_qual(elem: Meta) -> Qual:
    return Qual(OMEGA, _raw_meta_tuple(elem, Spec(_SET_QUAL_GROUND, core.Tuple.empty())))


def _frozenset_qual(elem: Meta) -> Qual:
    return Qual(OMEGA, _raw_meta_tuple(elem, Spec(_FROZENSET_QUAL_GROUND, core.Tuple.empty())))


def _dict_qual(key: Meta, val: Meta) -> Qual:
    val_args = _raw_meta_tuple(val)
    return Qual(OMEGA, _raw_meta_tuple(key, Spec(_DICT_QUAL_GROUND, val_args)))


# ── meta_from_native ───────────────────────────────────────────────────


def meta_from_native(
    annotation: Any,
    *,
    template: NativeType.Template | None = None,
) -> Meta:
    """Translate a Python type annotation to a core Meta."""
    if isinstance(annotation, Meta):
        return annotation

    if annotation is None:
        return OMEGA

    # TypeVar → Placeholder bound to the owning Template
    if isinstance(annotation, TypeVar):
        name = annotation.__name__
        if template is not None and name in template.params:
            return template.params[name]
        return Placeholder(Var(OMEGA, None), name)

    # Scalar Python types
    scalar = _SCALAR_METAS.get(annotation)
    if scalar is not None:
        return scalar

    # Union / PEP 604  (X | Y)
    origin = get_origin(annotation)
    args = get_args(annotation)
    if origin is Union or isinstance(annotation, PEP604Union):
        metas: frozenset[Meta] = frozenset(
            meta_from_native(a, template=template) for a in args
        )
        if len(metas) == 1:
            return next(iter(metas))
        from .variant import Union as CoreUnion
        return CoreUnion(OMEGA, metas)

    # Python container types → Qual
    if origin is list:
        elem = meta_from_native(args[0] if args else None, template=template)
        return _list_qual(elem)
    if origin is set:
        elem = meta_from_native(args[0] if args else None, template=template)
        return _set_qual(elem)
    if origin is frozenset:
        elem = meta_from_native(args[0] if args else None, template=template)
        return _frozenset_qual(elem)
    if origin is dict:
        key = meta_from_native(args[0] if args else None, template=template)
        val = meta_from_native(args[1] if len(args) > 1 else None, template=template)
        return _dict_qual(key, val)
    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            elem = meta_from_native(args[0], template=template)
            return _list_qual(elem)
        # tuple[T1, T2, ...] → structural; fall through to Fallback for now
        return OMEGA

    # Generic Builtin  (e.g. Box[T])
    if origin is not None and isinstance(origin, type) and issubclass(origin, Builtin):
        path = _ground_for(origin)
        if args:
            param_metas = [meta_from_native(a, template=template) for a in args]
            params_tuple = core.Tuple.varying_of(param_metas)
        else:
            params_tuple = core.Tuple.Empty
        return Spec(Spec.Ground, (path, params_tuple))

    # Non-generic Builtin subclass
    if isinstance(annotation, type) and issubclass(annotation, Builtin):
        path = _ground_for(annotation)
        return Spec(Spec.Ground, (path, core.Tuple.Empty))

    # Fallback
    return OMEGA


# ── NativeHost ─────────────────────────────────────────────────────────


class NativeHost(Host):

    @flux.property
    def type_by_ground(self) -> frozendict[str, NativeType.Template]:
        result: dict[str, NativeType.Template] = {}
        for cls in _ALL_BUILTINS:
            t = NativeType.Template(builtin_cls=cls)
            result[t.ground] = t
        return frozendict(result)

    # ── Hosted values (Builtin decomposition) ──────────────────────────

    def val_is_leaf(self, meta: Meta, data: Data) -> bool:
        if not isinstance(meta, Spec):
            return True
        template = self.type_by_ground.get(meta.path)
        return template is None or len(template.fields) == 0

    def val_children(self, meta: Meta, data: Data) -> tuple[Val, ...]:
        if not isinstance(meta, Spec):
            return ()
        template = self.type_by_ground.get(meta.path)
        if template is None:
            return ()
        fields = template.fields
        return tuple(
            field_meta.wrap(getattr(data, name))
            for name, field_meta in fields.items()
        )

    def val_reconstruct(self, meta: Meta, children: tuple[Val, ...]) -> Val:
        if not isinstance(meta, Spec):
            raise NotImplementedError
        template = self.type_by_ground[meta.path]
        fields = template.fields
        attrs = {
            name: child.__data__
            for (name, _), child in zip(fields.items(), children)
        }
        instance = template.builtin_cls(**attrs)
        return Hosted(meta, instance)

NATIVE_HOST = NativeHost()
