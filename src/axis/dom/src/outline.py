from __future__ import annotations

import re
from enum import Enum
from typing import Callable, Optional, Self

from protobase import MISSING, MissingType, Record, frozendict

from .file import File, Line
from .span import Span

DEFAULT_KEYWORD_SEPARATOR = " :\t"
EMPTY_LINE = re.compile(r"^\s*$", re.MULTILINE)


class Outline[T](Record, frozen=True):
    class Identation(str, Enum):
        SAME = "|"
        NEST = ">"
        OPT = "|>"

    class Child[T](Record, frozen=True):
        type: T
        identation: Outline.Identation

    class Spec[T](Record, frozen=True):
        type: T
        keyword: str
        children: tuple[Outline.Child[T], ...]
        separators: str = DEFAULT_KEYWORD_SEPARATOR

    class Rule[T](Record, frozen=True):
        type: T
        child_items: tuple[T]
        child_pattern: re.Pattern

        def match_child(self, line: Line, pos: int = 0) -> Optional[T]:
            if len(self.child_items) == 0:
                return None
            if m := line.match(self.child_pattern, pos):
                return self.child_items[m.lastindex - 1]
            return None

    rules: frozendict[T, Rule[T]]

    @classmethod
    def build(cls, *args: Spec[T]) -> Outline[T]:
        specs = {spec.type: spec for spec in args}

        identation_regexes = {
            Outline.Identation.SAME: "",
            Outline.Identation.NEST: "(?:[ \t]+)",
            Outline.Identation.OPT: "(?:[ \t]*)",
        }

        def build_rule(spec: Outline.Spec[T]) -> Outline.Rule[T]:
            child_patterns = []
            child_items = []

            for child in spec.children:
                child_spec = specs[child.type]
                child_items.append(child_spec.type)

                iden_part = identation_regexes[child.identation]
                kw_part = re.escape(child_spec.keyword)
                sep_part = (
                    f"(?:[{re.escape(child_spec.separators)}])"
                    #f"[{escape(child_spec.separators)}]"
                    if child_spec.separators
                    else ""
                )

                child_patterns.append(f"({iden_part}{kw_part}{sep_part})")

            return Outline.Rule(
                type=spec.type,
                child_items=tuple(child_items),
                #child_pattern=re.compile("^" + "|".join(child_patterns), re.MULTILINE),
                child_pattern=re.compile("|".join(child_patterns), re.MULTILINE),
            )

        return cls(frozendict({spec.type: build_rule(spec) for spec in specs.values()}))

    class Tree(Record, frozen=True):
        rule: Outline.Rule
        span: Span
        children: tuple[Self, ...]


        @property
        def type(self) -> str:
            return self.rule.type

        @property
        def content(self) -> str:
            return self.span.content

        def __rich__(self):
            from textwrap import shorten

            from rich.tree import Tree

            tree = Tree(
                f"[bold][green]{self.rule.type}[/green][/bold]: {shorten(self.content, 50)}"
            )
            for child in self.children:
                tree.add(child)

            return tree

        def transform[T](
            self,
            fn: Callable[[Self, tuple[T]], T | MissingType],
        ) -> T | MissingType:

            children = tuple(
                child_value
                for child_block in self.children
                if (child_value := child_block.transform(fn)) is not MISSING
            )

            try:
                return fn(self, children)
            except Exception as e:
                e.add_note(
                    f"Error processing block of type {self.rule.type} with content:\n{self.span.content}"
                )
                raise

    class StackEntry[T](Record):
        rule: Outline.Rule[T]
        identation: str
        content: list[Line]
        children: list[Outline.Tree]

        def as_tree(self):
            first_line, last_line = self.content[0], self.content[-1]
            return Outline.Tree(
                rule=self.rule,
                span=Span(
                    file=first_line.file,
                    start=first_line.start,
                    end=last_line.end,
                ),
                children=tuple(self.children),
            )

    def parse_tree(
        self,
        rule_id: T,
        file: File, # File deberia ser un Buffer
    ) -> Tree[T]:

        stack: list[Outline.StackEntry] = [
            self.StackEntry(
                rule=self.rules.get(rule_id),
                identation="",
                content=[],
                children=[],
            )
        ]

        def drain_stack(idx: int = 0):
            while len(stack) > (idx + 1):
                block = stack.pop().as_tree()
                stack[-1].children.append(block)

        def reversed_stack():
            offset = len(stack) - 1
            while offset >= 0:
                yield offset, stack[offset]
                offset -= 1

        for line in file:
            line.line_no == 20 and print(line.content)

            if line.fullmatch(EMPTY_LINE):
                stack[-1].content.append(line)
                continue

            line_matched = False

            for level, entry in reversed_stack():

                if not line.startswith(entry.identation):
                    continue

                if child_rule_id := entry.rule.match_child(line, len(entry.identation)):
                    line_matched = True
                    drain_stack(level)
                    stack.append(
                        self.StackEntry(
                            rule=self.rules.get(child_rule_id),
                            identation=line.identation,
                            content=[line],
                            children=[],
                        )
                    )
                    break

            if not line_matched:
                if not line.startswith(stack[-1].identation):
                    print(f"BAD IDENTATION ON '{line}'")
                    continue

                stack[-1].content.append(line)

        drain_stack(0)

        return stack[0].as_tree()
