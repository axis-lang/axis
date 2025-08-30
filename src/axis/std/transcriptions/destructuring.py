"""
Dependency tree transformations:

Transforma una expresion del tipo deptree en una expresion de composicion de tuples:

C = deptree_to_tuple(A, B)

A: std.io(
    console.print: log,
    file(..),
)

B: @root

C: (
    log = @root.std.io.console.print
    ..@root.std.io.file
)
"""
from functools import singledispatchmethod
from protobase import Object
from axis.core import syn, log
from axis.std.expr import Tuple, Member, Sym, Apply


class Destructuring(Object):
    """
    Destructuring para globales

    transforma una expresion desestructurada en un conjunto de expresiones
    Tuple.Element
    'std.io(console.print: log)' -> 'log = std.io.console.print' 
    """

    def __call__(self, expr: syn.Expr, prefix: syn.Expr):
        result = self.transform(expr, prefix)

        def process_expr(elem): 
            # if isinstance(elem, Tuple.Element):
            #     return elem
            if isinstance(elem, Member):
                ' convierte "a.b.c" en "c: a.b.c" '
                return Tuple.NominalElement(
                    key=elem.as_sym(), 
                    value=elem,
                ).with_span_of(elem)
            
            # syn.Error(expr0elem)
        
            return elem
        
        elements=tuple(map(process_expr, deep_flatten(result)))
        
        return Tuple(elements=elements).with_span_of(expr)

    @singledispatchmethod
    def transform(self, expr: syn.Item, prefix: syn.Expr):
        raise NotImplementedError(
            f"{type(self).__qualname__} not implemented for {type(expr).__qualname__}"
        )

    @transform.register
    def eval_none(self, none: None, prefix: syn.Expr):
        return None

    @transform.register
    def eval_sym(self, sym: Sym, prefix: syn.Expr):
        return Member(of=prefix, name=sym.name).with_span_of(sym)

    @transform.register
    def eval_member(self, member: Member, prefix: syn.Expr):
        return member.with_attrs(of=self.transform(member.of, prefix))

    @transform.register
    def eval_apply(self, apply: Apply, prefix: syn.Expr):
        prefix = self.transform(apply.function, prefix)
        return self.transform(apply.argument, prefix)
    
    @transform.register
    def eval_tuple(self, tup: Tuple, prefix: syn.Expr):
        return tuple(self.transform(element, prefix) for element in tup.elements)
    
    @transform.register
    def eval_tuple_value_elem(self, elem: Tuple.ValueElement, prefix: syn.Expr):
        #return elem.with_attrs(value=self.transform(elem.value, prefix))
        return self.transform(elem.value, prefix)

    @transform.register
    def eval_tuple_nominal_elem(self, elem: Tuple.NominalElement, prefix: syn.Expr):
        return elem.with_attrs(
            key=elem.value,
            bound=elem.bound,
            value=self.transform(elem.key, prefix),
        )
    
    @transform.register
    def eval_tuple_spread_elem(self, elem: Tuple.SpreadElement, prefix: syn.Expr):
        return elem.with_attrs(etc=self.transform(elem.etc, prefix))


def reify_destructure(expr: syn.Expr, from_: syn.Expr):
    """
    evalua una expresion de destructuracion
    """
    return Destructuring()(expr, from_)


def deep_flatten(lst):
    lst = list(lst)
    for i, _ in enumerate(lst):
        while (hasattr(lst[i], "__iter__") and not isinstance(lst[i], (str, bytes))):
            lst[i:i + 1] = lst[i]
    return lst

