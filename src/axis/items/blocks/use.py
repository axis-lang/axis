from functools import singledispatchmethod
from typing import ClassVar, Literal, Optional, Self

from protobase import Inmutable, Object, cached_property

from axis import expr, log, syn


class Use(syn.Block, Inmutable):
    """
    Represents a 'use' entity:
    use x
    """

    outline_keyword: ClassVar[str] = "use"
    #grammar: ClassVar[str] = "use: 'use' expression EOF;"

    import_expr: syn.Expr

    @classmethod
    def build(
        cls,
        kw: Literal["use"],
        import_expr: syn.Expr,
        *,
        children: tuple[syn.Block, ...],
        **kwargs,
    ) -> Self:
        return cls(import_expr=import_expr)

    @cached_property
    def flat_expr(self) -> expr.Tuple:
        return reify_destructure(self.import_expr, from_=expr.Sym.ROOT)

    # def contribute_to_scope(self, scope: sem.Scope.Builder) -> None:
    #     for element in self.flat_expr.elements:
    #         match element:
    #             case expr.Tuple.NominalElement(key=key, value=value):
    #                 assert isinstance(key, expr.Sym)
    #                 if key.at is not None:
    #                     log.error(f"Use key cannot have 'at' qualifier: {key}").with_label(self.as_label).emit()
    #                 scope.add(key, value)
    #             case expr.Tuple.ValueElement(value=value):
    #                 # if not isinstance(value, expr.Sym):
    #                 #     syn.Error(f"Use value must be a symbol, got {value}").with_label(self.as_label).throw()
    #                 # scope.add(value.name, value)
    #                 pass
    #             case expr.Tuple.SpreadElement(etc=etc):
    #                 #syn.Error(f"Spread elements are not allowed in use statements: {etc}").with_label(self.as_label).throw()
    #                 pass
    #             case _:
    #                 log.error(f"Invalid element in use statement: {element}").with_label(element.as_label).emit()
    #                 #syn.Error(f"Invalid element in use statement: {element}").with_label(self.as_label).throw()

class Destructuring(Object):
    """
    Destructuring para globales

    transforma una expresion desestructurada en un conjunto de expresiones
    Tuple.Element
    'std.io(console.print: log)' -> 'log = std.io.console.print' 

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



    def __call__(self, exp: syn.Expr, prefix: syn.Expr):
        result = self.transform(exp, prefix)

        def process_expr(elem): 
            # if isinstance(elem, Tuple.Element):
            #     return elem
            if isinstance(elem, expr.Member):
                ' convierte "a.b.c" en "c: a.b.c" '
                return expr.Tuple.Nominal(
                    key=elem.as_sym(),
                    bound=None,
                    value=elem,
                ).with_span_of(elem)
            
            # syn.Error(expr0elem)
        
            return elem
        
        elements=tuple(map(process_expr, deep_flatten(result)))
        
        return expr.Tuple(elements=elements).with_span_of(exp)

    @singledispatchmethod
    def transform(self, expr: syn.Item, prefix: syn.Expr):
        raise NotImplementedError(
            f"{type(self).__qualname__} not implemented for {type(expr).__qualname__}"
        )

    @transform.register
    def eval_none(self, none: None, prefix: syn.Expr):
        return None

    @transform.register
    def eval_sym(self, sym: expr.Sym, prefix: syn.Expr):
        return expr.Member(of=prefix, name=sym.name).with_span_of(sym)

    @transform.register
    def eval_member(self, member: expr.Member, prefix: syn.Expr):
        return member.with_attr(of=self.transform(member.of, prefix))

    @transform.register
    def eval_apply(self, apply: expr.Apply, prefix: syn.Expr):
        prefix = self.transform(apply.function, prefix)
        return self.transform(apply.argument, prefix)
    
    @transform.register
    def eval_tuple(self, tup: expr.Tuple, prefix: syn.Expr):
        return tuple(self.transform(element, prefix) for element in tup.elements)
    
    @transform.register
    def eval_tuple_value_elem(self, elem: expr.Tuple.Positional, prefix: syn.Expr):
        #return elem.with_attrs(value=self.transform(elem.value, prefix))
        return self.transform(elem.value, prefix)

    @transform.register
    def eval_tuple_nominal_elem(self, elem: expr.Tuple.Nominal, prefix: syn.Expr):
        return elem.with_attr(
            key=elem.value,
            value=self.transform(elem.key, prefix),
        )
    
    # @transform.register
    # def eval_tuple_spread_elem(self, elem: expr.Tuple.Spread, prefix: syn.Expr):
    #     return elem.with_attr(etc=self.transform(elem.etc, prefix))


def reify_destructure(expr: syn.Expr, from_: syn.Expr):
    """
    evalua una expresion de destructuracion
    """
    return Destructuring()(expr, from_)


def deep_flatten(lst, leaf_types=(str, bytes)):
    lst = list(lst)
    for i, _ in enumerate(lst):
        while (hasattr(lst[i], "__iter__") and not isinstance(lst[i], leaf_types)):
            lst[i:i + 1] = lst[i]
    return lst
