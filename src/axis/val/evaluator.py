from __future__ import annotations
from decimal import Decimal
from typing import Any, Iterable, Mapping, cast
from protobase import Inmutable, frozendict, mutate
from axis import syn, expr, dom
from axis.log import report as log
from axis.log.report import Report
from axis.literals import Wildcard, WildcardType, EllipsisType
from axis.sem import Scope
from functools import singledispatchmethod


class Evaluator(Inmutable):
    env: frozendict[str, dom.Val] = frozendict()
    scope: Scope | None = None

    @classmethod
    def from_env(
        cls, env: Mapping[str, dom.Val], scope: Scope | None = None
    ):
        return cls(env=_coerce_env(env), scope=scope)

    @classmethod
    def from_scope(cls, scope: Scope, env: Mapping[str, dom.Val] | None = None):
        base_env = _coerce_env(env or {})
        return cls(env=base_env, scope=scope)

    def with_env(self, env: Mapping[str, dom.Val]):
        return mutate(self, env=_coerce_env(env))

    def with_scope(self, scope: Scope | None):
        return mutate(self, scope=scope)

    def __call__(self, node: syn.Node) -> dom.Const:
        value = self.eval(node)
        return _as_const(node, value)

    def boolean(self, value: bool) -> dom.Val:
        return _value_const(value)

    def natural(self, value: int) -> dom.Val:
        return _value_const(value)

    def whole(self, value: int) -> dom.Val:
        return _value_const(value)

    def integer(self, value: int) -> dom.Val:
        return _value_const(value)
    
    def decimal(self, value: Decimal) -> dom.Val:
        return _value_const(value)
    
    def text(self, value: str) -> dom.Val:
        return _value_const(value)

    def struct(
        self,
        keys: Iterable[str | None],
        bounds: Iterable[dom.Type],
        values: Iterable[dom.Data],
    ):
        index = dom.Struct.Index(tuple(k for k in keys))
        fields = cast(
            dom.Struct[str, dom.Type], dom.Struct(index=index, values=tuple(bounds))
        )
        struct = dom.StructType(fields=cast(dom.Struct[str, dom.Type], fields))
        return dom.Const(type=struct, data=tuple(values))

    def _error(self, node: syn.Node, message: str):
        log.error(message).label(node, message).throw()

    def _resolve_env(self, sym: expr.Sym) -> dom.Val:
        key = str(sym)
        if key in self.env:
            value = self.env[key]
            return _coerce_env_value(sym, value)
        if self.scope is None:
            self._error(sym, f"Unbound symbol: {key}")
        value = self.scope.lookup(sym)
        return _coerce_scope_value(sym, value)

    def _numeric_result(self, value: int | Decimal) -> dom.Val:
        if isinstance(value, Decimal):
            return self.decimal(value)
        if isinstance(value, bool):
            return self.boolean(value)
        return self.integer(value)


    @singledispatchmethod
    def eval(cls, node: syn.Node) -> dom.Val:
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
def eval_lit(evaluator: Evaluator, node: expr.Lit) -> dom.Val:
    value = node.value

    if value is Ellipsis:
        evaluator._error(node, "Ellipsis is not a value")
    elif value is Wildcard:
        evaluator._error(node, "Wildcard is not a value")

    assert not isinstance(value, (EllipsisType, WildcardType))

    return dom.Const.of_literal(value)


@Evaluator.impl(expr.Tuple)
def eval_tuple(evaluator: Evaluator, node: expr.Tuple) -> dom.Val:
    keys: list[str | None] = []
    bounds: list[dom.Type] = []
    values: list[dom.Data] = []

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
def eval_sym(evaluator: Evaluator, node: expr.Sym) -> dom.Val:
    return evaluator._resolve_env(node)


@Evaluator.impl(expr.Additive)
def eval_additive(evaluator: Evaluator, node: expr.Additive) -> dom.Val:
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
def eval_productive(evaluator: Evaluator, node: expr.Productive) -> dom.Val:
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
def eval_sign(evaluator: Evaluator, node: expr.Sign) -> dom.Val:
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
def eval_compound(evaluator: Evaluator, node: expr.Compound) -> dom.Val:
    last_result: dom.Val | None = None
    for component in node.components:
        last_result = evaluator.eval(component)
    if last_result is None:
        evaluator._error(node, "Empty compound expression")
    return last_result


@Evaluator.impl(expr.Apply)
def eval_apply(evaluator: Evaluator, node: expr.Apply) -> dom.Val:
    evaluator._error(node, "Apply expressions are not implemented yet")


@Evaluator.impl(expr.Index)
def eval_index(evaluator: Evaluator, node: expr.Index) -> dom.Val:
    evaluator._error(node, "Index expressions are not implemented yet")


@Evaluator.impl(expr.Member)
def eval_member(evaluator: Evaluator, node: expr.Member) -> dom.Val:
    evaluator._error(node, "Member expressions are not implemented yet")


def _coerce_env(env: Mapping[str, dom.Val]) -> frozendict[str, dom.Val]:
    if isinstance(env, frozendict):
        return env
    return frozendict(env)


def _value_const(value: dom.Literal) -> dom.Const:
    return dom.Const.of_literal(value)


def _as_const(node: syn.Node, value: dom.Val) -> dom.Const:
    if isinstance(value, dom.Const):
        return value
    if isinstance(value, dom.Pure):
        return dom.Const(type=value.type, data=value.data)
    if isinstance(value, dom.Err):
        _raise_err(value, node=node)
    raise TypeError(f"Expected Pure value, got {type(value)}")


def _as_pure(node: syn.Node, value: dom.Val) -> dom.Pure:
    if isinstance(value, dom.Pure):
        return value
    if isinstance(value, dom.Err):
        _raise_err(value, node=node)
    log.error("Expected pure value").label(node, "expected pure value").throw()
    raise TypeError("Unreachable")


def _numeric_operand(
    node: syn.Node,
    value: dom.Val,
    message: str = "Numeric operand required",
) -> int | Decimal:
    pure = _as_pure(node, value)
    data = pure.data
    if not isinstance(data, (int, Decimal)):
        log.error(message).label(node, message).throw()
    return data


def _raise_err(err: dom.Err, node: syn.Node | None = None) -> None:
    report = Report.of(err)
    if report is not None:
        raise Report.Exception(report).with_traceback(None)
    message = "Invalid error value"
    builder = log.error(message)
    if node is not None:
        builder = builder.label(node, message)
    builder.throw()


def _coerce_env_value(sym: expr.Sym, value: dom.Val) -> dom.Val:
    if isinstance(value, dom.Err):
        _raise_err(value, node=sym)
    if isinstance(value, (dom.Val, dom.Pure)):
        return value
    raise TypeError(f"Invalid env value for {sym}: {type(value)}")


def _coerce_scope_value(sym: expr.Sym, value: dom.Val) -> dom.Val:
    if isinstance(value, dom.Err):
        _raise_err(value, node=sym)
    if isinstance(value, dom.Val):
        return value
    raise TypeError(f"Invalid scope value for {sym}: {type(value)}")
