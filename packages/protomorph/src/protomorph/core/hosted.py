from __future__ import annotations

from typing import Any, cast

from ..abstract.contract import Item

from .. import core as mp
from .foundation import Anchor, Builtin
from .type_ import Type
from .carrier import TupleCarrier


# ── Host ───────────────────────────────────────────────────────────────


class Host(Builtin):
    """Base host — Spec/Qual delegate their Type interface here.

    Default implementation: everything is a leaf (no schema).
    Subclasses (e.g. NativeHost) override to provide actual structure.
    """

    # ── Type-level: Spec/Qual delegate arity/item_at/item/carrier ──

    def schema_for(self, spec: Spec) -> mp.VaryingType | None:
        """Return the field schema for data classified by this Spec.
        None means leaf / unknown type."""
        return None

    # ── Carrier-level: for future HostedCarrier ─────────────────────

    def val_is_leaf(self, meta: mp.Type, data: Any) -> bool:
        return True

    def val_children(
        self,
        meta: mp.Type,
        data: Any,
    ) -> tuple[mp.Carrier, ...]:
        return ()

    def val_reconstruct(
        self,
        meta: mp.Type,
        children: tuple[mp.Carrier, ...],
    ) -> Any:
        raise NotImplementedError


class AnchorType(Type[str]):
    """Special leaf descriptor for hosted anchor strings."""

    def metatype(self) -> mp.Type:
        return ANCHOR_TYPE

    def carrier(self, data: str) -> mp.Carrier[str]:
        return mp.LeafCarrier(self, data)


def _current_host() -> Host:
    return mp.HOST.get()


def _value_descriptor(value: mp.Type | mp.Carrier) -> mp.Type:
    if isinstance(value, mp.Type):
        return value.metatype()
    if isinstance(value, mp.Carrier):
        return value.descriptor
    return mp.native_type(type(value))


def _value_carrier(value: mp.Type | mp.Carrier) -> mp.Carrier:
    if isinstance(value, mp.Carrier):
        return value
    if isinstance(value, mp.Type):
        return mp.native_type(type(value)).make(value)
    return mp.wrap(value)


# ── Spec ───────────────────────────────────────────────────────────────


class Spec(TupleCarrier, Type):
    """Dual Carrier + Type.

    As Carrier: wraps (anchor, *args) as a typed tuple.
      descriptor = VaryingType(ANCHOR_TYPE, arg_type_1, arg_type_2, ...)
      __data__   = (anchor,    arg_1,      arg_2,      ...)

    As Type: classifies external data, delegating to HOST.

    .anchor  = head of the tuple (the spec's identity)
    .args    = tail carrier (the type parameters)
    """

    descriptor: mp.VaryingType

    @property
    def anchor(self) -> Anchor:
        return self.content[0]

    @property
    def args(self) -> TupleCarrier:
        tail_type = cast(mp.VaryingType, self.descriptor).tail
        tail_data = self.content[1:]
        return TupleCarrier(cast(mp.Type, tail_type), tail_data)

    # ── Type interface (delegates to HOST) ────────────────────

    def metatype(self) -> mp.Type:
        return Spec.of("std.metas.Specialization")

    @property
    def arity(self) -> int | None:
        schema = _current_host().schema_for(self)
        return schema.arity if schema is not None else 0

    def item_at(self, offset: int) -> Item:
        schema = _current_host().schema_for(self)
        if schema is None:
            raise IndexError(offset)
        return schema.item_at(offset)

    def item(self, id: mp.Id) -> Item:
        schema = _current_host().schema_for(self)
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    def carrier(self, data) -> mp.Carrier:
        schema = _current_host().schema_for(self)
        if schema is None:
            return mp.LeafCarrier(self, data)
        return mp.NativeObjectCarrier(self, data)

    def reconstruct(self, children: tuple[mp.Carrier, ...]) -> Spec:
        values = tuple(
            child if isinstance(child, (Spec, Qual)) else child.fetch()
            for child in children
        )
        return Spec.of(
            str(values[0]),
            *cast(tuple[mp.Type | mp.Carrier, ...], values[1:]),
        )

    # ── Construction ──────────────────────────────────────────

    @classmethod
    def of(cls, anchor: str, *args: mp.Type | mp.Carrier) -> Spec:
        field_types = (_ANCHOR_VALUE_TYPE,) + tuple(_value_descriptor(arg) for arg in args)
        spec_type = mp.VaryingType(mp.Index.Empty, field_types)
        spec_data = (Anchor(anchor),) + args
        return cls(spec_type, spec_data)


# ── Qual ───────────────────────────────────────────────────────────────


class Qual(TupleCarrier, Type):
    """A sequence of Specs — base type + qualifiers.

    As Carrier: wraps a tuple of Specs.
      descriptor = VaryingType(spec1.descriptor, spec2.descriptor, ...)
      __data__   = (spec1,                      spec2,            ...)

    As Type: classifies data, delegating to HOST via underlying Spec.

    Children ARE the Specs directly (they're already Carriers).

    .underlying  = first Spec (the base type)
    .qualifiers  = tail (remaining Specs)
    """

    descriptor: mp.VaryingType

    @property
    def underlying(self) -> mp.Type:
        return self.content[0]

    @property
    def qualifiers(self) -> tuple[Spec, ...]:
        return cast(tuple[Spec, ...], self.content[1:])

    # ── Carrier override: Specs are already Carriers ──────────

    def __getitem__(self, offset: int) -> mp.Carrier:
        return _value_carrier(self.content[offset])

    def reconstruct(self, children: tuple[mp.Carrier, ...]) -> Qual:
        values = tuple(
            child if isinstance(child, (Spec, Qual)) else child.fetch()
            for child in children
        )
        return Qual.of(cast(mp.Type, values[0]), *cast(tuple[Spec, ...], values[1:]))

    # ── Type interface (delegates to HOST via underlying) ─────

    def metatype(self) -> mp.Type:
        return Spec.of("std.metas.Qualifier")

    @property
    def arity(self) -> int | None:
        return self.underlying.arity

    def item_at(self, offset: int) -> Item:
        return self.underlying.item_at(offset)

    def item(self, id: mp.Id) -> Item:
        return self.underlying.item(id)

    def carrier(self, data) -> mp.Carrier:
        return self.underlying.carrier(data)

    # ── Construction ──────────────────────────────────────────

    @classmethod
    def of(cls, underlying: mp.Type, *qualifiers: Spec) -> Qual:
        values = (underlying,) + qualifiers
        field_types = tuple(_value_descriptor(value) for value in values)
        qual_type = mp.VaryingType(mp.Index.Empty, field_types)
        return cls(qual_type, values)


_ANCHOR_VALUE_TYPE = AnchorType()

# Anchor descriptor remains a public hosted Spec, while its internal payload
# is classified by the dedicated AnchorType leaf descriptor.
ANCHOR_TYPE = Spec(
    mp.VaryingType(mp.Index.Empty, (_ANCHOR_VALUE_TYPE,)),
    (Anchor("std.types.Anchor"),),
)
