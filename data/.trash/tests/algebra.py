#%%
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import TypeAlias
from rich import print
import lark
from decimal import Decimal
from protobase import Object, Metadata, attrs_of
from protobase.collections import Tuple

class Location(Metadata):
    line: int
    column: int

    def __str__(self):
        return f"{self.line}:{self.column}"

class BinaryOperator(str, Enum):
    ADD = '+'
    SUB = '-'
    


class AST(Object): 
    # def __rich__(self, parent: Optional[AST] = None):
    #     from rich.tree import Tree
    #     content = type(self).__name__

    #     Tree = parent.add if parent else Tree

    #     tree = Tree(f'[bold]{content}[/bold]')

    #     for field in attrs_of(type(self)).values():
    #         value = getattr(self, field.name)
    #         if isinstance(value, AST):
    #             value.__rich__(tree)
    #         elif isinstance(value, list):
    #             rich_list(tree, value)
    #         else:
    #             tree.add(f'{field.name}: {value}')

    #     return tree
    ...
        

class Id(AST):
    symbol: str
 

class MemberAccess(AST):
    of: AST
    member: list[str]

class BinaryOperation(AST):
    l: Node
    r: Node
    op: BinaryOperator

class Add(Object, AST):
    l: Node
    r: Node

    def __str__(self):
        return f"{self.l} + {self.r}"


class Sub(Object, AST):
    l: Node
    r: Node

    def __str__(self):
        return f"{self.l} - {self.r}"


class Mul(Object, AST):
    l: Node
    r: Node

    def __str__(self):
        l = f"({self.l})" if isinstance(self.l, (Add, Sub)) else str(self.l)
        r = f"({self.r})" if isinstance(self.r, (Add, Sub)) else str(self.r)
        return f"{l} * {r}"


class Div(Object, AST):
    l: Node
    r: Node

    def __str__(self):
        l = f"({self.l})" if isinstance(self.l, (Add, Sub)) else str(self.l)
        r = f"({self.r})" if isinstance(self.r, (Add, Sub)) else str(self.r)
        return f"{l} / {r}"


class Neg(Object, AST):
    r: Node

    def __str__(self):
        return f"-{self.r}"


class Suite(AST):
    statements: list[AST]

class Composition(AST):
    items: list[Node]


Node: TypeAlias = float | str | Neg | Add | Sub | Mul | Div


class Algebra:
    class SyntaxTreeBuilder(lark.Transformer):
        """Builds a syntax tree from a Lark parse tree."""

        # identifiers
        def id(self, children):
            return Id(children[0].value)

        def binary_operator(self, children):
            return BinaryOperator(children[0].value)

        # literals
        def nat(self, children):
            return Decimal(children[0].value)

        # containers
        def parens(self, children) -> Node:
            return children[0]
        
        def addition(self, children) -> Node:
            l, *ops = children

            for op, term in zip(ops[::2], ops[1::2]):
                l = BinaryOperation(l, term, BinaryOperator(op.value))

            return l

        def member(self, children) -> Node:
            l, r = children
            if isinstance(l, MemberAccess):
                l.members.append(r.value)
                return l
            
            return MemberAccess(l, [r.value])

        def suite(self, children) -> Node:
            return Suite(children)

        def composed(self, children) -> Node:
            l, r = children
            if isinstance(l, Composition):
                l.items.append(r)
                return l
            
            return Composition(items=[l, r])

        def tuple_entry(self, children):
            return tuple(children)

        def tuple(self, children):
            return Tuple(children)

        # operators
        # add = Add.builder()
        # sub = Sub.builder()
        # mul = Mul.builder()
        # div = Div.builder()
        # neg = Neg.builder()

    def __init__(self):
        with (Path(__file__).parent / "axis.lark").open() as grammar_file:
            self.lark = lark.Lark(
                grammar_file,
                #start="expr",
                strict=True,
                parser="lalr",
                #parser="cyk",
                #ambiguity='explicit',
                #transformer=self.SyntaxTreeBuilder(),
                # import_paths=[str(path) for path in self.GRAMMAR_IMPORT_PATHS],
            )

    def parse(self, text: str) -> Node:
        return self.lark.parse(text)

expr = Algebra().parse

print(expr("var a = 7"))



