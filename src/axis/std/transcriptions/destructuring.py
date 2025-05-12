from functools import singledispatchmethod
from protobase import Object
from axis.core import syn, log
from axis.std.expressions import Tuple, Member, Sym, Apply

class Destructuring(Object):
    """
    transforma una expresion desestructurada en un conjunto de expresiones
    Tuple.Element
    'std.io(log=console.print)' -> 'log = std.io.console.print' 
    """

    def __call__(self, expr: syn.Expr, bound: syn.Expr):
        result = self.transform(expr, bound)

        def process_element(elem): 
            if isinstance(elem, Tuple.Element):
                return elem
            if isinstance(elem, Member):
                ' convierte "a.b.c" en "c: a.b.c" '
                return Tuple.Element(
                    key=Sym(name=elem.name).with_span_of(elem), 
                    bound=elem, 
                    value=None,
                ).with_span_of(elem)
        
            return None
        
        return tuple(map(process_element, deep_flatten(result)))

    @singledispatchmethod
    def transform(self, expr: syn.Item, bound: syn.Expr):
        raise NotImplementedError(
            f"{type(self).__qualname__} not implemented for {type(expr).__qualname__}"
        )

    @transform.register
    def eval_sym(self, sym: Sym, bound: syn.Expr):
        return syn.Member(of=bound, name=sym.name).with_span_of(sym)

    @transform.register
    def eval_member(self, member: Member, bound: syn.Expr):
        return member.with_attrs(of=self.transform(member.of, bound))

    @transform.register
    def eval_apply(self, apply: Apply, bound: syn.Expr):
        bound = self.transform(apply.function, bound)
        return tuple(self.transform(arg, bound) for arg in apply.argument.elements)

    @transform.register
    def eval_tuple_elem(self, element: Tuple.Element, bound: syn.Expr):
        if element.value is not None:
            #log.error(f"Invalid destructuring expression").with_label(element.value, "Invalid use of element value").emit()
            return self.transform(element.value, bound)

        if element.key is not None:
            bound = self.transform(element.bound, bound)
            
            if isinstance(element.key, Sym):
                return element.with_attrs(bound=bound)
                
            log.error(f"Invalid destructuring expression").with_label(element.bound, "Invalid use of element key").emit()

            return element.with_attrs(bound=bound)
        
        return self.transform(element.bound, bound)

def reify_destructure(expr: syn.Expr, from_: syn.Expr):
    """
    evalua una expresion de destructuracion
    """
    return Destructuring()(expr, from_)

# deep_flat_map

def deep_flatten(lst):
    lst = list(lst)
    for i, _ in enumerate(lst):
        while (hasattr(lst[i], "__iter__") and not isinstance(lst[i], (str, bytes))):
            lst[i:i + 1] = lst[i]
    return lst

