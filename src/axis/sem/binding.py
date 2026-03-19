from __future__ import annotations

from collections.abc import Callable, Iterator
from itertools import combinations
from typing import Literal

import protomorph as pm

from protobase import Consed, Inmutable

from axis import syn


type BindingShape = tuple[pm.Struct.Shape[str | None], bool]


class BindingStruct(Consed):
    class Field(Inmutable):
        kind: Literal["binding", "placeholder", "spread"]
        origin: syn.Node
        key_expr: syn.Expr
        binder_name: str | None = None
        slot_key: str | None = None
        bound_expr: syn.Expr | None = None
        default_expr: syn.Expr | None = None

        @property
        def is_spread(self) -> bool:
            return self.kind == "spread"

        @property
        def is_variadic(self) -> bool:
            return self.is_spread

        @property
        def is_placeholder(self) -> bool:
            return self.kind == "placeholder"

        @property
        def is_nameable(self) -> bool:
            return self.binder_name is not None

        @property
        def is_positional(self) -> bool:
            return self.slot_key is None

        @property
        def is_nominal(self) -> bool:
            return self.slot_key is not None

        @property
        def is_optional(self) -> bool:
            return self.default_expr is not None

        @property
        def is_required(self) -> bool:
            return not self.is_optional

    prefix: tuple[Field, ...] = ()
    spread: Field | None = None
    suffix: tuple[Field, ...] = ()
    open_tail: bool = False

    def __iter__(self) -> Iterator[Field]:
        return iter(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    def __getitem__(self, index: int | slice) -> Field | tuple[Field, ...]:
        return self.fields[index]

    @property
    def fields(self) -> tuple[Field, ...]:
        return self.prefix + (() if self.spread is None else (self.spread,)) + self.suffix

    @property
    def values(self) -> tuple[Field, ...]:
        return self.fields

    @property
    def index(self) -> pm.Struct.Index[str | None]:
        return pm.Struct.Index(tuple(field.slot_key for field in self.fields))

    @property
    def shape(self) -> BindingShape:
        return self.index.shape, self.open_tail

    @property
    def positional_fields(self) -> tuple[Field, ...]:
        return tuple(field for field in self.fields if field.is_positional)

    @property
    def nominal_fields(self) -> tuple[Field, ...]:
        return tuple(field for field in self.fields if field.is_nominal)

    @property
    def nameable_fields(self) -> tuple[Field, ...]:
        return tuple(field for field in self.fields if field.is_nameable)

    @property
    def required_fields(self) -> tuple[Field, ...]:
        return tuple(field for field in self.fields if field.is_required)

    @property
    def optional_fields(self) -> tuple[Field, ...]:
        return tuple(field for field in self.fields if field.is_optional)

    @property
    def is_variadic(self) -> bool:
        return self.spread is not None or self.open_tail

    @property
    def variadic_offset(self) -> int | None:
        return None if self.spread is None else len(self.prefix)

    @property
    def field_keys(self) -> tuple[str | None, ...]:
        return tuple(field.slot_key for field in self.non_spread_fields)

    @property
    def non_spread_fields(self) -> tuple[Field, ...]:
        return self.prefix + self.suffix if self.spread is not None else self.fields

    @property
    def variadic_signature(self) -> pm.VariadicSignature | None:
        if not self.is_variadic:
            return None
        return pm.VariadicSignature(
            prefix_len=len(self.prefix),
            suffix_len=len(self.suffix),
            prefix_index=pm.Struct.Index(tuple(field.slot_key for field in self.prefix)),
            suffix_index=pm.Struct.Index(tuple(field.slot_key for field in self.suffix)),
        )

    def field_entries(self) -> tuple[tuple[str | None, Field], ...]:
        return tuple((field.slot_key, field) for field in self.non_spread_fields)

    @property
    def routing_variants(self) -> frozenset[BindingStruct]:
        return frozenset(_binding_struct_variants(self))

    @property
    def closed_shapes(self) -> frozenset[BindingShape]:
        return frozenset(variant.shape for variant in self.routing_variants if not variant.is_variadic)

    @property
    def variadic_signatures(self) -> frozenset[pm.VariadicSignature]:
        return frozenset(
            signature
            for variant in self.routing_variants
            if (signature := variant.variadic_signature) is not None
        )


Binding = BindingStruct.Field


class LoweredBindingStruct(Consed):
    class Field(Inmutable):
        decl: BindingStruct.Field
        binder: pm.Var | None = None
        match_expr: pm.Val = pm.ANY
        default: pm.Val | None = None

        @property
        def binder_name(self) -> str | None:
            return self.decl.binder_name

        @property
        def slot_key(self) -> str | None:
            return self.decl.slot_key

        @property
        def origin(self) -> syn.Node:
            return self.decl.origin

        @property
        def key_expr(self) -> syn.Expr:
            return self.decl.key_expr

        @property
        def is_spread(self) -> bool:
            return self.decl.is_spread

        @property
        def is_variadic(self) -> bool:
            return self.is_spread

        @property
        def is_placeholder(self) -> bool:
            return self.decl.is_placeholder

        @property
        def is_nameable(self) -> bool:
            return self.decl.is_nameable

        @property
        def is_positional(self) -> bool:
            return self.decl.is_positional

        @property
        def is_nominal(self) -> bool:
            return self.decl.is_nominal

        @property
        def is_optional(self) -> bool:
            return self.default is not None

        @property
        def is_required(self) -> bool:
            return not self.is_optional

    prefix: tuple[Field, ...] = ()
    spread: Field | None = None
    suffix: tuple[Field, ...] = ()
    open_tail: bool = False

    def __iter__(self) -> Iterator[Field]:
        return iter(self.fields)

    def __len__(self) -> int:
        return len(self.fields)

    def __getitem__(self, index: int | slice) -> Field | tuple[Field, ...]:
        return self.fields[index]

    @property
    def fields(self) -> tuple[Field, ...]:
        return self.prefix + (() if self.spread is None else (self.spread,)) + self.suffix

    @property
    def values(self) -> tuple[Field, ...]:
        return self.fields

    @property
    def is_variadic(self) -> bool:
        return self.spread is not None or self.open_tail

    @property
    def variadic_offset(self) -> int | None:
        return None if self.spread is None else len(self.prefix)

    @property
    def variadic_signature(self) -> pm.VariadicSignature | None:
        if not self.is_variadic:
            return None
        return pm.VariadicSignature(
            prefix_len=len(self.prefix),
            suffix_len=len(self.suffix),
            prefix_index=pm.Struct.Index(tuple(field.slot_key for field in self.prefix)),
            suffix_index=pm.Struct.Index(tuple(field.slot_key for field in self.suffix)),
        )

    @property
    def non_spread_fields(self) -> tuple[Field, ...]:
        return self.prefix + self.suffix if self.spread is not None else self.fields

    def field_entries(self) -> tuple[tuple[str | None, Field], ...]:
        return tuple((field.slot_key, field) for field in self.non_spread_fields)


LoweredBinding = LoweredBindingStruct.Field


def lower_binding_struct(
    bindings: BindingStruct,
    scope: syn.ScopeLike,
    *,
    binder_for: Callable[[BindingStruct.Field], pm.Var | None] | None = None,
) -> LoweredBindingStruct:
    from axis.expr import bound_support as expr_bounds

    binder_for = (lambda field: None) if binder_for is None else binder_for

    def lower_field(field: BindingStruct.Field) -> LoweredBindingStruct.Field:
        bound = expr_bounds.build_bound(field.bound_expr, scope)
        return LoweredBindingStruct.Field(
            decl=field,
            binder=binder_for(field),
            match_expr=pm.ANY if bound is None else bound,
            default=expr_bounds.build_default(field.default_expr, scope),
        )

    return LoweredBindingStruct(
        prefix=tuple(lower_field(field) for field in bindings.prefix),
        spread=None if bindings.spread is None else lower_field(bindings.spread),
        suffix=tuple(lower_field(field) for field in bindings.suffix),
        open_tail=bindings.open_tail,
    )


def binding_schema(bindings: LoweredBindingStruct) -> pm.StructSchema:
    fields = pm.Struct.from_iter(
        (field.slot_key, pm.StructSchema.Field(match_expr=field.match_expr, default=field.default))
        for field in bindings.non_spread_fields
    )
    middle = pm.ANY if bindings.spread is None else bindings.spread.match_expr
    return pm.StructSchema(
        fields=fields,
        varsign=bindings.variadic_signature,
        middle=middle,
    )


def bindings_for_shape(
    bindings: BindingStruct,
    spec_ref: pm.Spec,
) -> pm.Struct[str, pm.Val] | None:
    if bindings.is_variadic:
        return None

    spec_args = spec_ref.args
    declared = bindings.fields
    if spec_args is None:
        return pm.Struct.Empty if not declared else None

    positional_args = [
        value for key, value in zip(spec_args.index.keys, spec_args.values) if key is None
    ]
    nominal_args = {
        key: value for key, value in zip(spec_args.index.keys, spec_args.values) if key is not None
    }
    matched_nominal_keys: set[str] = set()
    positional_offset = 0

    entries: list[tuple[str, pm.Val]] = []
    for binding in declared:
        value: pm.Val | None = None
        for key in binding_route_keys(binding):
            if key is None or key in matched_nominal_keys:
                continue
            candidate = nominal_args.get(key)
            if candidate is None:
                continue
            matched_nominal_keys.add(key)
            value = candidate
            break

        if value is None:
            if binding.is_positional and positional_offset < len(positional_args):
                value = positional_args[positional_offset]
                positional_offset += 1
            elif binding.default_expr is not None:
                continue
            else:
                return None

        if binding.binder_name is None:
            continue
        entries.append((binding.binder_name, value))

    if positional_offset != len(positional_args):
        return None
    if matched_nominal_keys != nominal_args.keys():
        return None
    return pm.Struct.from_iter(entries)


def binding_route_keys(binding: BindingStruct.Field | LoweredBindingStruct.Field) -> tuple[str | None, ...]:
    keys: list[str | None] = []
    if binding.slot_key is not None:
        keys.append(binding.slot_key)
    if binding.binder_name is not None:
        keys.append(binding.binder_name)
    if binding.slot_key is None and binding.binder_name is None:
        keys.append(None)
    return tuple(dict.fromkeys(keys))


def _binding_struct_variants(bindings: BindingStruct) -> tuple[BindingStruct, ...]:
    values = bindings.fields
    if not values:
        return (bindings,)

    positional_offsets = tuple(
        offset for offset, field in enumerate(values) if not field.is_variadic and field.slot_key is None
    )
    named_optional_offsets = tuple(
        offset
        for offset, field in enumerate(values)
        if not field.is_variadic and field.slot_key is not None and field.default_expr is not None
    )

    valid_positional_counts = tuple(
        count
        for count in range(len(positional_offsets) + 1)
        if all(values[offset].default_expr is not None for offset in positional_offsets[count:])
    )

    variants: set[BindingStruct] = set()
    for positional_count in valid_positional_counts:
        kept_positionals = frozenset(positional_offsets[:positional_count])
        for optional_count in range(len(named_optional_offsets) + 1):
            for optional_subset in combinations(named_optional_offsets, optional_count):
                kept_optional_nominals = frozenset(optional_subset)
                kept_values = tuple(
                    field
                    for offset, field in enumerate(values)
                    if _include_binding(
                        field,
                        offset=offset,
                        kept_positionals=kept_positionals,
                        kept_optional_nominals=kept_optional_nominals,
                    )
                )
                prefix, spread, suffix = _partition_fields(kept_values)
                variants.add(
                    BindingStruct(
                        prefix=prefix,
                        spread=spread,
                        suffix=suffix,
                        open_tail=bindings.open_tail,
                    )
                )

    return tuple(variants or (bindings,))


def _partition_fields(
    fields: tuple[BindingStruct.Field, ...],
) -> tuple[tuple[BindingStruct.Field, ...], BindingStruct.Field | None, tuple[BindingStruct.Field, ...]]:
    spread_offset = next((i for i, field in enumerate(fields) if field.is_spread), None)
    if spread_offset is None:
        return fields, None, ()
    return fields[:spread_offset], fields[spread_offset], fields[spread_offset + 1 :]


def _include_binding(
    field: BindingStruct.Field,
    *,
    offset: int,
    kept_positionals: frozenset[int],
    kept_optional_nominals: frozenset[int],
) -> bool:
    if field.is_variadic:
        return True
    if field.slot_key is None:
        return offset in kept_positionals
    if field.default_expr is None:
        return True
    return offset in kept_optional_nominals
