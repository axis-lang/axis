from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, cast, Literal

import protomorph as pm

from protobase import Consed, Inmutable, frozendict

from axis import syn, log


type LoweredBoundResult = pm.Result[log.Report, pm.Datum]


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
        match_expr: LoweredBoundResult | None = None
        default: LoweredBoundResult | None = None

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


class BindingIR(Consed):
    bindings: LoweredBindingStruct
    admission: pm.MatchCaseSummary

    @property
    def pattern(self) -> pm.Carrier:
        return self.admission.pattern


def build_binding_ir(bindings: LoweredBindingStruct) -> BindingIR:
    if bindings.spread is not None or bindings.open_tail:
        raise ValueError("BindingIR does not support spread/open-tail bindings yet")

    shape = pm.MatchShapeSummary(
        min_arity=_min_arity(bindings),
        max_arity=_max_arity(bindings),
        required_keys=_required_keys(bindings),
        allowed_keys=_allowed_keys(bindings),
        open_tail=bindings.open_tail,
    )

    return BindingIR(
        bindings=bindings,
        admission=pm.MatchCaseSummary(
            pattern=_binding_pattern(bindings),
            shape=shape,
            prefix_descriptors=_prefix_descriptors(bindings),
            suffix_descriptors=_suffix_descriptors(bindings),
            required_nominal_descriptors=_required_nominal_descriptors(bindings),
        ),
    )


def _min_arity(bindings: LoweredBindingStruct) -> int:
    return sum(1 for field in bindings.fields if field.is_positional and field.is_required)


def _max_arity(bindings: LoweredBindingStruct) -> int | None:
    if bindings.is_variadic:
        return None
    return sum(1 for field in bindings.fields if field.is_positional)


def _required_keys(bindings: LoweredBindingStruct) -> frozenset[pm.Id]:
    return frozenset(
        cast(pm.Id, field.slot_key)
        for field in bindings.fields
        if field.is_nominal and field.is_required and field.slot_key is not None
    )


def _allowed_keys(bindings: LoweredBindingStruct) -> frozenset[pm.Id] | None:
    if bindings.is_variadic:
        return None
    return frozenset(
        cast(pm.Id, field.slot_key)
        for field in bindings.fields
        if field.is_nominal and field.slot_key is not None
    )


def _descriptor_for(field: LoweredBindingStruct.Field) -> pm.Type | None:
    from axis import sem

    if field.binder is not None:
        return None
    return sem.bound_as_type(_bound_carrier(field.match_expr, origin=field.origin))


def _prefix_descriptors(bindings: LoweredBindingStruct) -> tuple[pm.Type | None, ...]:
    descriptors: list[pm.Type | None] = []
    for field in bindings.prefix:
        if not field.is_positional or not field.is_required:
            break
        descriptors.append(_descriptor_for(field))
    return tuple(descriptors)


def _suffix_descriptors(bindings: LoweredBindingStruct) -> tuple[pm.Type | None, ...]:
    descriptors: list[pm.Type | None] = []
    for field in reversed(bindings.suffix):
        if not field.is_positional or not field.is_required:
            break
        descriptors.append(_descriptor_for(field))
    return tuple(reversed(descriptors))


def _required_nominal_descriptors(
    bindings: LoweredBindingStruct,
) -> frozendict[pm.Id, pm.Type | None]:
    return frozendict(
        {
            cast(pm.Id, field.slot_key): _descriptor_for(field)
            for field in bindings.fields
            if field.is_nominal and field.is_required and field.slot_key is not None
        }
    )


def _binding_value(field: LoweredBindingStruct.Field) -> pm.Carrier:
    if field.binder is not None:
        return pm.wrap(field.binder)
    if field.match_expr is not None:
        value = _bound_carrier(field.match_expr, origin=field.origin)
        assert value is not None
        return value
    if field.is_placeholder:
        return pm.wrap(pm.placeholder("_"))
    raise ValueError(f"Binding field {field.origin!r} cannot be lowered to a matching value")


def _bound_carrier(
    result: LoweredBoundResult | None,
    *,
    origin: syn.Node,
) -> pm.Carrier | None:
    if result is None:
        return None
    if result.is_err:
        report = result.unwrap_err().fetch()
        if isinstance(report, log.Report):
            report.throw()
        raise TypeError(f"Binding field {origin!r} failed with non-report error: {report!r}")
    return result.unwrap()


def _binding_pattern(bindings: LoweredBindingStruct) -> pm.Carrier:
    positional: list[pm.Carrier] = []
    nominal: dict[str, pm.Carrier] = {}
    for field in bindings.fields:
        if field.is_optional:
            continue
        value = _binding_value(field)
        if field.is_positional:
            positional.append(value)
        else:
            assert field.slot_key is not None
            nominal[field.slot_key] = value
    return pm.VaryingType.new(*positional, **nominal)


def lower_binding_struct(
    bindings: BindingStruct,
    scope: syn.ScopeLike,
    *,
    binder_for: Callable[[BindingStruct.Field], pm.Var | None] | None = None,
) -> LoweredBindingStruct:
    import axis.expr.lowering as expr_bounds

    binder_for = (lambda field: None) if binder_for is None else binder_for

    def lower_field(field: BindingStruct.Field) -> LoweredBindingStruct.Field:
        bound = expr_bounds.build_bound(field.bound_expr, scope)
        return LoweredBindingStruct.Field(
            decl=field,
            binder=binder_for(field),
            match_expr=_carrier_result(bound),
            default=_carrier_result(expr_bounds.build_default(field.default_expr, scope)),
        )

    return LoweredBindingStruct(
        prefix=tuple(lower_field(field) for field in bindings.prefix),
        spread=None if bindings.spread is None else lower_field(bindings.spread),
        suffix=tuple(lower_field(field) for field in bindings.suffix),
        open_tail=bindings.open_tail,
    )


def _carrier_result(result: pm.Result[log.Report, Any] | None) -> LoweredBoundResult | None:
    if result is None:
        return None
    if result.is_err:
        return cast(LoweredBoundResult, result)
    return pm.Result.ok(result.unwrap())
