from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Literal

import protomorph as pm

from protobase import Consed, Inmutable

from axis import syn


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
    def non_spread_fields(self) -> tuple[Field, ...]:
        return self.prefix + self.suffix if self.spread is not None else self.fields


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
