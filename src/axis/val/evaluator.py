from __future__ import annotations
from decimal import Decimal
from typing import Any, Iterable, Mapping, cast
from protobase import Inmutable, frozendict, mutate
from axis import log, syn, expr, dom
from functools import singledispatchmethod


class Evaluator(Inmutable):
    # type Bound = type
    type EvalResult = tuple[dom.Type, dom.Data]
    type EnvValue = dom.Dom | EvalResult

    env: frozendict = frozendict()

    @classmethod
    def from_env(cls, env: Mapping[str, "Evaluator.EnvValue"]):
        return cls(env=_coerce_env(env))

    def with_env(self, env: Mapping[str, "Evaluator.EnvValue"]):
        return mutate(self, env=_coerce_env(env))

    def __call__(self, node: syn.Node) -> dom.Const:
        type_, data = self.eval(node)
        return dom.Const(type=type_, data=cast(dom.Data, data))

    def boolean(self, value: bool) -> EvalResult:
        return _builtin_nominal("Boolean"), value

    def natural(self, value: int) -> EvalResult:
        return _builtin_nominal("Natural"), value

    def whole(self, value: int) -> EvalResult:
        return _builtin_nominal("Whole"), value

    def integer(self, value: int) -> EvalResult:
        return _builtin_nominal("Integer"), value
    
    def decimal(self, value: Decimal) -> EvalResult:
        return _builtin_nominal("Decimal"), value
    
    def text(self, value: str) -> EvalResult:
        return _builtin_nominal("Text"), value

    def struct(
        self,
        keys: Iterable[str | None],
        bounds: Iterable[dom.Type],
        values: Iterable[dom.Data],
    ):
        index = dom.Index(tuple(k for k in keys))
        fields = cast(dom.Tuple[str, dom.Type], dom.Tuple(index=index, values=tuple(bounds)))
        struct = dom.StructType(fields=cast(dom.Tuple[str, dom.Type], fields))
        return struct, tuple(values)

    def _error(self, node: syn.Node, message: str):
        diag = log.error(message)
        if node.span is not None:
            diag = diag.with_label(node.as_label(message))
        diag.throw()

    def _resolve_env(self, sym: expr.Sym) -> EvalResult:
        key = str(sym)
        if key not in self.env:
            self._error(sym, f"Unbound symbol: {key}")
        value = self.env[key]
        if isinstance(value, dom.Dom):
            return value.type, _env_data(value)
        if isinstance(value, tuple) and len(value) == 2:
            return value  # type: ignore[return-value]
        raise TypeError(f"Invalid env value for {key}: {type(value)}")

    def _numeric_result(self, value: int | Decimal) -> EvalResult:
        if isinstance(value, Decimal):
            return self.decimal(value)
        if isinstance(value, bool):
            return self.boolean(value)
        return self.integer(value)


    @singledispatchmethod
    def eval(cls, node: syn.Node) -> EvalResult:
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
def eval_lit(evaluator: Evaluator, node: expr.Lit) -> Evaluator.EvalResult:
    value = node.value
    if isinstance(value, float):
        value = Decimal(value)
    literal = dom.Const.from_literal(value)
    return literal.type, literal.data


@Evaluator.impl(expr.Tuple)
def eval_tuple(evaluator: Evaluator, node: expr.Tuple) -> Evaluator.EvalResult:
    keys: list[str | None] = []
    bounds: list[dom.Type] = []
    values: list[dom.Data] = []

    for element in node.elements:
        match element:
            case expr.Tuple.Positional(value=value):
                bound, value = evaluator.eval(value)
                keys.append(None)
                bounds.append(bound)
                values.append(value)

            case expr.Tuple.Nominal(key=key, bound=bound, value=value):
                # key: {'literal'}
                bound, value = evaluator.eval(value)
                # if bound.. debe cohercionar value
                assert isinstance(key, expr.Sym)
                keys.append(key.name)
                bounds.append(bound)
                values.append(value)

    return evaluator.struct(keys, bounds, values)


@Evaluator.impl(expr.Sym)
def eval_sym(evaluator: Evaluator, node: expr.Sym) -> Evaluator.EvalResult:
    return evaluator._resolve_env(node)


@Evaluator.impl(expr.Additive)
def eval_additive(evaluator: Evaluator, node: expr.Additive) -> Evaluator.EvalResult:
    lhs_meta, lhs = evaluator.eval(node.lhs)
    rhs_meta, rhs = evaluator.eval(node.rhs)

    if not isinstance(lhs, (int, Decimal)) or not isinstance(rhs, (int, Decimal)):
        evaluator._error(node, "Additive operator requires numeric operands")

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
def eval_productive(evaluator: Evaluator, node: expr.Productive) -> Evaluator.EvalResult:
    lhs_meta, lhs = evaluator.eval(node.lhs)
    rhs_meta, rhs = evaluator.eval(node.rhs)

    if not isinstance(lhs, (int, Decimal)) or not isinstance(rhs, (int, Decimal)):
        evaluator._error(node, "Productive operator requires numeric operands")

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
def eval_sign(evaluator: Evaluator, node: expr.Sign) -> Evaluator.EvalResult:
    type_, value = evaluator.eval(node.rhs)
    op = node.op.symbol.value

    match op:
        case "+":
            if not isinstance(value, (int, Decimal)):
                evaluator._error(node, "Unary + requires a numeric operand")
            return evaluator._numeric_result(value)
        case "-":
            if not isinstance(value, (int, Decimal)):
                evaluator._error(node, "Unary - requires a numeric operand")
            return evaluator._numeric_result(-value)
        case "!":
            if not isinstance(value, bool):
                evaluator._error(node, "Unary ! requires a boolean operand")
            return evaluator.boolean(not value)
        case "~":
            if not isinstance(value, int):
                evaluator._error(node, "Unary ~ requires an integer operand")
            return evaluator.integer(~value)

    evaluator._error(node, f"Unsupported unary operator: {op}")


@Evaluator.impl(expr.Compound)
def eval_compound(evaluator: Evaluator, node: expr.Compound) -> Evaluator.EvalResult:
    last_result: Evaluator.EvalResult | None = None
    for component in node.components:
        last_result = evaluator.eval(component)
    if last_result is None:
        evaluator._error(node, "Empty compound expression")
    return last_result


@Evaluator.impl(expr.Apply)
def eval_apply(evaluator: Evaluator, node: expr.Apply) -> Evaluator.EvalResult:
    evaluator._error(node, "Apply expressions are not implemented yet")


@Evaluator.impl(expr.Index)
def eval_index(evaluator: Evaluator, node: expr.Index) -> Evaluator.EvalResult:
    evaluator._error(node, "Index expressions are not implemented yet")


@Evaluator.impl(expr.Member)
def eval_member(evaluator: Evaluator, node: expr.Member) -> Evaluator.EvalResult:
    evaluator._error(node, "Member expressions are not implemented yet")


def _coerce_env(env: Mapping[str, "Evaluator.EnvValue"]) -> frozendict:
    if isinstance(env, frozendict):
        return env
    return frozendict(env)


def _builtin_nominal(name: str) -> dom.Type:
    return dom.NominalType.from_str(f"std.{name}")


def _env_data(value: dom.Dom) -> dom.Data:
    if hasattr(value, "data"):
        return cast(dom.Data, getattr(value, "data"))
    raise TypeError("Env values must carry data")
