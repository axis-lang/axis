from __future__ import annotations

from typing import Any, cast, ClassVar
from itertools import chain

from .abstract.contract import Item

import pm
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

    def schema_for(self, spec: Spec) -> pm.VaryingType | None:
        """Return the field schema for data classified by this Spec.
        None means leaf / unknown type."""
        return None

    # ── Val-level: for future HostedCarrier ─────────────────────

    def val_is_leaf(self, meta: pm.Type, data: Any) -> bool:
        return True

    def val_children(
        self,
        meta: pm.Type,
        data: Any,
    ) -> tuple[pm.Carrier, ...]:
        return ()

    def val_reconstruct(
        self,
        meta: pm.Type,
        children: tuple[pm.Carrier, ...],
    ) -> Any:
        raise NotImplementedError


class AnchorType(Type[pm.Anchor]):
    """Special leaf descriptor for hosted anchor strings."""

    Singleton: ClassVar[AnchorType]

    def metatype(self) -> pm.Type:
        return Spec.of("std.metas.Anchot")
        # return ANCHOR_TYPE


AnchorType.Singleton = AnchorType()


def anchor(content: str | pm.Anchor) -> pm.LeafCarrier[Anchor]:
    return pm.LeafCarrier(AnchorType.Singleton, pm.Anchor(content))


def _current_host() -> Host:
    return pm.HOST.get()


def _value_descriptor(value: pm.Type | pm.Carrier) -> pm.Type:
    if isinstance(value, pm.Type):
        return value.metatype()
    if isinstance(value, pm.Carrier):
        return value.descriptor
    return pm.native_type(type(value))


def _value_carrier(value: pm.Type | pm.Carrier) -> pm.Carrier:
    if isinstance(value, pm.Carrier):
        return value
    if isinstance(value, pm.Type):
        return pm.native_type(type(value)).make(value)
    return pm.wrap(value)


# ── Spec ───────────────────────────────────────────────────────────────


class Spec(TupleCarrier, Type):
    """Dual Val + Type.

    As Val: wraps (anchor, *args) as a typed tuple.
      descriptor = VaryingType(ANCHOR_TYPE, arg_type_1, arg_type_2, ...)
      __data__   = (anchor,    arg_1,      arg_2,      ...)

    As Type: classifies external data, delegating to HOST.

    .anchor  = head of the tuple (the spec's identity)
    .args    = tail carrier (the type parameters)
    """

    descriptor: pm.VaryingType

    @property
    def anchor(self) -> Anchor:
        return self.content[0]

    @property
    def args(self) -> TupleCarrier:
        tail_type = cast(pm.VaryingType, self.descriptor).tail
        tail_data = self.content[1:]
        return TupleCarrier(cast(pm.Type, tail_type), tail_data)

    # ── Type interface (delegates to HOST) ────────────────────

    def metatype(self) -> pm.Type:
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

    def item(self, id: pm.Id) -> Item:
        schema = _current_host().schema_for(self)
        if schema is None:
            raise KeyError(id)
        return schema.item(id)

    def carrier(self, data) -> pm.Carrier:
        schema = _current_host().schema_for(self)
        if schema is None:
            return pm.LeafCarrier(self, data)
        return pm.NativeObjectCarrier(self, data)

    def reconstruct(self, children: tuple[pm.Carrier, ...]) -> Spec:
        values = tuple(
            child if isinstance(child, (Spec, Qual)) else child.fetch()
            for child in children
        )
        return Spec.of(
            str(values[0]),
            *cast(tuple[pm.Type | pm.Carrier, ...], values[1:]),
        )

    # ── Construction ──────────────────────────────────────────

    @classmethod
    def of(cls, anchor: str, *args: pm.Type | pm.Carrier) -> Spec:
        field_types = (_ANCHOR_VALUE_TYPE,) + tuple(
            _value_descriptor(arg) for arg in args
        )
        spec_type = pm.VaryingType(pm.Index.Empty, field_types)
        spec_data = (Anchor(anchor),) + args
        return cls(spec_type, spec_data)

    @classmethod
    def new(
        cls, anchor: pm.Carrier[Anchor], *vals: pm.Carrier, **kwvals: pm.Carrier
    ) -> Spec:
        return cls(
            pm.VaryingType.of(
                AnchorType.Singleton,
                *(val.descriptor for val in vals),
                **{k: v.descriptor for k, v in kwvals.items()},
            ),
            (anchor,) + vals + tuple(kwvals.values()),
        )
        
        # pm.VaryingType.of()
        # vt = pm.VaryingType.new(anchor, *args, **kwargs)
        # return cls(vt.descriptor, vt.content)


# ── Qual ───────────────────────────────────────────────────────────────


class Qual(TupleCarrier, Type):
    """A sequence of Specs — base type + qualifiers.

    As Val: wraps a tuple of Specs.
      descriptor = VaryingType(spec1.descriptor, spec2.descriptor, ...)
      __data__   = (spec1,                      spec2,            ...)

    As Type: classifies data, delegating to HOST via underlying Spec.

    Children ARE the Specs directly (they're already Carriers).

    .underlying  = first Spec (the base type)
    .qualifiers  = tail (remaining Specs)
    """

    descriptor: pm.VaryingType

    @property
    def underlying(self) -> pm.Type:
        return self.content[0]

    @property
    def qualifiers(self) -> tuple[Spec, ...]:
        return cast(tuple[Spec, ...], self.content[1:])

    # ── Val override: Specs are already Carriers ──────────

    def __getitem__(self, offset: int) -> pm.Carrier:
        return _value_carrier(self.content[offset])

    def reconstruct(self, children: tuple[pm.Carrier, ...]) -> Qual:
        values = tuple(
            child if isinstance(child, (Spec, Qual)) else child.fetch()
            for child in children
        )
        return Qual.of(cast(pm.Type, values[0]), *cast(tuple[Spec, ...], values[1:]))

    # ── Type interface (delegates to HOST via underlying) ─────

    def metatype(self) -> pm.Type:
        return Spec.of("std.metas.Qualifier")

    @property
    def arity(self) -> int | None:
        return self.underlying.arity

    def item_at(self, offset: int) -> Item:
        return self.underlying.item_at(offset)

    def item(self, id: pm.Id) -> Item:
        return self.underlying.item(id)

    def carrier(self, data) -> pm.Carrier:
        return self.underlying.carrier(data)

    # ── Construction ──────────────────────────────────────────

    @classmethod
    def of(cls, underlying: pm.Type, *qualifiers: Spec) -> Qual:
        values = (underlying,) + qualifiers
        field_types = tuple(_value_descriptor(value) for value in values)
        qual_type = pm.VaryingType(pm.Index.Empty, field_types)
        return cls(qual_type, values)


_ANCHOR_VALUE_TYPE = AnchorType()

# Anchor descriptor remains a public hosted Spec, while its internal payload
# is classified by the dedicated AnchorType leaf descriptor.
ANCHOR_TYPE = Spec(
    pm.VaryingType(pm.Index.Empty, (_ANCHOR_VALUE_TYPE,)),
    (Anchor("std.types.Anchor"),),
)
