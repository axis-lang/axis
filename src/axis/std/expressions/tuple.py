from multiprocessing import Value
from optparse import Option
from token import OP
from typing import Optional
from protobase import cached_property
from axis.core import syn, log
#from .etc import Etc
from .sym import Sym

#[..1..4..]
class Tuple(syn.Expr):
    """
    Represents a tuple expression in the AST.
    It can contain elements that are:
    - Values (e.g. `1`, `2`, `3`)
    - Named elements (e.g. `a: b`, `c = d`, `e: f = g`)
    - Spread elements (e.g. `..alpha..`, `..`)

    """
    class Element(syn.Node, abstract=True):
        ...

    class ValueElement(Element):
        'value'
        value: Optional[syn.Expr]

    class SpreadElement(Element):
        '..spread..'

        etc: Optional[syn.Expr]

    class NamedElement(syn.Node):
        'name: bound = value'
        name: str
        bound: Optional[syn.Expr]
        value: Optional[syn.Expr]

    class KeyElement(syn.Node):
        '<a .. b>'
        key: syn.Expr
        value: syn.Expr

    elements: tuple[Element, ...]

    @cached_property
    def spread_positions(self) -> tuple[int, ...]:
        return tuple(i for i, e in enumerate(self.elements) if isinstance(e, self.SpreadElement))
    
    @cached_property # TODO: cached property can retain the raised error and rethrow it on subsequent calls
    def head_and_tail_count(self) -> tuple[int, int]:
        """
        Returns a tuple of (head_count, spread_count, tail_count).
        - head_count: Number of elements before the first spread element.
        - spread_count: Number of spread elements.
        - tail_count: Number of elements after the last spread element.
        """
        spread_positions = self.spread_positions
        if len(spread_positions) == 0:
            return len(self.elements), 0
        
        if len(spread_positions) > 1:
            with log.error(f"Tuple has {len(spread_positions)} spread positions, only one expected") as err:
                for pos in spread_positions:
                    err.with_label(self.elements[pos], f"Spread element at position {pos}")
            raise ValueError("Tuple has multiple spread positions")
        
        head_count = spread_positions[0]
        tail_count = len(self.elements) - head_count - 1
        return head_count, tail_count
    
    def head_rest_and_tail_elemets(self, head_count: int, tail_count: int = 0) -> tuple[tuple[Element, ...], tuple[Element, ...], tuple[Element, ...]]:
        """
        Returns a tuple of (head_elements, rest_elements, tail_elements).
        - head_elements: Elements before the first spread element.
        - tail_elements: Elements after the last spread element.
        - rest_elements: Elements in between, including the spread element if present.
        """
        if head_count < 0 or tail_count < 0:
            raise ValueError("Head and tail counts must be non-negative")
        
        if head_count + tail_count > len(self.elements):
            raise ValueError("Head and tail counts exceed total number of elements")
        
        head_elements = self.elements[:head_count]
        tail_elements = self.elements[-tail_count:] if tail_count > 0 else ()
        rest_elements = self.elements[head_count:len(self.elements) - tail_count] if tail_count > 0 else self.elements[head_count:]
        
        return head_elements, rest_elements, tail_elements
        
        
@syn.AstBuilder.build.register
def build_tuple_ast(
    self,
    ctx: syn.AxisParser.TupleContext | syn.AxisParser.ShapeContext,
    *elements: tuple[Tuple.Element, ...],
) -> Tuple:
    return Tuple(elements=elements)

@syn.AstBuilder.build.register(syn.AxisParser.ValueElementContext)
def build_value_element_ast(
    self, 
    _: syn.AxisParser.ValueElementContext, 
    value: syn.Expr,
):
    return Tuple.ValueElement(value=value)


@syn.AstBuilder.build.register(syn.AxisParser.SpreadElementContext)
def build_spread_element_ast(
    self, 
    _: syn.AxisParser.SpreadElementContext,
    ellipsis: str,
    etc: syn.Expr,
):
    assert ellipsis == '..', "Expected '..' for spread element"
    return Tuple.SpreadElement(etc=etc)


@syn.AstBuilder.build.register(syn.AxisParser.NamedElementContext)
def build_named_element_ast(
    self, 
    _: syn.AxisParser.NamedElementContext, 
    name: str,
    op1: Optional[str] = None,
    e1: Optional[syn.Expr] = None,
    op2: Optional[str] = None,
    e2: Optional[syn.Expr] = None,
):
    if op1 == ':':
        if op2 is None:
            return Tuple.NamedElement(name=name, bound=e1, value=None)
        assert op2 == '=', "Expected '=' after ':' in named element"
        return Tuple.NamedElement(name=name, bound=e1, value=e2)
        
    assert op1 == '=', "Expected '=' before named element"
    assert op2 is None, "Expected no operator after '=' in named element"
    return Tuple.NamedElement(name=name, bound=None, value=e1)

@syn.Matcher.match.register(Tuple)
def match_tuple(self: syn.Matcher, tuple: Tuple, value: syn.Expr):

    if not isinstance(value, Tuple):
        raise syn.StopUnification
    
    try:
        head_and_tail_count = tuple.head_and_tail_count

        value_head, value_rest, value_tail = value.head_rest_and_tail_elemets(*head_and_tail_count)
        target_head, target_rest, target_tail = tuple.head_rest_and_tail_elemets(*head_and_tail_count)

    except: 
        raise syn.StopUnification
    

    for a, b in zip(target_head, value_head):
        print(f"Matching tuple {a} with value {b}")

        self.match_node(a, b)

    for a, b in zip(target_tail, value_tail):
        self.match_node(a, b)

    if len(target_rest) == 1:
        target_spread = target_rest[0]
        assert isinstance(target_spread, Tuple.SpreadElement), "Expected a spread element in the rest of the tuple"

        if isinstance(target_spread.etc, Sym) and target_spread.etc.is_wildcard:
            self.capture(target_spread.etc.name, value.with_attrs(elements=value_rest))


    
    
        
    

    
   

    