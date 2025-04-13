from decimal import Decimal
from protobase import Record, attrs_of

class Node(Record, frozen=True, abstract=True):
    def __rich__(self):
        from rich.tree import Tree
        from textwrap import shorten

        tree = Tree(f"{type(self).__name__}", style="bold green")

        for attr, info in attrs_of(type(self)).items():
            value = getattr(self, attr)

            # leaf
            if isinstance(value, str): # LEAF TYPES
                tree.add(f"[bold][blue]{attr}[/blue][/bold]: [red]{shorten(value, 50)}[/red]")

            elif isinstance(value, (int, Decimal, float, bool)):
                tree.add(f"[bold][blue]{attr}[/blue][/bold]: [red]{value}[/red]")

            elif value is Ellipsis:
                tree.add(f"[bold][blue]{attr}[/blue][/bold]: [red]..[/red]")


            # container
            elif isinstance(value, (tuple, frozenset)):
                child = Tree(f"[bold][blue]{attr}[/blue][/bold]: {type(value).__name__}")
                for item in value:
                    if isinstance(item, Node):
                        child.add(item)
                tree.add(child)

            # node
            elif isinstance(value, Node):
                child = value.__rich__()
                child.label = f"[bold][blue]{attr}[/blue][/bold]: {child.label}"
                tree.add(child)

        return tree

class Statement(Node, abstract=True): 
    ...

class Expr(Statement, abstract=True): 
    ...

class Block(Node, abstract=True):
    children: tuple[Node]

class Item(Block, abstract=True):
    ...

class Err(Node, abstract=True):
    ...

class UnexpectedErr(Node):
    unexpected: str
