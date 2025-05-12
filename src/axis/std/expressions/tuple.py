from typing import Optional
from axis.core import syn

class Tuple(syn.Expr):
    '''
    '''

    class Element(syn.Node):
        key: Optional[syn.Expr]
        bound: Optional[syn.Expr]
        value: Optional[syn.Expr]

    elements: tuple[Element, ...]

@syn.AstBuilder.build.register
def build_tuple_ast(
    self,
    ctx: syn.AxisParser.TupleContext | syn.AxisParser.ShapeContext,
    *elements: tuple[Tuple.Element, ...],
) -> Tuple:
    return Tuple(elements=elements)

@syn.AstBuilder.build.register
def build_tuple_element_value_ast(
    self, 
    ctx: syn.AxisParser.TupleElementSingleContext, 
    value: syn.Expr,
):
    return Tuple.Element(key=None, bound=None, value=value)

@syn.AstBuilder.build.register
def build_tuple_element_assign_ast(
    self,
    ctx: syn.AxisParser.TupleElementAssignationContext,
    key: syn.Expr,
    _assign,
    value: syn.Expr,
):
    return Tuple.Element(key=key, bound=None, value=value)

@syn.AstBuilder.build.register
def build_tuple_element_bound_ast(
    self,
    ctx: syn.AxisParser.TupleElementBoundedContext,
    key: syn.Expr,
    _colon,
    bound: syn.Expr,
):
    return Tuple.Element(key=key, bound=bound, value=None)

@syn.AstBuilder.build.register
def build_tuple_element_full_ast(
    self,
    ctx: syn.AxisParser.TupleElementBoundedAssignationContext,
    key: syn.Expr,
    _colon,
    bound: syn.Expr,
    _assign,
    value: syn.Expr,
):
    return Tuple.Element(key=key, bound=bound, value=value)
