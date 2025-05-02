from typing import Optional
from .abstract import Block, Statement, Expr

class Doc(Block):
    '''

    '''
    content: str

    def __str__(self):
        return self.content
    
    

class Uses(Block):
    '''
    uses std.core(
        io(
            print,
            println,
            _
        ),
        math(
            sin,
            cos,
            tan
        )
    ) = dep('axis-core')
    '''
    expr: Expr


class Takes(Block): 
    '''
    takes [overload_name]:
        val x: N
        val y: N
    '''
    id: Optional[str]
    


class Where(Block):
    '''
    where:
        val N: Number
    '''


class Returns(Block):
    '''

    '''
    expr: Expr

class Suite(Block):
    '''
    suite:
        
        
    '''

    statements: tuple[Statement, ...]


# class Item(Block, abstract=True):
#     @property
#     def name(self) -> str:
#         raise NotImplementedError(f"Item {type(self)} has no name")


#     @property
#     def if_first_order(self):
#         return True

#     def members(self) -> Iterable[Item]:
#         return ()

#     def where_values(self) -> Iterable[Val]:
#         for where in self.iter_children(Where):
#             for val in where.iter_children(Val):
#                 yield val

#     def take_values(self) -> Iterable[Val]:
#         for where in self.iter_children(Takes):
#             for val in where.iter_children(Val):
#                 yield val


# class Mod(Item):
#     def members(self):
#         for child in self.children:
#             if isinstance(child, Item):
#                 yield child


# class Val(Item):
#     expr: Expr
#     bound: Optional[Expr]
#     value: Optional[Expr]

#     # puede tener multiples nombres :S


# class Def(Item):
#     """
#     Represents a 'def' entity:

#     def Vector(..)
#     takes:
#         val x: N
#         val y: N
#     where:
#         val N: Number
#     """

#     expr: Expr

#     class Kind(str, Enum):
#         CLASS = "class"

#     @property
#     def name(self) -> str:
#         if isinstance(self.expr, str):
#             return self.expr
#         if isinstance(self.expr, Call) and isinstance(self.expr.function, str):
#             return self.expr.function

#     @property
#     def if_first_order(self) -> bool:
#         # tambien si la expresion es diferente de str?
#         return not any(isinstance(child, (Takes, Where)) for child in self.children)