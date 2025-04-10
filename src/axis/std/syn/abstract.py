from protobase import Record, attrs_of

class Node(Record, frozen=True, abstract=True):
    def __rich__(self):
        from rich.tree import Tree
        from textwrap import shorten

        tree = Tree(f"[bold][green]{type(self).__name__}[/green][/bold]: {shorten(str(self), 50)}")

        for attr, info in attrs_of(type(self)).items():
            if isinstance(info.type, Node):
                tree.add(getattr(self, attr))
            if isinstance(info.type, tuple):
                for item in getattr(self, attr):
                    if isinstance(item, Node):
                        tree.add(item)

        return tree

class Block(Node, abstract=True):
    '''
    a block can be takes, o where
    '''
    # class Heading(Node, abstract=True):
    #     '''
    #     A block heading node
    #     '''

    # heading: Heading
    children: tuple[Node]

class Item(Block):
    '''
    a item is a def, a unit a val or a function
    '''


class Err(Node, abstract=True):
    '''
    A abstract syntactic error node
    '''
    