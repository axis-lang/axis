from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, Optional, Self, Sequence, cast

from protobase import (
    Inmutable,
    Record,
    cached_property,
    classproperty,
    frozendict,
    is_abstract,
)

from axis import src

from .parsing import Builder, FromStrNodeMixin


EMPTY_LINE = re.compile(r"^\s*$", re.MULTILINE)


class OutlineTree[T](Inmutable):
    tag: T
    content: src.Source.Span
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
        return cls(
            tag=tag, children=frozendict((child.keyword, child) for child in children)
        )

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

    def match_child(self, line: src.Source.Line, pos: int = 0) -> Optional[T]:
        if len(self.children) == 0:
            return None

        if m := line.match(self.child_pattern, pos):
            assert (
                m.lastindex is not None
            ), f"Pattern must have at least one group {self.child_pattern}"
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
        content: list[src.Source.Line] = []
        children: list[OutlineTree] = []
        next: Optional[OutlineSpec.StackEntry] = None

        def as_tree(self):
            return OutlineTree(
                tag=self.rule.tag,
                content=src.Source.Span(
                    source=self.content[0].source,
                    start=self.content[0].start,
                    end=self.content[-1].end,
                ),
                children=tuple(self.children),
            )

    def parse_tree(self, file: src.Source) -> OutlineTree[T]:

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
                # print("TRY", line, entry.rule.tag, repr(entry.identation), repr(line.content))

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


class FromOutlineNodeMixin(FromStrNodeMixin, abstract=True):
    type Children = tuple[EmbeddedOutlineNode, ...]

    outline_keyword: ClassVar[str]
    outline_keyword_sep: ClassVar[str] = ": \t"
    outline_children: ClassVar[dict[type[FromOutlineNodeMixin], Optional[bool]]]

    # @classmethod
    # def build(cls, *args, **kwargs) -> Self:
    #     return cast(Any, super()).build(*args, **kwargs)

    # @classmethod
    # def from_str(cls, src_span: src.Source.Span | str, **kwargs) -> Self:
    #     return cast(Any, super()).from_str(src_span, **kwargs)

    @classmethod
    def __class_post_build__(cls):
        super().__class_post_build__()
        # super_post_build = getattr(cast(Any, super()), "__class_post_build__", None)
        # if super_post_build is not None:
        #     super_post_build()
        if "outline_children" not in vars(cls):
            cls.outline_children = {}
        if is_abstract(cls):
            return

        is_embedded = issubclass(cls, EmbeddedOutlineNode)
        is_segregated = issubclass(cls, SegregatedOutlineNode)
        if not (is_embedded or is_segregated):
            return

        assert (
            getattr(cls, "outline_keyword", None) is not None
        ), f"{cls.__qualname__} must have an outline keyword"

        assert is_embedded != is_segregated, (
            f"{cls.__qualname__} must be either Embedded or Segregated"
        )

    @classmethod
    def register_outline_children(
        cls,
        child_class: type[FromOutlineNodeMixin],
        /,
        must_be_indented: Optional[bool] = None,
    ):
        cls.outline_children[child_class] = must_be_indented
        return child_class

    @classproperty
    @classmethod
    @cache
    def outline_spec(cls) -> OutlineSpec[type[FromOutlineNodeMixin]]:
        rules: dict[type[FromOutlineNodeMixin], OutlineRule[type[FromOutlineNodeMixin]]] = {}

        def process_cls(node_cls: type[FromOutlineNodeMixin]):
            if node_cls in rules:
                return

            rule = OutlineRule.from_children(
                tag=node_cls,
                children=[
                    OutlineRule.Child(
                        tag=child_cls,
                        identation=child_ident,
                        keyword=child_cls.outline_keyword,
                        keyword_sep=child_cls.outline_keyword_sep,
                    )
                    for base in reversed(node_cls.__mro__)
                    if issubclass(base, FromOutlineNodeMixin)
                    for child_cls, child_ident in base.outline_children.items()
                ],
            )

            rules[node_cls] = rule

            for child in rule.children.values():
                process_cls(child.tag)

        process_cls(cls)

        return OutlineSpec(cls, frozendict(rules))

    @classmethod
    def parse_outline_tree(cls, file: src.Source) -> OutlineTree[type[FromOutlineNodeMixin]]:
        return cls.outline_spec.parse_tree(file)

    @classmethod
    def from_outline(
        cls,
        tree: OutlineTree[type[FromOutlineNodeMixin]],
        parent: Optional[SegregatedOutlineNode] = None,
        **kwargs,
    ) -> tuple[Self | None, tuple[SegregatedOutlineNode, ...]]:
        assert issubclass(tree.tag, EmbeddedOutlineNode) != issubclass(
            tree.tag, SegregatedOutlineNode
        ), "Class must be either Embedded or Segregated"

        segregated_nodes = []
        embedded_children = []

        for child_tree in tree.children:
            if issubclass(child_tree.tag, EmbeddedOutlineNode):
                child, segnodes = child_tree.tag.from_outline(child_tree, **kwargs)
                if child is not None:
                    embedded_children.append(child)
                segregated_nodes.extend(segnodes)

        try:
            if issubclass(tree.tag, SegregatedOutlineNode):
                self = cast(Any, tree.tag).from_str(
                    tree.content,
                    children=tuple(embedded_children),
                    parent=parent,
                    **kwargs,
                )
                parent = self
            elif issubclass(tree.tag, EmbeddedOutlineNode):
                self = cast(Any, tree.tag).from_str(
                    tree.content,
                    children=tuple(embedded_children),
                    **kwargs,
                )
            else:
                raise TypeError("Class must be either Embedded or Segregated")
        except Builder.SyntaxError as e:
            e.report.emit()
            return None, ()

        for child_tree in tree.children:
            if issubclass(child_tree.tag, SegregatedOutlineNode):
                child, segnodes = cast(Any, child_tree.tag).from_outline(
                    child_tree,
                    parent=parent,
                    **kwargs,
                )
                if child is not None:
                    segregated_nodes.append(child)
                segregated_nodes.extend(segnodes)

        assert isinstance(self, cls)
        return self, tuple(segregated_nodes)


class EmbeddedOutlineNode(FromOutlineNodeMixin, abstract=True):
    @classmethod
    def build(
        cls,
        *args,
        children: FromOutlineNodeMixin.Children,
        **kwargs,
    ) -> Self:
        return super().build(*args, children=children, **kwargs)


class SegregatedOutlineNode[P: FromOutlineNodeMixin](FromOutlineNodeMixin, abstract=True):
    parent: Optional[P] = None

    @classmethod
    def build(
        cls,
        *args,
        parent: Optional[P],
        children: FromOutlineNodeMixin.Children,
        **kwargs,
    ) -> Self:
        return super().build(*args, parent=parent, children=children, **kwargs)

    @classmethod
    def from_src(
        cls,
        src_file: src.Source | str,
        **kwargs,
    ) -> tuple[Self | None, *tuple[SegregatedOutlineNode, ...]]:
        if isinstance(src_file, str):
            src_file = src.SourceBuffer.from_str(src_file)
        tree = cls.parse_outline_tree(src_file)
        self, more = cls.from_outline(tree, **kwargs)
        return (self, *more)


type OutlineChildren = tuple[EmbeddedOutlineNode, ...]
