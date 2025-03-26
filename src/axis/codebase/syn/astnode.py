from protobase import Record



class Node(Record, frozen=True):
    def __rich__(self):
        from rich.tree import Tree
        from textwrap import shorten

        tree = Tree(f"[bold][green]{type(self).__name__}[/green][/bold]: {shorten(str(self), 50)}")

        for child in self.children:
            tree.add(child)

        return tree
