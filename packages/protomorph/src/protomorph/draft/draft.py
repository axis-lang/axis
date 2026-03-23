# %%

from __future__ import annotations

from typing import Any, Self, NewType, Iterator, NamedTuple

from protobase import Consed

Id = NewType("Id", str)
Anchor = NewType("Anchor", str)

_RECONSTRUCT = object()


# ══════════════════════════════════════════════════════════════════
# Layer 0: Builtin — hash-consed identity
# ══════════════════════════════════════════════════════════════════


class Builtin(Consed, abstract=True): ...


# ══════════════════════════════════════════════════════════════════
# Layer 1: Type — classification, structure, and carrier factory
# ══════════════════════════════════════════════════════════════════


class Field(NamedTuple):
    offset: int
    key: Id | None
    type: Type


class Type[T](Builtin, abstract=True):

    # ── Classification ────────────────────────────────────────────

    def metatype(self) -> Type[Self]:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def carrier(self, data: T) -> Carrier[T]:
        """Create the appropriate carrier for data of this type."""
        raise NotImplementedError(
            f"carrier() not implemented for {type(self).__name__}"
        )

    # ── Structure (defaults: leaf / no children) ──────────────────

    @property
    def arity(self) -> int | None:
        return 0

    def field_at(self, offset: int) -> Field:
        raise IndexError(offset)

    def field(self, id: Id) -> Field:
        raise KeyError(id)

    def iter_fields(self) -> Iterator[Field]:
        a = self.arity
        if a is None:
            return
        for i in range(a):
            yield self.field_at(i)


# ══════════════════════════════════════════════════════════════════
# Omega — fixed point of the metatype chain
# ══════════════════════════════════════════════════════════════════


class Omega(Type["Omega"]):
    """OMEGA.metatype() is OMEGA — terminates the meta chain."""

    def metatype(self) -> Omega:
        return OMEGA

    def carrier(self, data) -> LeafCarrier:
        return LeafCarrier(self, data)


OMEGA = Omega()


class Placeholder(Type):
    """Universal stand-in — can appear as Type, as data, anywhere.

    Behaves as Any: a leaf in traversal, captured/substituted later.
    Identity comes from (context, id) via hash-consing.
    """

    context: Builtin | None
    id: str

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> LeafCarrier:
        return LeafCarrier(self, data)


def placeholder(id: str, context: Any = None) -> Placeholder:
    return Placeholder(context, id)


# ══════════════════════════════════════════════════════════════════
# Layer 2: Carrier — the traversal interface
# ══════════════════════════════════════════════════════════════════


class Carrier[T](Consed, abstract=True):
    """Cursor over typed data.

    Pairs a Type (classifier) with data (payload) and exposes both
    targeted access (attr / item) and generic structural iteration.
    Traversal algorithms operate exclusively through this API.
    """

    __type__: Type[T]
    __data__: T

    # ── Factory ───────────────────────────────────────────────────

    def child(self, meta: Type, data: Any) -> Carrier:
        """Produce a child carrier — the Type decides which carrier to use.
        Exception: if data is a Placeholder, always wrap as leaf."""
        if isinstance(data, Placeholder):
            return LeafCarrier(meta, data)
        return meta.carrier(data)

    # ── Meta navigation ───────────────────────────────────────────

    @property
    def type(self) -> Carrier[Type[T]]:
        """Carrier wrapping this value's type."""
        return NativeObjectCarrier(self.__type__.metatype(), self.__type__)

    def fetch(self) -> T:
        """Extract the raw data payload."""
        return self.__data__

    # ── Targeted access ───────────────────────────────────────────

    def attr(self, id: Id) -> Carrier:
        """Access a child by name."""
        raise NotImplementedError(f"attr() not implemented for {type(self).__name__}")

    def __getitem__(self, offset: int) -> Carrier:
        """Access a child by positional offset."""
        raise NotImplementedError(
            f"__getitem__ not implemented for {type(self).__name__}"
        )

    # ── Structural algebra ────────────────────────────────────────

    @property
    def is_leaf(self) -> bool:
        return self.__type__.arity == 0

    def __len__(self) -> int:
        a = self.__type__.arity
        if a is not None:
            return a
        raise NotImplementedError(
            f"__len__ for unbounded type: override in {type(self).__name__}"
        )

    def __iter__(self) -> Iterator[Carrier]:
        for i in range(len(self)):
            yield self[i]

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        """Rebuild this carrier with *children* replacing the current ones."""
        raise NotImplementedError(
            f"reconstruct() not implemented for {type(self).__name__}"
        )

    # ── Derived traversals ────────────────────────────────────────

    def deep_iter(self, is_leaf=None) -> Iterator[Carrier]:
        """Depth-first iteration over leaf carriers."""
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack = [self]
        while stack:
            node = stack.pop()
            if _is_leaf(node):
                yield node
            else:
                stack.extend(reversed(list(node)))

    def deep_map(self, f, is_leaf=None) -> Carrier:
        """Bottom-up map: apply *f* to leaves, reconstruct upward."""
        _is_leaf = is_leaf or (lambda c: c.is_leaf)
        stack: list = [self]
        results: list[Carrier] = []
        while stack:
            item = stack.pop()
            if item is _RECONSTRUCT:
                node, n = stack.pop()
                new_children = tuple(results[len(results) - n :])
                del results[len(results) - n :]
                results.append(node.reconstruct(new_children))
            elif _is_leaf(item):
                results.append(f(item))
            else:
                children = list(item)
                stack.append((item, len(children)))
                stack.append(_RECONSTRUCT)
                stack.extend(reversed(children))
        return results[0]

    def subst(self, mapping: dict) -> Carrier:
        """Substitute carriers according to *mapping*."""

        def _is_leaf(c):
            return c in mapping or c.is_leaf

        return self.deep_map(lambda c: mapping.get(c, c), is_leaf=_is_leaf)

    def search(self, target: Carrier) -> bool:
        """Return True if *target* appears anywhere in this structure."""
        stack = [self]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if not node.is_leaf:
                stack.extend(node)
        return False


# ══════════════════════════════════════════════════════════════════
# Layer 3: Concrete carriers
# ══════════════════════════════════════════════════════════════════


class NativeObjectCarrier[T](Carrier[T]):
    """Carrier for Builtin / native Python objects with named fields."""

    def attr(self, id: Id) -> Carrier:
        field = self.__type__.field(id)
        return self.child(field.type, getattr(self.__data__, id))

    def __getitem__(self, offset: int) -> Carrier:
        field = self.__type__.field_at(offset)
        assert (
            field.key is not None
        ), f"NativeObjectCarrier requires named fields (offset {offset})"
        return self.child(field.type, getattr(self.__data__, field.key))

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        new_data = type(self.__data__)(*(c.fetch() for c in children))
        return type(self)(self.__type__, new_data)


class LeafCarrier[T](Carrier[T]):
    """Carrier for leaf values — scalars, placeholders, etc.
    Always a leaf (arity=0), never traversed into."""

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        assert not children
        return self


class TupleCarrier(Carrier[tuple]):
    """Carrier for raw Python tuples (both uniform and varying)."""

    def __getitem__(self, offset: int) -> Carrier:
        field = self.__type__.field_at(offset)
        return self.child(field.type, self.__data__[offset])

    def attr(self, id: Id) -> Carrier:
        field = self.__type__.field(id)
        return self.child(field.type, self.__data__[field.offset])

    def __len__(self) -> int:
        a = self.__type__.arity
        return a if a is not None else len(self.__data__)

    def reconstruct(self, children: tuple[Carrier, ...]) -> Self:
        return type(self)(self.__type__, tuple(c.fetch() for c in children))


# ══════════════════════════════════════════════════════════════════
# Layer 4: Index & Tuple data structures
# ══════════════════════════════════════════════════════════════════


class Index[K](Builtin):

    keys: tuple[K, ...]

    def __len__(self) -> int:
        return len(self.keys)

    def __getitem__(self, offset: int) -> K:
        return self.keys[offset]

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys)

    def __contains__(self, id: K) -> bool:
        return id in self.keys

    def offset_of(self, id: K) -> int:
        return self.keys.index(id)

    @classmethod
    def make(cls, *keys: K) -> Index[K]:
        return cls(keys)


EMPTY_INDEX: Index = Index(())


class Spread[V](Builtin):
    """Sentinel: wraps a tuple of values to be spliced into a parent Tuple.

    Like Python's *iterable unpacking — the parent Tuple's splice() method
    flattens Spread entries into its own values sequence.
    """

    values: tuple[V, ...]


class Tuple[K, V](Builtin):

    index: Index[K]
    values: tuple[V, ...]

    def __len__(self) -> int:
        return len(self.values)

    def __getitem__(self, key: int | K) -> V:
        if isinstance(key, int):
            return self.values[key]
        return self.values[self.index.offset_of(key)]

    def __iter__(self) -> Iterator[V]:
        return iter(self.values)

    def __contains__(self, value: V) -> bool:
        return value in self.values

    def items(self) -> Iterator[tuple[K, V]]:
        for k, v in zip(self.index, self.values):
            yield k, v

    def splice(self) -> Tuple[K, V]:
        """Flatten any Spread entries in values, expanding them in-place.

        (a, Spread(x, y), b) → (a, x, y, b)
        Index keys for spread positions are dropped; surrounding keys are preserved.
        """
        has_spread = any(isinstance(v, Spread) for v in self.values)
        if not has_spread:
            return self
        new_keys: list[K] = []
        new_values: list[V] = []
        keys = self.index.keys if self.index is not EMPTY_INDEX else (None,) * len(self.values)
        for key, val in zip(keys, self.values):
            if isinstance(val, Spread):
                for sv in val.values:
                    new_values.append(sv)
                    new_keys.append(None)
            else:
                new_values.append(val)
                new_keys.append(key)
        has_keys = any(k is not None for k in new_keys)
        idx = Index(tuple(new_keys)) if has_keys else EMPTY_INDEX
        return type(self)(idx, tuple(new_values))

    @classmethod
    def make[T](cls, *args: T, **kwargs: T) -> Tuple[Id, T]:
        keys = [None] * len(args) + [Id(k) for k in kwargs]
        values = args + tuple(kwargs.values())
        has_keys = any(k is not None for k in keys)
        idx = Index(tuple(keys)) if has_keys else EMPTY_INDEX
        return cls(idx, values)


# ══════════════════════════════════════════════════════════════════
# Layer 5: Concrete types
# ══════════════════════════════════════════════════════════════════


class ScalarType(Type):
    """Leaf type for Python scalars.  arity=0 (inherited default)."""

    python_type: type

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> LeafCarrier:
        return LeafCarrier(self, data)


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

    element_type: Type[T]

    def metatype(self) -> Type:
        return OMEGA

    @property
    def arity(self) -> int | None:
        return None  # unknown until we see data

    def field_at(self, offset: int) -> Field:
        return Field(offset, None, self.element_type)

    def field(self, id: Id) -> Field:
        raise KeyError(id)  # no index at the type level

    def carrier(self, data) -> TupleCarrier:
        return TupleCarrier(self, data)


class UnionType(Type):
    """Union of types — leaf in structure, carrier dispatches at runtime."""

    variants: frozenset[Type]

    def metatype(self) -> Type:
        return OMEGA

    def carrier(self, data) -> LeafCarrier:
        return LeafCarrier(self, data)

    @classmethod
    def of(cls, *types: Type) -> Type:
        """Build a union, flattening nested unions. Returns single type if only one."""
        flat: set[Type] = set()
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

    def field_at(self, offset: int) -> Field:
        key = self.index.keys[offset] if self.index else None
        return Field(offset, key, self.values[offset])

    def field(self, id: Id) -> Field:
        if not self.index:
            raise KeyError(id)
        offset = self.index.offset_of(id)
        return Field(offset, id, self.values[offset])

    def carrier(self, data) -> TupleCarrier:
        return TupleCarrier(self, data)


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

    def field_at(self, offset: int) -> Field:
        return self.schema.field_at(offset)

    def field(self, id: Id) -> Field:
        return self.schema.field(id)

    def carrier(self, data) -> NativeObjectCarrier:
        return NativeObjectCarrier(self, data)

    def specialize(self, mapping: dict[Placeholder, Type]) -> NativeType:
        """Substitute Placeholders in field types, returning a new NativeType.

        Spread placeholders (*T) are replaced with Spread(...) sentinels
        inside the carrier subst, then splice() flattens them.
        """
        def _make_replacement(ph: Placeholder, target_type: Type) -> Any:
            """Build the replacement data for a placeholder."""
            replacement = mapping[ph]
            if ph.id.startswith("*") and isinstance(replacement, VaryingType):
                return Spread(replacement.values)
            return replacement

        new_types: list[Type] = []
        for ft in self.schema.values:
            # Direct placeholder at schema level
            if isinstance(ft, Placeholder) and ft in mapping:
                new_types.append(_make_replacement(ft, ft))
                continue
            # Traverse field type, substitute leaves (including nested spreads)
            ft_carrier = wrap(ft)
            carrier_mapping = {}
            for leaf in ft_carrier.deep_iter():
                data = leaf.fetch()
                if data in mapping:
                    repl = _make_replacement(data, leaf.__type__)
                    carrier_mapping[leaf] = LeafCarrier(leaf.__type__, repl)
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


# ══════════════════════════════════════════════════════════════════
# Layer 6: Native bridge — Python annotations → Type
# ══════════════════════════════════════════════════════════════════


def type_from_annotation(
    annotation: Any, *, template: NativeType | None = None
) -> Type:
    """Map a Python type annotation to a Type."""
    from types import UnionType as PEP604Union
    from typing import get_origin, get_args, TypeVar, TypeVarTuple, Union, Unpack

    if isinstance(annotation, Type):
        return annotation

    # Type itself → OMEGA (the classifier of types)
    if annotation is Type:
        return OMEGA

    # TypeVar → Placeholder
    if isinstance(annotation, TypeVar):
        return Placeholder(template, annotation.__name__)

    # TypeVarTuple → Placeholder (will expand to VaryingType on specialization)
    if isinstance(annotation, TypeVarTuple):
        return Placeholder(template, f"*{annotation.__name__}")

    scalar = _SCALAR_TYPES.get(annotation)
    if scalar is not None:
        return scalar

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Union / X | Y
    if origin is Union or isinstance(annotation, PEP604Union):
        return UnionType.of(*(type_from_annotation(a, template=template) for a in args))

    # Unpack[T] (from tuple[*T]) → delegate to the TypeVarTuple inside
    if origin is Unpack and args:
        return type_from_annotation(args[0], template=template)

    # tuple[T, ...] → UniformType
    if origin is tuple and len(args) == 2 and args[1] is Ellipsis:
        return UniformType(type_from_annotation(args[0], template=template))

    # tuple[*T] → Placeholder (single Unpack arg)
    # tuple[A, B, C] → VaryingType
    if origin is tuple and args:
        converted = tuple(type_from_annotation(a, template=template) for a in args)
        # If single element and it's a spread placeholder (*T), return it directly
        if len(converted) == 1 and isinstance(converted[0], Placeholder) and converted[0].id.startswith("*"):
            return converted[0]
        return VaryingType.make(*converted)

    # Parameterized Builtin: B[int, str, float]
    if isinstance(origin, type) and issubclass(origin, Builtin):
        base = native_type(origin, template=template)
        param_types = tuple(type_from_annotation(a, template=template) for a in args)
        # Build mapping from class type params to concrete types
        cls_params = getattr(origin, "__type_params__", ())
        mapping: dict[Placeholder, Type] = {}
        for param, concrete in zip(cls_params, param_types):
            if isinstance(param, TypeVarTuple):
                # Spread: *T → VaryingType of the remaining args
                mapping[Placeholder(template, f"*{param.__name__}")] = VaryingType.make(*param_types[len(mapping):])
                break
            else:
                mapping[Placeholder(template, param.__name__)] = concrete
        return base.specialize(mapping)

    if isinstance(annotation, type) and issubclass(annotation, Builtin):
        return native_type(annotation, template=template)

    return OMEGA  # fallback for unresolvable annotations


def native_type(
    cls: type[Builtin], *, template: NativeType | None = None
) -> NativeType:
    """Build a NativeType with a reflected schema from class annotations."""
    from protobase import attr_info_of

    attrs = attr_info_of(cls)
    if not attrs:
        return NativeType(cls, VaryingType.make())

    # Use a temporary NativeType as context for Placeholders,
    # but we need the schema first → two-pass: build with `template` context,
    # then construct. Placeholders get context=template (the enclosing NativeType
    # if nested) or context=None for top-level.
    names = list(attrs.keys())
    types = tuple(
        type_from_annotation(info.type, template=template)
        for info in attrs.values()
    )
    schema = VaryingType.make(**{n: t for n, t in zip(names, types)})
    return NativeType(cls, schema)


def wrap(obj: Builtin) -> NativeObjectCarrier:
    """Wrap a Builtin instance in a carrier with its reflected type."""
    return NativeObjectCarrier(native_type(type(obj)), obj)


# ══════════════════════════════════════════════════════════════════
# Example: mapping Python's built-in tuple type to a core Tuple type
# ══════════════════════════════════════════════════════════════════


if __name__ == "__main__":

    print(VaryingType.make(INT_TYPE, STR_TYPE, FLOAT_TYPE))

    class A[T](Builtin):
        elements: tuple[T, ...]
        # other : Tuple[Id, T]  # TODO: needs Tuple annotation support

    class B[*T](Builtin):
        elements: tuple[int, *T, float]

    # ── Generic NativeType: A[T] ───────────────────────────────

    A_type = native_type(A)
    print("\n=== NativeType(A) ===")
    print("A_type:", A_type)
    print("arity:", A_type.arity)

    for i in range(A_type.arity):
        f = A_type.field_at(i)
        print(f"  field[{i}]: key={f.key}, type={f.type}")

    # Specialize A[T] → A[int]
    T_ph = placeholder("T")
    A_int = A_type.specialize({T_ph: INT_TYPE})
    print("\n=== A specialized to int ===")
    print("A_int:", A_int)
    for i in range(A_int.arity):
        f = A_int.field_at(i)
        print(f"  field[{i}]: key={f.key}, type={f.type}")

    # ── Generic NativeType: B[*T] ─────────────────────────────

    B_type = native_type(B)
    print("\n=== NativeType(B) ===")
    print("B_type:", B_type)
    print("arity:", B_type.arity)

    for i in range(B_type.arity):
        f = B_type.field_at(i)
        print(f"  field[{i}]: key={f.key}, type={f.type}")

    # Specialize B[*T] → B[int, str, float]
    T_star = placeholder("*T")
    B_concrete = B_type.specialize({T_star: VaryingType.make(INT_TYPE, STR_TYPE, FLOAT_TYPE)})
    print("\n=== B specialized to (int, str, float) ===")
    print("B_concrete:", B_concrete)
    print("arity:", B_concrete.arity)
    for i in range(B_concrete.arity):
        f = B_concrete.field_at(i)
        print(f"  field[{i}]: key={f.key}, type={f.type}")

    # ── Substitution example ─────────────────────────────────────

    T = placeholder("T")

    # VaryingType(int, <T>, str) — a heterogeneous tuple with a hole
    vt = VaryingType.make(INT_TYPE, T, z=STR_TYPE)
    print("original:", vt)

    # Wrap in a Carrier for type-level traversal
    vt_carrier = wrap(vt)
    print("carrier:", vt_carrier)
    print("is_leaf:", vt_carrier.is_leaf)

    # NativeType reflects Tuple's own fields: index, values
    # children[0] = index (leaf), children[1] = values (TupleCarrier)
    children = list(vt_carrier)
    print("top children:", children)

    values_carrier = vt_carrier[1]  # the 'values' tuple
    print("values carrier:", values_carrier)
    print("values elements:", list(values_carrier))

    # values[1] is the placeholder T, wrapped as a leaf
    ph_carrier = values_carrier[1]
    print("placeholder leaf:", ph_carrier, "data:", ph_carrier.fetch())

    # Find it via deep_iter too
    leaves = list(vt_carrier.deep_iter())
    print("all leaves:", leaves)
    print("placeholder in leaves:", ph_carrier in leaves)

    # Substitute: replace the leaf carrying T with one carrying FLOAT_TYPE
    target = ph_carrier
    replacement = LeafCarrier(ph_carrier.__type__, FLOAT_TYPE)
    result_carrier = vt_carrier.subst({target: replacement})
    result = result_carrier.fetch()
    print("after subst:", result)

    # Verify: should be VaryingType(int, float, str)
    expected = VaryingType.make(INT_TYPE, FLOAT_TYPE, z=STR_TYPE)
    print("matches expected:", result == expected)
