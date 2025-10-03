from protobase import Record
from axis import syn, expr, builtins
from functools import singledispatchmethod

type R = tuple[R, int]


class Evaluator(Record, frozen=True):
    # type Bound = type
    type Result = tuple[Bound, builtins.All]

    def __call__(self, node: syn.Node) -> Result:
        return self.eval(node)
        # return Value(meta=descriptor, payload=payload)

    @singledispatchmethod
    def eval(cls, node: syn.Node) -> Result:
        raise NotImplementedError(f"Cannot evaluate node of type {type(node)}")

    @classmethod
    def impl(cls, node_type: type[syn.Node]):
        def decorator(func):
            cls.eval.register(node_type, func)  # type: ignore
            return func

        return decorator




@Evaluator.impl(expr.Lit)
def eval_lit(evaluator: Evaluator, node: expr.Lit) -> Evaluator.Result:
    match node.value:
        # case None:
        #     return None, None
        case bool() as b:
            return bool, b
        case int() as i:
            return int, i
        case float() as f:
            return float, f
        case str() as s:
            return str, s
        case builtins.Decimal() as d:
            return builtins.Decimal, d
    raise NotImplementedError(f"Literal of type {type(node.value)} not implemented")


@Evaluator.impl(expr.Tuple)
def eval_tuple(evaluator: Evaluator, node: expr.Tuple) -> Evaluator.Result:
    bounds: list[Bound] = []
    values: list[builtins.All] = []
    keymap: list[builtins.All] = []

    for element in node.elements:
        match element:
            case expr.Tuple.Positional(value=value):
                bound, value = evaluator.eval(value)
                bounds.append(bound)
                values.append(value)
                keymap.append(None)

            case expr.Tuple.Nominal(key=key, bound=coherce, value=value):
                bound, value = evaluator.eval(value)
                # if bound.. debe cohercionar value
                assert isinstance(key, expr.Sym)
                keymap.append(key.name)
                bounds.append(bound)
                values.append(value)

    return (
        TupleBound(index=builtins.SparseIndex(tuple(keymap)), bound=tuple(bounds)),
        tuple(values),
    )


class Bound(Record, frozen=True, consed=True, abstract=True):
    def __get_property__(self, value: builtins.All, property: str) -> Evaluator.Result:
        raise NotImplementedError(
            f"Cannot get property {property} of value {value} with type {type(value)}"
        )

class TupleBound(Bound, frozen=True, consed=True):
    "Array[index] bound"

    index: builtins.SparseIndex
    bound: tuple[Bound, ...]

    def __get_property__(self, value: builtins.All, property: str) -> Evaluator.Result:
        offset = self.index.offsets[property]
        match value:
            case tuple() as values:
                return self.bound[offset], values[offset]
            case _:
                return super().__get_property__(value, property)


def get_property(value: Evaluator.Result, property: str) -> Evaluator.Result:
    bound, val = value
    return bound.__get_property__(val, property)


# class Monad(Record, consed=True, abstract=True):
#     def __call__(self, value: Evaluator.Result) -> Evaluator.Result:
#         raise NotImplementedError()
# class GetProperty(Monad):
#     property: str

# alpha.{..k}.property