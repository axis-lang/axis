from __future__ import annotations
from decimal import Decimal
from typing import Any, Iterable, Mapping, cast

from functools import singledispatchmethod

from protobase import Inmutable, frozendict, mutate
from axis import dom, expr, log, syn
from axis.literals import Wildcard, WildcardType, EllipsisType
from axis.sem import Scope


class Evaluator(Inmutable):
    env: frozendict[str, std.Val] = frozendict()
    scope: Scope | None = None

    @classmethod
    def from_env(
        cls, env: Mapping[str, std.Val], scope: Scope | None = None
    ):
        return cls(env=_coerce_env(env), scope=scope)

    @classmethod
    def from_scope(cls, scope: Scope, env: Mapping[str, std.Val] | None = None):
        base_env = _coerce_env(env or {})
        return cls(env=base_env, scope=scope)

    def with_env(self, env: Mapping[str, std.Val]):
        return mutate(self, env=_coerce_env(env))

    def with_scope(self, scope: Scope | None):
        return mutate(self, scope=scope)

    def __call__(self, node: syn.Node) -> std.Const:
        value = self.eval(node)
        return _as_const(node, value)

    def boolean(self, value: bool) -> std.Val:
        return _value_const(value)

    def natural(self, value: int) -> std.Val:
        return _value_const(value)

    def whole(self, value: int) -> std.Val:
        return _value_const(value)

    def integer(self, value: int) -> std.Val:
        return _value_const(value)
    
    def decimal(self, value: Decimal) -> std.Val:
        return _value_const(value)
    
    def text(self, value: str) -> std.Val:
        return _value_const(value)

    def struct(
        self,
        keys: Iterable[str | None],
        bounds: Iterable[std.Type],
        values: Iterable[std.Data],
    ):
        index = std.Struct.Index(tuple(k for k in keys))
        fields = cast(
            std.Struct[str, std.Type], std.Struct(index=index, values=tuple(bounds))
        )
        struct = std.StructType(meta_fields=cast(std.Struct[str, std.Type], fields))
        return std.Const(type=struct, data=tuple(values))

    def _error(self, node: syn.Node, message: str):
        log.error(message).label(node, message).throw()

    def _resolve_env(self, sym: expr.Sym) -> std.Val:
        key = str(sym)
        if key in self.env:
            value = self.env[key]
            return _coerce_env_value(sym, value)
        if self.scope is None:
            self._error(sym, f"Unbound symbol: {key}")
        value = self.scope.lookup(sym)
        return _coerce_scope_value(sym, value)

    def _numeric_result(self, value: int | Decimal) -> std.Val:
        if isinstance(value, Decimal):
            return self.decimal(value)
        if isinstance(value, bool):
            return self.boolean(value)
        return self.integer(value)


    @singledispatchmethod
    def eval(cls, node: syn.Node) -> std.Val:
        raise NotImplementedError(f"Cannot evaluate node of type {type(node)}")

    @classmethod
    def impl(cls, node_type: type[syn.Node]):
        def decorator(func):
            dispatch = cast(Any, cls.eval)
            register = cast(Any, dispatch.register)
            register(node_type)(func)
            return func

        return decorator


@Evaluator.impl(expr.Lit)
def eval_lit(evaluator: Evaluator, node: expr.Lit) -> std.Val:
    value = node.value

    if value is Ellipsis:
        evaluator._error(node, "Ellipsis is not a value")
    elif value is Wildcard:
        evaluator._error(node, "Wildcard is not a value")

    assert not isinstance(value, (EllipsisType, WildcardType))

    return std.Const.new_literal(value)


@Evaluator.impl(expr.Tuple)
def eval_tuple(evaluator: Evaluator, node: expr.Tuple) -> std.Val:
    keys: list[str | None] = []
    bounds: list[std.Type] = []
    values: list[std.Data] = []

    for element in node.elements:
        match element:
            case expr.Tuple.Positional(value=value):
                result = evaluator.eval(value)
                pure = _as_pure(value, result)
                keys.append(None)
                bounds.append(pure.type)
                values.append(pure.data)

            case expr.Tuple.Nominal(key=key, bound=bound, value=value):
                value_expr = value if value is not None else key
                result = evaluator.eval(value_expr)
                pure = _as_pure(value_expr, result)
                keys.append(expr.to_slot_name(key))
                bounds.append(pure.type)
                values.append(pure.data)

    return evaluator.struct(keys, bounds, values)


@Evaluator.impl(expr.Sym)
def eval_sym(evaluator: Evaluator, node: expr.Sym) -> std.Val:
    return evaluator._resolve_env(node)


@Evaluator.impl(expr.Additive)
def eval_additive(evaluator: Evaluator, node: expr.Additive) -> std.Val:
    lhs = _numeric_operand(node.lhs, evaluator.eval(node.lhs))
    rhs = _numeric_operand(node.rhs, evaluator.eval(node.rhs))

    op = node.op.symbol.value
    if isinstance(lhs, Decimal) or isinstance(rhs, Decimal):
        lhs = Decimal(lhs)
        rhs = Decimal(rhs)

    match op:
        case "+":
            return evaluator._numeric_result(lhs + rhs)  # type: ignore[arg-type]
        case "-":
            return evaluator._numeric_result(lhs - rhs)  # type: ignore[arg-type]
    evaluator._error(node, f"Unsupported additive operator: {op}")


@Evaluator.impl(expr.Productive)
def eval_productive(evaluator: Evaluator, node: expr.Productive) -> std.Val:
    lhs = _numeric_operand(node.lhs, evaluator.eval(node.lhs))
    rhs = _numeric_operand(node.rhs, evaluator.eval(node.rhs))

    op = node.op.symbol.value
    if isinstance(lhs, Decimal) or isinstance(rhs, Decimal) or op == "/":
        lhs = Decimal(lhs)
        rhs = Decimal(rhs)

    match op:
        case "*" | "·":
            return evaluator._numeric_result(lhs * rhs)  # type: ignore[arg-type]
        case "/":
            return evaluator.decimal(cast(Decimal, Decimal(lhs) / Decimal(rhs)))
        case "%":
            return evaluator._numeric_result(lhs % rhs)  # type: ignore[arg-type]
    evaluator._error(node, f"Unsupported productive operator: {op}")


@Evaluator.impl(expr.Sign)
def eval_sign(evaluator: Evaluator, node: expr.Sign) -> std.Val:
    value = evaluator.eval(node.rhs)
    op = node.op.symbol.value

    match op:
        case "+":
            operand = _numeric_operand(node.rhs, value, "Unary + requires a numeric operand")
            return evaluator._numeric_result(operand)
        case "-":
            operand = _numeric_operand(node.rhs, value, "Unary - requires a numeric operand")
            return evaluator._numeric_result(-operand)
        case "!":
            pure = _as_pure(node.rhs, value)
            if not isinstance(pure.data, bool):
                evaluator._error(node, "Unary ! requires a boolean operand")
            return evaluator.boolean(not pure.data)
        case "~":
            pure = _as_pure(node.rhs, value)
            if not isinstance(pure.data, int) or isinstance(pure.data, bool):
                evaluator._error(node, "Unary ~ requires an integer operand")
            return evaluator.integer(~pure.data)

    evaluator._error(node, f"Unsupported unary operator: {op}")


@Evaluator.impl(expr.Compound)
def eval_compound(evaluator: Evaluator, node: expr.Compound) -> std.Val:
    last_result: std.Val | None = None
    for component in node.components:
        last_result = evaluator.eval(component)
    if last_result is None:
        evaluator._error(node, "Empty compound expression")
    return last_result


@Evaluator.impl(expr.Apply)
def eval_apply(evaluator: Evaluator, node: expr.Apply) -> std.Val:
    evaluator._error(node, "Apply expressions are not implemented yet")


@Evaluator.impl(expr.Index)
def eval_index(evaluator: Evaluator, node: expr.Index) -> std.Val:
    evaluator._error(node, "Index expressions are not implemented yet")


@Evaluator.impl(expr.Member)
def eval_member(evaluator: Evaluator, node: expr.Member) -> std.Val:
    evaluator._error(node, "Member expressions are not implemented yet")


def _coerce_env(env: Mapping[str, std.Val]) -> frozendict[str, std.Val]:
    if isinstance(env, frozendict):
        return env
    return frozendict(env)


def _value_const(value: std.Literal) -> std.Const:
    return std.Const.new_literal(value)


def _as_const(node: syn.Node, value: std.Val) -> std.Const:
    if isinstance(value, std.Const):
        return value
    if isinstance(value, std.Pure):
        return std.Const(type=value.type, data=value.data)
    if isinstance(value, std.Err):
        _raise_err(value, node=node)
    raise TypeError(f"Expected Pure value, got {type(value)}")


def _as_pure(node: syn.Node, value: std.Val) -> std.Pure:
    if isinstance(value, std.Pure):
        return value
    if isinstance(value, std.Err):
        _raise_err(value, node=node)
    log.error("Expected pure value").label(node, "expected pure value").throw()
    raise TypeError("Unreachable")


def _numeric_operand(
    node: syn.Node,
    value: std.Val,
    message: str = "Numeric operand required",
) -> int | Decimal:
    pure = _as_pure(node, value)
    data = pure.data
    if not isinstance(data, (int, Decimal)):
        log.error(message).label(node, message).throw()
    return data


def _raise_err(err: std.Err, node: syn.Node | None = None) -> None:
    report = log.Report.of(err)
    if report is not None:
        raise log.Report.Exception(report).with_traceback(None)
    message = "Invalid error value"
    builder = log.error(message)
    if node is not None:
        builder = builder.label(node, message)
    builder.throw()


def _coerce_env_value(sym: expr.Sym, value: std.Val) -> std.Val:
    if isinstance(value, std.Err):
        _raise_err(value, node=sym)
    if isinstance(value, (std.Val, std.Pure)):
        return value
    raise TypeError(f"Invalid env value for {sym}: {type(value)}")


def _coerce_scope_value(sym: expr.Sym, value: std.Val) -> std.Val:
    if isinstance(value, std.Err):
        _raise_err(value, node=sym)
    if isinstance(value, std.Val):
        return value
    raise TypeError(f"Invalid scope value for {sym}: {type(value)}")
