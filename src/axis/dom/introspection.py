"""Builtin introspection for Axis DOM.

Resolves nominal anchors to structural attrs and reconstructs Builtin values
from decoded positional data.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import ClassVar, Protocol, cast, runtime_checkable

from protobase import Consed, Record, attr_info_of, cached_property, mutate

from axis import dom
from .base import _PENDING_CLASSES


_ENTRIES_BY_ANCHOR: dict[dom.Anchor, BuiltinEntry] = {}
_RESOLVED_FIELDS_BY_SPEC: dict[dom.Spec, dom.Struct[str, dom.Type]] = {}

_LITERAL_ANCHORS = {
    "std.Integer",
    "std.Text",
    "std.Boolean",
    "std.Decimal",
    "std.Empty",
    "std.Natural",
    "std.Whole",
}


@runtime_checkable
class Introspector(Protocol):
    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None: ...

    def class_for(self, type: dom.NominalType) -> type[dom.Builtin] | None: ...

    def construct(self, type: dom.NominalType, args: tuple[dom.Data, ...]) -> dom.Data: ...


class BuiltinEntry(dom.ContextProto, Consed):
    anchor: dom.Anchor
    builtin_cls: type[dom.Builtin]

    def lookup_bound(self, name: str) -> dom.Type | None:
        return None

    @cached_property
    def template(self) -> tuple[dom.Struct[str, dom.Type], frozenset[dom.Var]]:
        from .interop import python_to_axis_type

        attrs = attr_info_of(self.builtin_cls)
        if not attrs:
            return dom.Struct.Empty, frozenset()

        vars: set[dom.Var] = set()
        field_dict: dict[str, dom.Type] = {}
        for name, attr_info in attrs.items():
            field_dict[name] = python_to_axis_type(attr_info.type, ctx=self, vars=vars)

        return dom.Struct.new(**field_dict), frozenset(vars)

    @property
    def fields(self) -> dom.Struct[str, dom.Type]:
        return self.template[0]

    @property
    def vars(self) -> frozenset[dom.Var]:
        return self.template[1]

    @property
    def is_generic(self) -> bool:
        return bool(self.vars)


class VarGenericType(dom.VarType[BuiltinEntry]):
    ANCHOR: ClassVar[str] = "dom.Type.Var.Generic"


def _resolve_generics(entry: BuiltinEntry, spec: dom.Spec) -> dom.Struct[str, dom.Type]:
    """Substitute ``Var`` placeholders using spec args."""
    spec_args = spec.args
    if spec_args is None:
        def substitute_any(field_type: dom.Type) -> dom.Type:
            if isinstance(field_type, dom.Var):
                return dom.ANY_TYPE
            if isinstance(field_type, dom.NominalQualifier):
                new_underlying = substitute_any(field_type.underlying)
                if new_underlying is field_type.underlying:
                    return field_type
                return mutate(field_type, underlying=new_underlying)
            if isinstance(field_type, dom.StructType):
                new_attrs = field_type.meta_attrs.map(substitute_any)
                if new_attrs is field_type.meta_attrs:
                    return field_type
                return mutate(field_type, meta_attrs=new_attrs)
            if isinstance(field_type, dom.UnionType):
                new_types = frozenset(substitute_any(t) for t in field_type.types)
                if new_types == field_type.types:
                    return field_type
                return dom.UnionType(types=new_types)
            return field_type

        return entry.fields.map(substitute_any)

    def resolve_binding(binding: dom.Val | None) -> dom.Type:
        if isinstance(binding, dom.Var):
            return binding
        if isinstance(binding, dom.Const) and isinstance(binding.data, dom.Type):
            return binding.data
        return dom.ANY_TYPE

    def substitute(field_type: dom.Type) -> dom.Type:
        if isinstance(field_type, dom.Var):
            return resolve_binding(spec_args.get(field_type.data, default=None))
        if isinstance(field_type, dom.NominalQualifier):
            new_underlying = substitute(field_type.underlying)
            if new_underlying is field_type.underlying:
                return field_type
            return mutate(field_type, underlying=new_underlying)
        if isinstance(field_type, dom.StructType):
            new_attrs = field_type.meta_attrs.map(substitute)
            if new_attrs is field_type.meta_attrs:
                return field_type
            return mutate(field_type, meta_attrs=new_attrs)
        if isinstance(field_type, dom.UnionType):
            new_types = frozenset(substitute(t) for t in field_type.types)
            if new_types == field_type.types:
                return field_type
            return dom.UnionType(types=new_types)
        return field_type

    return entry.fields.map(substitute)


class NativeIntrospector(Record):
    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None:
        drain_pending()

        spec = type.spec_ref
        anchor = dom.Anchor(data=spec.segments)
        if spec.path in _LITERAL_ANCHORS:
            return None

        cached = _RESOLVED_FIELDS_BY_SPEC.get(spec)
        if cached is not None:
            return cached

        entry = _ENTRIES_BY_ANCHOR.get(anchor)
        if entry is None:
            return None
        if not entry.is_generic:
            return entry.fields

        resolved = _resolve_generics(entry, spec)
        _RESOLVED_FIELDS_BY_SPEC[spec] = resolved
        return resolved

    def class_for(self, type: dom.NominalType) -> type[dom.Builtin] | None:
        drain_pending()
        anchor = dom.Anchor(data=type.spec_ref.segments)
        entry = _ENTRIES_BY_ANCHOR.get(anchor)
        return entry.builtin_cls if entry is not None else None

    def construct(self, type: dom.NominalType, args: tuple[dom.Data, ...]) -> dom.Data:
        builtin_cls = self.class_for(type)
        anchor_path = type.spec_ref.path
        if builtin_cls is None:
            raise ValueError(
                f"Cannot decode {anchor_path}: no registered builtin class for {type!r}"
            )

        if builtin_cls is dom.NominalType:
            if len(args) != 1:
                raise ValueError(
                    f"Cannot decode {anchor_path}: expected 1 decoded arg for NominalType, got {len(args)}"
                )

            spec_ref = args[0]
            if isinstance(spec_ref, dom.Spec):
                return dom.NominalType(spec_ref=spec_ref)
            if not isinstance(spec_ref, tuple) or len(spec_ref) != 2:
                raise ValueError(
                    f"Cannot decode {anchor_path}: expected Spec payload tuple(anchor, spec), got {spec_ref!r}"
                )

            spec_type = dom.SpecType(meta_args=type.spec_ref.type.meta_args)
            return dom.NominalType(
                spec_ref=dom.Spec(type=spec_type, data=cast(tuple[tuple[str, ...], dom.Data], spec_ref))
            )

        fields = self.fields(type)
        if fields is None:
            raise ValueError(
                f"Cannot decode {anchor_path}: no field schema available for {type!r}"
            )
        if len(args) != len(fields):
            raise ValueError(
                f"Cannot decode {anchor_path}: expected {len(fields)} decoded args, got {len(args)}"
            )

        attrs: dict[str, dom.Data] = {}
        for key, value in zip(fields.index.keys, args):
            if key is None:
                raise ValueError(
                    f"Cannot decode {anchor_path}: positional fields are not supported for builtin construction"
                )
            attrs[key] = value

        try:
            return cast(dom.Data, builtin_cls(**attrs))
        except Exception as exc:
            raise ValueError(
                f"Cannot decode {anchor_path}: failed to construct {builtin_cls.__name__} from {attrs!r}"
            ) from exc


DEFAULT_INTROSPECTOR: Introspector = NativeIntrospector()

INTROSPECTOR: ContextVar[Introspector] = ContextVar(
    "axis.dom.introspection.INTROSPECTOR",
    default=DEFAULT_INTROSPECTOR,
)


def drain_pending() -> None:
    if not _PENDING_CLASSES:
        return

    while _PENDING_CLASSES:
        cls = _PENDING_CLASSES.pop()
        anchor = dom.anchor(cls._anchor_path())
        _ENTRIES_BY_ANCHOR[anchor] = BuiltinEntry(anchor=anchor, builtin_cls=cls)
