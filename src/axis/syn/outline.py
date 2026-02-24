from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Self, Sequence

from protobase import Inmutable, Record, cached_property, frozendict

from axis import src


EMPTY_LINE = re.compile(r"^\s*$", re.MULTILINE)


class OutlineTree[T](Inmutable):
    tag: T
    content: src.Span
    children: tuple[OutlineTree, ...]

    def __rich__(self):
        from textwrap import shorten

        from rich.text import Text
        from rich.tree import Tree

        OP_STYLE = "yellow"
        ATTR_STYLE = "cyan"
        TYPE_STYLE = "green"
        VALUE_STYLE = "italic bright_black"

        label = Text(no_wrap=False)
        label.append(str(self.tag), style=TYPE_STYLE)
        label.append(": ", style=OP_STYLE)
        label.append(shorten(str(self.content), 50), style=VALUE_STYLE)

        tree = Tree(label, guide_style=TYPE_STYLE)
        for child in self.children:
            tree.add(child.__rich__())
        return tree


class OutlineRule[T](Inmutable):

    class Child[CT](Inmutable):
        tag: CT
        identation: Optional[bool]
        keyword: str
        keyword_sep: str = " \t"

        @property
        def identation_part(self):
            match self.identation:
                case False:
                    return ""
                case True:
                    return "(?:[ \t]+)"
                case None:
                    return "(?:[ \t]*)"

        @property
        def kw_part(self):
            return re.escape(self.keyword)

        @property
        def sep_part(self):
            return f"(?:[{re.escape(self.keyword_sep)}])" if self.keyword_sep else ""

        @property
        def pattern(self) -> str:
            return f"({self.identation_part}{self.kw_part}{self.sep_part})"

    tag: T
    children: frozendict[str, Child[T]]

    @classmethod
    def from_children(cls, tag: T, children: Sequence[OutlineRule.Child[T]]) -> Self:
        # TODO: verify keyword uniqueness
        return cls(tag=tag, children=frozendict((child.keyword, child) for child in children))

    @cached_property
    def child_pattern(self) -> re.Pattern:
        if len(self.children) == 0:
            return re.compile(r"(?!x)x")  # never matches
        return re.compile(
            "|".join(child.pattern for child in self.children.values()), re.MULTILINE
        )

    @cached_property
    def child_tags(self) -> tuple[T, ...]:
        return tuple(child.tag for child in self.children.values())

    def match_child(self, line: src.Line, pos: int = 0) -> Optional[T]:
        if len(self.children) == 0:
            return None

        if m := line.match(self.child_pattern, pos):
            assert m.lastindex is not None, f"Pattern must have at least one group {self.child_pattern}"
            return self.child_tags[m.lastindex - 1]
        return None


class OutlineSpec[T](Inmutable):

    # @classmethod
    # def from_rules(cls, *rules: Rule[E]) -> Self:
    #     return cls(rules=frozendict((r.element, r) for r in rules))

    start: T
    rules: frozendict[T, OutlineRule[T]]

    @classmethod
    def from_rules(cls, start: T, *rules: OutlineRule[T]) -> Self:
        if len(rules) == 0:
            raise ValueError("At least one rule must be provided")

        rules_dict = frozendict((r.tag, r) for r in rules)

        return cls(start=start, rules=rules_dict)

    class StackEntry(Record):
        rule: OutlineRule
        identation: str = ""
        content: list[src.Line] = []
        children: list[OutlineTree] = []
        next: Optional[OutlineSpec.StackEntry] = None

        def as_tree(self):
            return OutlineTree(
                tag=self.rule.tag,
                content=src.Span(
                    file=self.content[0].file,
                    start=self.content[0].start,
                    end=self.content[-1].end,
                ),
                children=tuple(self.children),
            )

    def parse_tree(self, file: src.File) -> OutlineTree[T]:

        top_level_entry = self.StackEntry(rule=self.rules[self.start])
        current_entry = top_level_entry

        def drain_stack(up_to: OutlineSpec.StackEntry):
            nonlocal current_entry

            while current_entry is not up_to:
                tree = current_entry.as_tree()
                assert current_entry.next is not None
                current_entry = current_entry.next
                current_entry.children.append(tree)

        def reversed_stack():
            nonlocal current_entry
            entry = current_entry
            while entry is not None:
                yield entry
                entry = entry.next

        for line in file:

            if line.match(EMPTY_LINE, full=True):
                current_entry.content.append(line)
                continue

            line_matched = False

            for entry in reversed_stack():
                #print("TRY", line, entry.rule.tag, repr(entry.identation), repr(line.content))

                if not line.startswith(entry.identation):
                    continue

                if child_tag := entry.rule.match_child(line, len(entry.identation)):
                    line_matched = True
                    drain_stack(entry)
                    current_entry = OutlineSpec.StackEntry(
                        rule=self.rules[child_tag],
                        identation=line.identation,
                        content=[line],
                        children=[],
                        next=current_entry,
                    )
                    break

            if not line_matched:
                if not line.startswith(current_entry.identation):
                    print(f"BAD IDENTATION ON '{line}'")
                    continue

                current_entry.content.append(line)

        drain_stack(top_level_entry)

        return current_entry.as_tree()


# if __name__ == "__main__":
#     from rich import print

    #     class Elem(Inmutable):
#         keyword: str
#         keyword_sep: str = " \t"

#     mod = Elem("mod")
#     doc = Elem("---", "")
#     def_ = Elem("def")
#     val = Elem("val")
#     where = Elem("where", ": \t")

#     outline = OutlineSpec.from_rules(
#         OutlineSpec.Rule(
#             mod,
#             frozendict(
#                 {
#                     doc: OutlineSpec.Identation.OPT,
#                     def_: OutlineSpec.Identation.SAME,
#                     val: OutlineSpec.Identation.SAME,
#                 }
#             ),
#         ),
#         OutlineSpec.Rule(
#             def_,
#             frozendict(
#                 {
#                     doc: OutlineSpec.Identation.OPT,
#                     where: OutlineSpec.Identation.SAME,
#                 }
#             ),
#         ),
#         OutlineSpec.Rule(
#             where,
#             frozendict(
#                 {
#                     val: OutlineSpec.Identation.NEST,
#                 }
#             ),
#         ),
#         OutlineSpec.Rule(val, frozendict({})),
#         OutlineSpec.Rule(doc, frozendict({})),
#     )

#     file = src.File.from_buffer(
#         Path("test.txt"),
#         """
#         mod alpha
#             -----
#             alpha documentation

#         def foo
#             --- 
#             foo documentation
#         where:
#             val alpha: Natural = 42

#         def bar
#             --- 
#             bar documentation
#         where:
#             val beta: Natural = 42
#         """,
#     )

#     print(outline.parse_tree(mod, file))
