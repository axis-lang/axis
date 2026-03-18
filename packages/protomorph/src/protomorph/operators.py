from __future__ import annotations

from collections.abc import Iterable
from typing import cast

from protobase import Consed, _, mutate

import protomorph as pm

__all__ = [
    "Operator",
    "OperatorType",
    "Op",
    "ViewAs",
    "Satisfy",
    "VariadicStruct",
    "QualifierSuffix",
    "op",
    "view_as",
    "satisfy",
    "variadic_struct",
    "qualifier_suffix",
]


class Operator(pm.Builtin, abstract=True):
    @property
    def ref_spec(self) -> pm.Spec:
        return pm.spec_ref(type(self)._anchor_path(), self._metaspec())

    def _metaspec(self) -> pm.Const:
        return pm.EmptyStruct

    def normalize(self, bridge: pm.SemanticBridge) -> pm.Val:
        return pm.op(self)

    def satisfy(
        self,
        rhs: pm.Val,
        state: pm.MatchState,
        bridge: pm.SemanticBridge,
    ) -> Iterable[pm.MatchState]:
        _ = (rhs, state, bridge)
        return ()

    def intersect(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> pm.Val | None:
        if isinstance(right, pm.Op) and right.__data__ == self:
            return pm.op(self)
        _ = bridge
        return None

    def subsumes(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> bool:
        _ = bridge
        return isinstance(right, pm.Op) and right.__data__ == self

    def discriminants(self, bridge: pm.SemanticBridge) -> tuple[pm.Discriminant, ...]:
        _ = bridge
        return (pm.Discriminant(key="operator", value=self.ref_spec.path),)


class OperatorType(pm.Type):
    ANCHOR = "std.types.Operator"

    ref_spec: pm.Spec = _

    def _wrap(self, data: pm.Data) -> pm.Val:
        if not isinstance(data, Operator):
            raise TypeError(
                f"{type(self).__name__}.wrap expected Operator data, got {type(data).__name__}"
            )
        return Op(self, data)


class Op(pm.Placeholder, Consed):
    __type__: OperatorType = _
    __data__: Operator = _


class ViewAs(Operator):
    ANCHOR = "std.operators.ViewAs"

    trait: pm.Spec
    pattern: pm.Val

    def _metaspec(self) -> pm.Const:
        return pm.spec(trait=self.trait, P=self.pattern.__type__)

    def normalize(self, bridge: pm.SemanticBridge) -> pm.Val:
        pattern = pm.normalize(self.pattern, bridge=bridge)
        if pattern == self.pattern:
            return pm.op(self)
        return pm.op(mutate(self, pattern=pattern))

    def satisfy(
        self,
        rhs: pm.Val,
        state: pm.MatchState,
        bridge: pm.SemanticBridge,
    ) -> Iterable[pm.MatchState]:
        subject = _as_bridge_subject(rhs)
        for candidate in bridge.view(self.trait, subject):
            yield from pm.match(self.pattern, candidate, state=state, bridge=bridge)

    def intersect(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> pm.Val | None:
        if isinstance(right, pm.Op) and isinstance(right.__data__, ViewAs):
            other = right.__data__
            if other.trait != self.trait:
                return None
            pattern = pm.intersect(self.pattern, other.pattern, bridge=bridge)
            return None if pattern is None else pm.view_as(self.trait, pattern)

        if isinstance(right, pm.Placeholder):
            return None

        initial = pm.MatchState()
        for candidate in bridge.view(self.trait, right):
            if any(pm.match(self.pattern, candidate, state=initial, bridge=bridge)):
                return right
        return None

    def subsumes(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> bool:
        if isinstance(right, pm.Op) and isinstance(right.__data__, ViewAs):
            other = right.__data__
            return other.trait == self.trait and pm.subsumes(
                self.pattern,
                other.pattern,
                bridge=bridge,
            )

        if isinstance(right, pm.Placeholder):
            return False

        return self.intersect(right, bridge=bridge) == right

    def discriminants(self, bridge: pm.SemanticBridge) -> tuple[pm.Discriminant, ...]:
        _ = bridge
        return (
            pm.Discriminant(key="operator", value="ViewAs"),
            pm.Discriminant(key="trait", value=self.trait.path),
            pm.Discriminant(key="pattern_type", value=repr(self.pattern.__type__)),
        )


class Satisfy(Operator):
    ANCHOR = "std.operators.Satisfy"

    goal: pm.Spec

    def _metaspec(self) -> pm.Const:
        meta_args = self.goal.__type__.meta_args
        return pm.spec(
            head=self.goal.anchor,
            shape=pm.literal(repr(meta_args.meta_attrs.index)),
        )

    def satisfy(
        self,
        rhs: pm.Val,
        state: pm.MatchState,
        bridge: pm.SemanticBridge,
    ) -> Iterable[pm.MatchState]:
        subject = _as_bridge_subject(rhs)
        goal = self.goal.subst(
            lambda value: subject if value == pm.THIS else state.bindings.get(value)
        )
        if not isinstance(goal, pm.Spec):
            return ()
        return bridge.solve(goal, state)

    def intersect(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> pm.Val | None:
        if isinstance(right, pm.Op) and isinstance(right.__data__, Satisfy):
            return pm.op(self) if right.__data__.goal == self.goal else None

        if isinstance(right, pm.Placeholder):
            return None

        goal = self.goal.subst(lambda value: right if value == pm.THIS else None)
        if not isinstance(goal, pm.Spec):
            return None
        initial = pm.MatchState()
        return right if any(bridge.solve(goal, initial)) else None

    def subsumes(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> bool:
        if isinstance(right, pm.Op) and isinstance(right.__data__, Satisfy):
            return right.__data__.goal == self.goal
        if isinstance(right, pm.Placeholder):
            return False
        return self.intersect(right, bridge=bridge) == right

    def discriminants(self, bridge: pm.SemanticBridge) -> tuple[pm.Discriminant, ...]:
        _ = bridge
        return (
            pm.Discriminant(key="operator", value="Satisfy"),
            pm.Discriminant(key="head", value=self.goal.anchor.path),
            pm.Discriminant(key="shape", value=repr(self.goal.struct_shape)),
        )


class VariadicStruct(Operator):
    ANCHOR = "std.operators.VariadicStruct"

    prefix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty
    middle: pm.Val = pm.ANY
    suffix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty

    def _metaspec(self) -> pm.Const:
        return pm.spec(
            prefix=pm.val(self.prefix.index),
            middle=self.middle.__type__,
            suffix=pm.val(self.suffix.index),
        )

    def normalize(self, bridge: pm.SemanticBridge) -> pm.Val:
        prefix = _normalize_control_struct(self.prefix, bridge=bridge)
        middle = pm.normalize(self.middle, bridge=bridge)
        suffix = _normalize_control_struct(self.suffix, bridge=bridge)
        if prefix == self.prefix and middle == self.middle and suffix == self.suffix:
            return pm.op(self)
        return pm.op(mutate(self, prefix=prefix, middle=middle, suffix=suffix))

    def satisfy(
        self,
        rhs: pm.Val,
        state: pm.MatchState,
        bridge: pm.SemanticBridge,
    ) -> Iterable[pm.MatchState]:
        rhs_struct = _as_struct(rhs)
        if rhs_struct is None:
            return ()

        prefix_len = len(self.prefix.values)
        suffix_len = len(self.suffix.values)
        if len(rhs_struct.values) < prefix_len + suffix_len:
            return ()

        head_keys = rhs_struct.index.keys[:prefix_len]
        head_values = rhs_struct.values[:prefix_len]
        tail_start = len(rhs_struct.values) - suffix_len
        middle_keys = rhs_struct.index.keys[prefix_len:tail_start]
        middle_values = rhs_struct.values[prefix_len:tail_start]
        tail_keys = rhs_struct.index.keys[tail_start:]
        tail_values = rhs_struct.values[tail_start:]

        states: tuple[pm.MatchState, ...] = (state,)
        if prefix_len:
            states = tuple(
                next_state
                for current in states
                for next_state in pm.match(
                    _struct_const(self.prefix),
                    _struct_const(pm.Struct.from_keys(head_keys, head_values)),
                    state=current,
                    bridge=bridge,
                )
            )
            if not states:
                return ()

        states = tuple(
            next_state
            for current in states
            for next_state in pm.match(
                self.middle,
                _struct_const(pm.Struct.from_keys(middle_keys, middle_values)),
                state=current,
                bridge=bridge,
            )
        )
        if not states:
            return ()

        if suffix_len:
            states = tuple(
                next_state
                for current in states
                for next_state in pm.match(
                    _struct_const(self.suffix),
                    _struct_const(pm.Struct.from_keys(tail_keys, tail_values)),
                    state=current,
                    bridge=bridge,
                )
            )
        return states

    def intersect(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> pm.Val | None:
        if isinstance(right, pm.Op) and isinstance(right.__data__, VariadicStruct):
            other = right.__data__
            if self.prefix.index.keys != other.prefix.index.keys:
                return None
            if self.suffix.index.keys != other.suffix.index.keys:
                return None
            prefix = _intersect_control_struct(self.prefix, other.prefix, bridge=bridge)
            suffix = _intersect_control_struct(self.suffix, other.suffix, bridge=bridge)
            middle = pm.intersect(self.middle, other.middle, bridge=bridge)
            if prefix is None or suffix is None or middle is None:
                return None
            return pm.variadic_struct(prefix=prefix, middle=middle, suffix=suffix)

        if isinstance(right, pm.Placeholder):
            return None

        initial = pm.MatchState()
        return right if any(self.satisfy(right, initial, bridge)) else None

    def subsumes(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> bool:
        if isinstance(right, pm.Op) and isinstance(right.__data__, VariadicStruct):
            other = right.__data__
            return (
                self.prefix.index.keys == other.prefix.index.keys
                and self.suffix.index.keys == other.suffix.index.keys
                and _subsumes_control_struct(self.prefix, other.prefix, bridge=bridge)
                and pm.subsumes(self.middle, other.middle, bridge=bridge)
                and _subsumes_control_struct(self.suffix, other.suffix, bridge=bridge)
            )
        if isinstance(right, pm.Placeholder):
            return False
        return self.intersect(right, bridge=bridge) == right

    def discriminants(self, bridge: pm.SemanticBridge) -> tuple[pm.Discriminant, ...]:
        _ = bridge
        return (
            pm.Discriminant(key="operator", value="VariadicStruct"),
            pm.Discriminant(key="prefix_len", value=self.prefix.arity),
            pm.Discriminant(key="suffix_len", value=self.suffix.arity),
            pm.Discriminant(key="prefix_index", value=repr(self.prefix.index)),
            pm.Discriminant(key="suffix_index", value=repr(self.suffix.index)),
        )


class QualifierSuffix(Operator):
    ANCHOR = "std.operators.QualifierSuffix"

    suffix: pm.Val
    skip_if: pm.Val = pm.ANY
    include_terminal: bool = True

    def _metaspec(self) -> pm.Const:
        return pm.spec(
            suffix=_pattern_type(self.suffix),
            skip=_pattern_type(self.skip_if),
            terminal=pm.literal(self.include_terminal),
        )

    def normalize(self, bridge: pm.SemanticBridge) -> pm.Val:
        suffix = _normalize_pattern(self.suffix, bridge=bridge)
        skip_if = _normalize_pattern(self.skip_if, bridge=bridge)
        if suffix == self.suffix and skip_if == self.skip_if:
            return pm.op(self)
        return pm.op(mutate(self, suffix=suffix, skip_if=skip_if))

    def satisfy(
        self,
        rhs: pm.Val,
        state: pm.MatchState,
        bridge: pm.SemanticBridge,
    ) -> Iterable[pm.MatchState]:
        states: list[pm.MatchState] = []
        for candidate, candidate_state in _qualifier_suffix_candidates(
            rhs,
            state=state,
            skip_if=cast(pm.Val, self.skip_if),
            include_terminal=self.include_terminal,
            bridge=bridge,
        ):
            states.extend(
                pm.match(
                    cast(pm.Val, self.suffix),
                    cast(pm.Val, candidate),
                    state=candidate_state,
                    bridge=bridge,
                )
            )
        return tuple(states)

    def intersect(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> pm.Val | None:
        if isinstance(right, pm.Op) and isinstance(right.__data__, QualifierSuffix):
            other = right.__data__
            if self.skip_if != other.skip_if or self.include_terminal != other.include_terminal:
                return None
            suffix = _intersect_pattern(self.suffix, other.suffix, bridge=bridge)
            return None if suffix is None else pm.qualifier_suffix(
                cast(pm.Val, suffix),
                skip_if=self.skip_if,
                include_terminal=self.include_terminal,
            )

        if isinstance(right, pm.Placeholder):
            return None

        initial = pm.MatchState()
        return right if any(self.satisfy(right, initial, bridge)) else None

    def subsumes(
        self,
        right: pm.Val,
        bridge: pm.SemanticBridge,
    ) -> bool:
        if isinstance(right, pm.Op) and isinstance(right.__data__, QualifierSuffix):
            other = right.__data__
            return (
                self.skip_if == other.skip_if
                and self.include_terminal == other.include_terminal
                and _subsumes_pattern(self.suffix, other.suffix, bridge=bridge)
            )
        if isinstance(right, pm.Placeholder):
            return False
        return self.intersect(right, bridge=bridge) == right

    def discriminants(self, bridge: pm.SemanticBridge) -> tuple[pm.Discriminant, ...]:
        _ = bridge
        return (
            pm.Discriminant(key="operator", value="QualifierSuffix"),
            pm.Discriminant(key="suffix_type", value=repr(_pattern_type(self.suffix))),
            pm.Discriminant(key="skip_type", value=repr(_pattern_type(self.skip_if))),
            pm.Discriminant(key="include_terminal", value=self.include_terminal),
        )


def op(operator: Operator) -> Op:
    return Op(OperatorType(ref_spec=operator.ref_spec), operator)


def view_as(trait: pm.Spec, pattern: pm.Val) -> Op:
    return op(ViewAs(trait=trait, pattern=pattern))


def satisfy(goal: pm.Spec) -> Op:
    return op(Satisfy(goal=goal))


def variadic_struct(
    *,
    prefix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty,
    middle: pm.Val = pm.ANY,
    suffix: pm.Struct[str | None, pm.Val] = pm.Struct.Empty,
) -> Op:
    return op(VariadicStruct(prefix=prefix, middle=middle, suffix=suffix))


def qualifier_suffix(
    suffix: pm.Val | pm.Type,
    *,
    skip_if: pm.Val | pm.Type = pm.ANY,
    include_terminal: bool = True,
) -> Op:
    return op(
        QualifierSuffix(
            suffix=cast(pm.Val, suffix),
            skip_if=cast(pm.Val, skip_if),
            include_terminal=include_terminal,
        )
    )


def _as_struct(value: object) -> pm.Struct[str | None, pm.Val] | None:
    if isinstance(value, pm.Struct):
        return value
    if isinstance(value, pm.Const) and isinstance(value.__type__, pm.StructType):
        raw_data = value.__data__
        if not isinstance(raw_data, tuple):
            return None
        fields = tuple(
            field_type._wrap(field_data)
            for field_type, field_data in zip(value.__type__.meta_attrs.values, raw_data)
        )
        return pm.Struct.from_keys(value.__type__.meta_attrs.index.keys, fields)
    return None


def _struct_const(struct: pm.Struct[str | None, pm.Val]) -> pm.Const:
    positional: list[pm.Val] = []
    nominal: dict[str, pm.Val] = {}
    for key, value in zip(struct.index.keys, struct.values):
        if key is None:
            positional.append(value)
        else:
            nominal[key] = value
    return pm.struct(*positional, **nominal)


def _normalize_control_struct(
    struct: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> pm.Struct[str | None, pm.Val]:
    values = tuple(pm.normalize(value, bridge=bridge) for value in struct.values)
    if values == struct.values:
        return struct
    return pm.Struct.from_keys(struct.index.keys, values)


def _intersect_control_struct(
    left: pm.Struct[str | None, pm.Val],
    right: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> pm.Struct[str | None, pm.Val] | None:
    if left.index.keys != right.index.keys:
        return None
    values: list[pm.Val] = []
    for left_value, right_value in zip(left.values, right.values):
        value = pm.intersect(left_value, right_value, bridge=bridge)
        if value is None:
            return None
        values.append(value)
    return pm.Struct.from_keys(left.index.keys, tuple(values))


def _subsumes_control_struct(
    left: pm.Struct[str | None, pm.Val],
    right: pm.Struct[str | None, pm.Val],
    *,
    bridge: pm.SemanticBridge,
) -> bool:
    if left.index.keys != right.index.keys:
        return False
    return all(
        pm.subsumes(left_value, right_value, bridge=bridge)
        for left_value, right_value in zip(left.values, right.values)
    )


def _qualifier_suffix_candidates(
    candidate: object,
    *,
    state: pm.MatchState,
    skip_if: pm.Val,
    include_terminal: bool,
    bridge: pm.SemanticBridge,
) -> Iterable[tuple[object, pm.MatchState]]:
    yield candidate, state

    if not isinstance(candidate, pm.NominalQualifier):
        return

    for next_state in pm.match(skip_if, cast(pm.Val, candidate), state=state, bridge=bridge):
        underlying = candidate.underlying
        if isinstance(underlying, pm.NominalQualifier):
            yield from _qualifier_suffix_candidates(
                underlying,
                state=next_state,
                skip_if=skip_if,
                include_terminal=include_terminal,
                bridge=bridge,
            )
        elif include_terminal:
            yield underlying, next_state


def _as_bridge_subject(value: object) -> pm.Val:
    if isinstance(value, pm.Val):
        return value
    if isinstance(value, pm.Type):
        return pm.val(value)
    raise TypeError(f"Expected protomorph value or type, got {type(value).__name__}")


def _pattern_type(value: object) -> pm.Type:
    type_ = getattr(value, "__type__", None)
    if isinstance(type_, pm.Type):
        return type_
    if isinstance(value, pm.Type):
        return value._metatype()
    raise TypeError(f"Expected protomorph pattern, got {type(value).__name__}")


def _normalize_pattern(value: object, *, bridge: pm.SemanticBridge) -> object:
    if isinstance(getattr(value, "__type__", None), pm.Type):
        return pm.normalize(cast(pm.Val, value), bridge=bridge)
    if isinstance(value, pm.Type):
        return value
    raise TypeError(f"Expected protomorph pattern, got {type(value).__name__}")


def _intersect_pattern(
    left: object,
    right: object,
    *,
    bridge: pm.SemanticBridge,
) -> object | None:
    if isinstance(getattr(left, "__type__", None), pm.Type) and isinstance(
        getattr(right, "__type__", None),
        pm.Type,
    ):
        return pm.intersect(cast(pm.Val, left), cast(pm.Val, right), bridge=bridge)
    if isinstance(left, pm.Type) and isinstance(right, pm.Type):
        return left if left == right else None
    return None


def _subsumes_pattern(
    left: object,
    right: object,
    *,
    bridge: pm.SemanticBridge,
) -> bool:
    if isinstance(getattr(left, "__type__", None), pm.Type) and isinstance(
        getattr(right, "__type__", None),
        pm.Type,
    ):
        return pm.subsumes(cast(pm.Val, left), cast(pm.Val, right), bridge=bridge)
    if isinstance(left, pm.Type) and isinstance(right, pm.Type):
        return left == right
    return False
