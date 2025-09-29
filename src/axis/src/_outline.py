from __future__ import annotations

import re
from enum import Enum
from typing import ClassVar, Optional, Self

from protobase import Record, frozendict, Object, classproperty

from .file import File, Line
from .span import Span

EMPTY_LINE = re.compile(r"^\s*$", re.MULTILINE)


class Block(Object, abstract=True):
    keyword: ClassVar[str]
    keyword_sep: ClassVar[str] = " \t"
    child_block_types: ClassVar[dict[type[Block], Block.OutlineSpec.Identation]]

    @classmethod
    def __class_post_build__(cls):
        cls.child_block_types = {}
        if not cls.__isabstract__:
            assert (
                getattr(cls, "keyword", None) is not None
            ), f"Block {cls.__qualname__} must have a keyword"

    @classmethod
    def parse_block(cls, span: Span, children: tuple[Block, ...]) -> Self:
        raise NotImplementedError(
            f"Block {cls.__qualname__} does not implement parse_block()"
        )

    @classmethod
    def add_child_block(
        cls, child_block_class: type[Block], /, must_be_indented: Optional[bool] = False
    ):
        cls.child_block_types[child_block_class] = Block.OutlineSpec.Identation.from_bool(
            must_be_indented
        )
        return child_block_class
    
    class OutlineSpec[T: 'Block'](Record, frozen=True):
        class Identation(str, Enum):  # En block
            SAME = ""
            NEST = "(?:[ \t]+)"
            OPT = "(?:[ \t]*)"

            @classmethod
            def from_bool(cls, must_be_indented: Optional[bool]):
                if must_be_indented is None:
                    return cls.OPT
                return cls.NEST if must_be_indented else cls.SAME

        class Rule(Record, frozen=True):
            block_type: type[Block]
            child_items: tuple[type[Block], ...]
            child_pattern: re.Pattern

            def match_child(self, line: Line, pos: int = 0) -> Optional[type[Block]]:
                if len(self.child_items) == 0:
                    return None
                if m := line.match(self.child_pattern, pos):
                    assert m.lastindex is not None
                    return self.child_items[m.lastindex - 1]
                return None

        start: Rule
        rules: frozendict[type[Block], Rule]

        def parse_outline(self, file: File) -> T:
            return _parse_outline(self, file)

    @classproperty
    @classmethod
    def outline_spec(cls):
        return _build_outline_spec(cls)

def _build_outline_spec[T:Block](cls: type[T]) -> Block.OutlineSpec[T]:
    """
    Build the outline spec for this block type.
    """
    rules: dict[type[Block], Block.OutlineSpec.Rule] = {}

    def process_block(block_type: type[Block]):
        if block_type in rules:
            return

        children = {
            child_type: child_ident
            for base in reversed(block_type.__mro__)
            if issubclass(base, Block)
            for child_type, child_ident in base.child_block_types.items()
        }

        child_types: list[type[Block]] = []
        child_patterns: list[str] = []

        for child_type, child_ident in children.items():

            child_types.append(child_type)

            iden_part = child_ident.value
            kw_part = re.escape(child_type.keyword)
            sep_part = (
                f"(?:[{re.escape(child_type.keyword_sep)}])"
                if child_type.keyword_sep
                else ""
            )

            child_patterns.append(f"({iden_part}{kw_part}{sep_part})")

        rules[block_type] = Block.OutlineSpec.Rule(
            block_type=block_type,
            child_items=tuple(child_types),
            child_pattern=re.compile("|".join(child_patterns), re.MULTILINE),
        )

        for child_type in child_types:
            process_block(child_type)

    process_block(cls)

    return Block.OutlineSpec(rules[cls], frozendict(rules))


# class Outline[T: Block](Record, frozen=True):  # outline.spec
#     class Identation(str, Enum):  # En block
#         SAME = ""
#         NEST = "(?:[ \t]+)"
#         OPT = "(?:[ \t]*)"

#         @classmethod
#         def from_bool(cls, must_be_indented: Optional[bool]) -> Outline.Identation:
#             if must_be_indented is None:
#                 return cls.OPT
#             return cls.NEST if must_be_indented else cls.SAME

#     class Rule(Record, frozen=True):
#         block_type: type[Block]
#         child_items: tuple[type[Block], ...]
#         child_pattern: re.Pattern

#         def match_child(self, line: Line, pos: int = 0) -> Optional[type[Block]]:
#             if len(self.child_items) == 0:
#                 return None
#             if m := line.match(self.child_pattern, pos):
#                 assert m.lastindex is not None
#                 return self.child_items[m.lastindex - 1]
#             return None

#     start: type[T]
#     rules: frozendict[type[Block], Rule]

class StackEntry(Record):
    rule: Block.OutlineSpec.Rule
    identation: str
    content: list[Line]
    children: list[Block]

    def as_block(self):
        return self.rule.block_type.parse_block(
            Span(
                file=self.content[0].file,
                start=self.content[0].start,
                end=self.content[-1].end,
            ),
            tuple(self.children),
        )

def _parse_outline[T: Block](spec: Block.OutlineSpec[T], file: File) -> T:

    stack: list[StackEntry] = [
        StackEntry(
            rule=spec.start,
            identation="",
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

    for line in file:

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
                    StackEntry(
                        rule=spec.rules.get(child_rule_id),
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

    return stack[0].as_block()
