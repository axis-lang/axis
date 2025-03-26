# %%
from typing import Callable, Self
from protobase import Record, MISSING, MissingType
from .spec import Spec



class SrcBlock(Record, frozen=True):
    item_id: str
    content: str
    children: tuple[Self, ...]

    def __rich__(self):
        from rich.tree import Tree
        from textwrap import shorten

        tree = Tree(f"[bold][green]{self.item_id}[/green][/bold]: {shorten(self.content, 50)}")
        for child in self.children:
            tree.add(child)

        return tree

    def transform[T](
        self,
        fn: Callable[[Self, list[T]], T | MissingType],
    ) -> T | MissingType:

        children = [
            child_value
            for child_block in self.children
            if (child_value := child_block.transform(fn)) is not MISSING
        ]

        return fn(self, children)


class Parser(Spec):

    class StackEntry(Record):
        rule: Spec.Rule
        ident: str
        content: list[str]
        children: list[SrcBlock]

        def as_block(self):
            return SrcBlock(
                item_id=self.rule.item_id,
                content="\n".join(c[len(self.ident) :] for c in self.content),
                children=tuple(self.children),
            )

    def parse(
        self,
        item: str,
        buffer: str,
    ) -> SrcBlock:

        stack: list[Parser.StackEntry] = [
            self.StackEntry(
                rule=self.ruleset.get(item),
                ident="",
                content=[],
                children=[],
            )
        ]

        def drain_stack(idx: int = 0):
            while len(stack) > (idx + 1):
                block = stack.pop().as_block()
                stack[-1].children.append(block)

        def reversed_stack():
            offset = len(stack) - 1
            while offset >= 0:
                yield offset, stack[offset]
                offset -= 1

        for line_n, line in enumerate(buffer.splitlines()):

            line_matched = False

            for idx, entry in reversed_stack():
                if not line.startswith(entry.ident):
                    continue

                if child_rule_id := entry.rule.match_line(line[len(entry.ident) :]):
                    drain_stack(idx)

                    stack.append(
                        self.StackEntry(
                            rule=self.ruleset.get(child_rule_id),
                            ident=line[: len(line) - len(line.lstrip(" \t"))],
                            content=[line],
                            children=[],
                        )
                    )

                    line_matched = True

                    break

            if not line_matched:
                stack[-1].content.append(line)

        drain_stack(0)
        return stack[0].as_block()
