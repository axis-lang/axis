from __future__ import annotations
from decimal import Decimal
from typing import Iterable
from protobase import Record
from axis import syn, expr, dom
from functools import singledispatchmethod

type R = tuple[R, int]


class Evaluator(Record, frozen=True):
    # type Bound = type
    type EvalResult = tuple[dom.Meta, dom.Data]

    def __call__(self, node: syn.Node) -> dom.Val:
        meta, data = self.eval(node)
        return dom.Val(meta=meta, data=data)

    def boolean(self, value: bool) -> EvalResult:
        return dom.ConstSymbol(('std', 'Boolean'), dom.Tuple.EMPTY), value

    def natural(self, value: int) -> EvalResult:
        return dom.ConstSymbol(('std', 'Natural'), dom.Tuple.EMPTY), value

    def whole(self, value: int) -> EvalResult:
        return dom.ConstSymbol(('std', 'Whole'), dom.Tuple.EMPTY), value

    def integer(self, value: int) -> EvalResult:
        return dom.ConstSymbol(('std', 'Integer'), dom.Tuple.EMPTY), value
    
    def decimal(self, value: Decimal) -> EvalResult:
        return dom.ConstSymbol(('std', 'Decimal'), dom.Tuple.EMPTY), value
    
    def text(self, value: str) -> EvalResult:
        return dom.ConstSymbol(('std', 'Text'), dom.Tuple.EMPTY), value

    def struct(self, keys: Iterable[str], bounds: Iterable[dom.Meta], values: Iterable[dom.Data]):
        index = dom.Index(tuple(keys))
        fields = dom.Tuple(index=index, values=tuple(bounds))
        if all(isinstance(b, dom.Const) for b in bounds):
            struct = dom.ConstStruct(fields=fields) # type: ignore
            return struct, tuple(values)
        raise NotImplementedError("Only constant structs are implemented")


    @singledispatchmethod
    def eval(cls, node: syn.Node) -> EvalResult:
        raise NotImplementedError(f"Cannot evaluate node of type {type(node)}")

    @classmethod
    def impl(cls, node_type: type[syn.Node]):
        def decorator(func):
            cls.eval.register(node_type, func)  # type: ignore
            return func

        return decorator


@Evaluator.impl(expr.Lit)
def eval_lit(evaluator: Evaluator, node: expr.Lit) -> Evaluator.EvalResult:
    match node.value:
        case bool() as b:
            return evaluator.boolean(b)
        case int() as i:
            return evaluator.integer(i)
        case float() as f:
            return evaluator.decimal(Decimal(f))
        case str() as s:
            return evaluator.text(s)
        case Decimal() as d:
            return evaluator.decimal(d)
    raise NotImplementedError(f"Literal of type {type(node.value)} not implemented")


@Evaluator.impl(expr.Tuple)
def eval_tuple(evaluator: Evaluator, node: expr.Tuple) -> Evaluator.EvalResult:
    keys: list[dom.Data] = []
    bounds: list[dom.Meta] = []
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

