from __future__ import annotations

from typing import Any

from .. import draft as mp
from .foundation import Builtin, Id
from .type_ import Type, OMEGA, Placeholder
from .index import Tuple, Spread


class ScalarType(Type):
    """Leaf type for Python scalars.  arity=0 (inherited default)."""

    python_type: type

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> mp.LeafCarrier:
        return mp.LeafCarrier(self, data)


INT_TYPE = ScalarType(int)
STR_TYPE = ScalarType(str)
FLOAT_TYPE = ScalarType(float)
BOOL_TYPE = ScalarType(bool)
NONE_TYPE = ScalarType(type(None))

_SCALAR_TYPES: dict[type, ScalarType] = {
    int: INT_TYPE,
    str: STR_TYPE,
    float: FLOAT_TYPE,
    bool: BOOL_TYPE,
    type(None): NONE_TYPE,
}


class UniformType[T](Type[tuple[T, ...]]):
    """Homogeneous collection — arity and index come from __data__."""

    element_type: mp.Type[T]

    def metatype(self) -> Type:
        return OMEGA

    @property
    def arity(self) -> int | None:
        return None  # unknown until we see data

    def field_at(self, offset: int) -> mp.Field:
        return mp.Field(offset, None, self.element_type)

    def field(self, id: Id) -> mp.Field:
        raise KeyError(id)  # no index at the type level

    def carrier(self, data) -> mp.TupleCarrier:
        return mp.TupleCarrier(self, data)


class UnionType(Type):
    """Union of types — leaf in structure, carrier dispatches at runtime."""

    variants: frozenset[mp.Type]

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> mp.LeafCarrier:
        return mp.LeafCarrier(self, data)

    @classmethod
    def of(cls, *types: mp.Type) -> mp.Type:
        """Build a union, flattening nested unions. Returns single type if only one."""
        flat: set[mp.Type] = set()
        for t in types:
            if isinstance(t, UnionType):
                flat.update(t.variants)
            else:
                flat.add(t)
        if len(flat) == 1:
            return next(iter(flat))
        return cls(frozenset(flat))


class VaryingType(Type[tuple], Tuple[Id, Type]):
    """Heterogeneous tuple type — IS a Tuple[Id, Type].

    Inherits index and values from Tuple.
    values = the field types, index = the field keys.
    """

    def metatype(self) -> Type:
        return OMEGA

    @property
    def arity(self) -> int:
        return len(self.values)

    def field_at(self, offset: int) -> mp.Field:
        key = self.index.keys[offset] if self.index else None
        return mp.Field(offset, key, self.values[offset])

    def field(self, id: Id) -> mp.Field:
        if not self.index:
            raise KeyError(id)
        offset = self.index.offset_of(id)
        return mp.Field(offset, id, self.values[offset])

    def carrier(self, data) -> mp.TupleCarrier:
        return mp.TupleCarrier(self, data)


class NativeType(Type):
    """Type derived from a Builtin class's field annotations.

    Structure delegates to `schema` — a VaryingType that holds
    the field names and types as traversable data.
    This means Placeholders from TypeVars are stored in the schema
    and visible to Carrier traversal / subst.
    """

    builtin_cls: type[Builtin]
    schema: VaryingType

    def metatype(self) -> Type:
        return OMEGA

    @property
    def arity(self) -> int:
        return self.schema.arity

    def field_at(self, offset: int) -> mp.Field:
        return self.schema.field_at(offset)

    def field(self, id: Id) -> mp.Field:
        return self.schema.field(id)

    def carrier(self, data) -> mp.NativeObjectCarrier:
        return mp.NativeObjectCarrier(self, data)

    def specialize(self, mapping: dict[Placeholder, mp.Type]) -> NativeType:
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

        new_types: list[mp.Type] = []
        for ft in self.schema.values:
            # Direct placeholder at schema level
            if isinstance(ft, Placeholder) and ft in mapping:
                new_types.append(_make_replacement(ft))
                continue
            # Traverse field type, substitute leaves (including nested spreads)
            ft_carrier = mp.wrap(ft)
            carrier_mapping = {}
            for leaf in ft_carrier.deep_iter():
                data = leaf.fetch()
                if data in mapping:
                    repl = _make_replacement(data)
                    carrier_mapping[leaf] = mp.LeafCarrier(leaf.__type__, repl)
            if carrier_mapping:
                result = ft_carrier.subst(carrier_mapping).fetch()
                # If result is a Tuple-like with Spreads, splice them
                if isinstance(result, Tuple):
                    result = result.splice()
                new_types.append(result)
            else:
                new_types.append(ft)
        new_schema = VaryingType(self.schema.index, tuple(new_types)).splice()
        return NativeType(self.builtin_cls, new_schema)
