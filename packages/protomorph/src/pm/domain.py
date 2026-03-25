from __future__ import annotations

from itertools import chain
from typing import Any, cast, Self

from .abstract.contract import Item

import pm
from .foundation import Builtin, Id
from .type_ import Type, Placeholder
from .index import Index, Tuple, Spread


class UniformType[T](Type[tuple[T, ...]]):
    """Homogeneous collection — arity from index if present, else from data."""

    element_type: pm.Type[T]
    index: Index

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Uniform", self.element_type.metatype())

    @property
    def arity(self) -> int | None:
        if self.index is not Index.Empty:
            return len(self.index)
        return None  # carrier infers from data

    def item_at(self, offset: int) -> Item:
        key = self.index[offset] if self.index is not Index.Empty else None
        return Item(offset, key, self.element_type)

    def item(self, id: Id) -> Item:
        if self.index is Index.Empty:
            raise KeyError(id)
        offset = self.index.offset_of(id)
        return Item(offset, id, self.element_type)

    def carrier(self, data) -> pm.TupleCarrier:
        return pm.TupleCarrier(self, data)


class UnionType[T: tuple[Any, ...]](Type[T]):
    """Union of types — leaf in structure, carrier dispatches at runtime."""

    variants: frozenset[pm.Type]

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Union")

    def carrier(self, data) -> pm.LeafCarrier:
        return pm.LeafCarrier(self, data)

    @classmethod
    def of(cls, *types: pm.Type) -> pm.Type:
        """Build a union, flattening nested unions. Returns single type if only one."""
        flat: set[pm.Type] = set()
        for t in types:
            if isinstance(t, UnionType):
                flat.update(t.variants)
            else:
                flat.add(t)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))


class VaryingType[T: tuple[Any, ...]](Tuple[Id | None, Type], Type[tuple]):
    """Heterogeneous tuple type — IS a Tuple[Id, Type].

    Inherits structural protocol from Tuple (item_at, item, items,
    __len__, __iter__).  values = the field types, index = the field keys.
    """

    def metatype(self) -> Type:
        return VaryingType(self.index, tuple(t.metatype() for t in self.values))

    @property
    def arity(self) -> int:
        return len(self.values)

    @classmethod
    def new(cls, *vals: pm.Carrier, **kwvals: pm.Carrier) -> pm.Carrier:
        return cls.of(
            *(val.descriptor for val in vals),
            **{k: v.descriptor for k, v in kwvals.items()},
        ).make(tuple(chain(vals, kwvals.values())))


class NativeType(Type):
    """Type derived from a Builtin class's field annotations.

    Structure delegates to `schema` — a VaryingType that holds
    the field names and types as traversable data.
    This means Placeholders from TypeVars are stored in the schema
    and visible to Val traversal / subst.
    """

    builtin_cls: type[Builtin]
    schema: VaryingType

    def metatype(self) -> Type:
        return pm.Spec.of("std.metas.Native", self.schema)

    @property
    def arity(self) -> int:
        return self.schema.arity

    def item_at(self, offset: int) -> Item:
        return self.schema.item_at(offset)

    def item(self, id: Id) -> Item:
        return self.schema.item(id)

    def carrier(self, data) -> pm.NativeObjectCarrier:
        return pm.NativeObjectCarrier(self, data)

    def specialize(self, mapping: dict[Placeholder, pm.Type]) -> NativeType:
        """Substitute Placeholders in field types, returning a new NativeType.

        Spread placeholders (*T) are replaced with Spread(...) sentinels
        inside the carrier subst, then splice() flattens them.
        """

        def _make_replacement(ph: Placeholder) -> Any:
            """Build the replacement data for a placeholder."""
            replacement = mapping[ph]
            if ph.id.startswith("*") and isinstance(replacement, VaryingType):
                return Spread(replacement.values)
            return replacement

        new_types: list[pm.Type] = []
        for ft in self.schema.values:
            # Direct placeholder at schema level
            if isinstance(ft, Placeholder) and ft in mapping:
                new_types.append(_make_replacement(ft))
                continue
            if isinstance(ft, UniformType):
                element_type = ft.element_type
                if isinstance(element_type, Placeholder) and element_type in mapping:
                    replacement = mapping[element_type]
                    if isinstance(replacement, VaryingType):
                        new_types.append(replacement)
                    else:
                        new_types.append(UniformType(replacement, ft.index))
                    continue
            if isinstance(ft, VaryingType):
                replaced_values = []
                changed = False
                for item_type in ft.values:
                    if isinstance(item_type, Placeholder) and item_type in mapping:
                        replacement = mapping[item_type]
                        if isinstance(replacement, VaryingType):
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
                            VaryingType(ft.index, tuple(replaced_values)).splice(),
                        )
                    )
                    continue
            # Traverse field type, substitute leaves (including nested spreads)
            ft_carrier = pm.wrap(ft)
            carrier_mapping = {}
            for leaf in ft_carrier.deep_iter():
                data = leaf.fetch()
                if data in mapping:
                    repl = _make_replacement(data)
                    carrier_mapping[leaf] = pm.LeafCarrier(leaf.descriptor, repl)
            if carrier_mapping:
                result = ft_carrier.subst(carrier_mapping).fetch()
                # If result is a Tuple-like with Spreads, splice them
                if isinstance(result, Tuple):
                    result = result.splice()
                new_types.append(cast(pm.Type, result))
            else:
                new_types.append(ft)
        new_schema = cast(
            VaryingType,
            VaryingType(self.schema.index, tuple(new_types)).splice(),
        )
        return NativeType(self.builtin_cls, new_schema)
