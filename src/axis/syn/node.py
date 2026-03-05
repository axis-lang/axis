from __future__ import annotations
from functools import cache
from typing import Any, Callable, ClassVar, Iterable, Literal, Optional, Self
from axis import src
from protobase import Inmutable, attrs_of, classproperty, frozendict, is_abstract
from rich.tree import Tree
from rich.text import Text
from textwrap import shorten
from .building import FromSrcMixin
from .outline import OutlineTree, OutlineRule, OutlineSpec


# alpha -> {}


class Node(FromSrcMixin, Inmutable, abstract=True):
    grammar_context_infix: ClassVar[str] = "Node"
    _as_registry: ClassVar[dict[type, Callable[[Any], Any]]] = {}

    @property
    def match_spec(self) -> "MatchSpec":
        return MatchSpec()

    @classmethod
    def as_impl(cls, target_type: type):
        def decorator(func: Callable[[Any], Any]):
            registry = dict(getattr(cls, "_as_registry", {}))
            registry[target_type] = func
            cls._as_registry = registry
            return func
        return decorator

    @classmethod
    def can_project(cls, target_type: type) -> bool:
        if issubclass(cls, target_type):
            return True
        for base in cls.__mro__:
            registry = getattr(base, "_as_registry", None)
            if registry and target_type in registry:
                return True
        return False

    def as_(self, target_type: type):
        if not isinstance(target_type, type):
            raise TypeError(f"Expected type for projection, got {target_type!r}")
        if isinstance(self, target_type):
            return self
        for base in type(self).__mro__:
            registry = getattr(base, "_as_registry", None)
            if registry and target_type in registry:
                return registry[target_type](self)
        return NotImplemented

    def __rich__(self):
        from axis.tui.ast_render import NodeRenderer

        return NodeRenderer().render(self)


class OutlineNode(Node, abstract=True):
    type Children = tuple[EmbeddedOutlineNode, ...]

    outline_keyword: ClassVar[str]
    outline_keyword_sep: ClassVar[str] = ": \t"
    outline_children: ClassVar[dict[type[OutlineNode], Optional[bool]]]

    @classmethod
    def __class_post_build__(cls):
        super().__class_post_build__()
        if "outline_children" not in vars(cls):  # .__dict__:
            cls.outline_children = {}
        if not is_abstract(cls):
            assert (
                getattr(cls, "outline_keyword", None) is not None
            ), f"{cls.__qualname__} must have an outline keyword"

            assert issubclass(cls, EmbeddedOutlineNode) != issubclass(
                cls, SegregatedOutlineNode
            ), f"{cls.__qualname__} must be either Embedded or Segregated"

    @classmethod
    def register_outline_children(
        cls,
        child_class: type[OutlineNode],
        /,
        must_be_indented: Optional[bool] = None,
    ):
        cls.outline_children[child_class] = must_be_indented
        return child_class

    @classproperty
    @classmethod
    @cache
    def outline_spec(cls) -> OutlineSpec[type[OutlineNode]]:
        rules: dict[type[OutlineNode], OutlineRule[type[OutlineNode]]] = {}

        def process_cls(node_cls: type[OutlineNode]):
            # debe procesar node_cls junto a todas sus subclasses, y solo agregar clases no abstractas
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
                    if issubclass(base, OutlineNode)
                    for child_cls, child_ident in base.outline_children.items()
                ],
            )

            rules[node_cls] = rule

            for child in rule.children.values():
                process_cls(child.tag)

        process_cls(cls)

        return OutlineSpec(cls, frozendict(rules))

    @classmethod
    def parse_outline_tree(cls, file: src.Source) -> OutlineTree[type[OutlineNode]]:
        return cls.outline_spec.parse_tree(file)

    @classmethod
    def from_outline(
        cls,
        tree: OutlineTree[type[OutlineNode]],
        parent: Optional[SegregatedOutlineNode] = None,
        **kwargs,
    ) -> tuple[Self, tuple[SegregatedOutlineNode, ...]]:
        assert issubclass(tree.tag, EmbeddedOutlineNode) != issubclass(
            tree.tag, SegregatedOutlineNode
        ), "Class must be either Embedded or Segregated"

        segregated_nodes = []
        embedded_children = []

        for child_tree in tree.children:

            if issubclass(child_tree.tag, EmbeddedOutlineNode):
                child, segnodes = child_tree.tag.from_outline(child_tree, **kwargs)
                embedded_children.append(child)
                segregated_nodes.extend(segnodes)

        if issubclass(tree.tag, SegregatedOutlineNode):
            self = tree.tag.from_str(
                tree.content,
                children=tuple(embedded_children),
                parent=parent,
                **kwargs,
            )
            parent = self
        elif issubclass(tree.tag, EmbeddedOutlineNode):
            self = tree.tag.from_str(
                tree.content,
                children=tuple(embedded_children),
                **kwargs,
            )
        else:
            raise TypeError("Class must be either Embedded or Segregated")

        for child_tree in tree.children:
            if issubclass(child_tree.tag, SegregatedOutlineNode):
                child, segnodes = child_tree.tag.from_outline(
                    child_tree,
                    parent=parent,
                    **kwargs,
                )
                segregated_nodes.append(child)
                segregated_nodes.extend(segnodes)

        assert isinstance(self, cls)
        return self, tuple(segregated_nodes)


class EmbeddedOutlineNode(OutlineNode, abstract=True):

    @classmethod
    def build(
        cls,
        *args,
        children: OutlineNode.Children,
        **kwargs,
    ) -> Self:
        return super().build(*args, children=children, **kwargs)


class SegregatedOutlineNode(OutlineNode, abstract=True):
    parent: Optional[OutlineNode] = None

    @classmethod
    def build(
        cls,
        *args,
        parent: Optional[OutlineNode],
        children: OutlineNode.Children,
        **kwargs,
    ) -> Self:
        return super().build(*args, parent=parent, children=children, **kwargs)

    @classmethod
    def from_file(
        cls, src_file: src.Source, **kwargs
    ) -> tuple[Self, *tuple[SegregatedOutlineNode, ...]]:
        tree = cls.parse_outline_tree(src_file)
        #from rich import print
        #print(tree)
        self, more = cls.from_outline(tree, **kwargs)
        return (self, *more)


class Statement(Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Statement"
    grammar_parser_name: ClassVar[str] = "statement"


class Expr(Statement, abstract=True):
    grammar_context_infix: ClassVar[str] = "Expr"
    grammar_parser_name: ClassVar[str] = "expr"


class Block(EmbeddedOutlineNode, Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Block"


class Item(OutlineNode, Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Item"


class SegregatedItem(Item, SegregatedOutlineNode, abstract=True):
    """"""

    # pkg:


class EmbeddedItem(Item, EmbeddedOutlineNode, abstract=True):
    """"""


class MatchSpec(Inmutable):
    capture_name: str | None = None
    match_all: bool = False
    filter_any: frozenset[str] = frozenset()


_OP_STYLE = "yellow"
_ATTR_STYLE = "cyan"
_TYPE_STYLE = "green"
_VALUE_STYLE = "italic bright_black"


def _rich_root_label(node: Node) -> Text:
    label = Text(no_wrap=False)
    label.append(type(node).__qualname__, style=_TYPE_STYLE)
    label.append(" = ", style=_OP_STYLE)
    label.append(shorten(str(node), 50), style=_VALUE_STYLE)
    return label


def _rich_attr_type_label(name: str, value: object) -> Text:
    label = Text()
    label.append(name, style=_ATTR_STYLE)
    label.append(": ", style=_OP_STYLE)
    label.append(type(value).__qualname__, style=_TYPE_STYLE)
    return label


def _rich_scalar_label(name: str, value: object) -> Text:
    label = Text()
    label.append(name, style=_ATTR_STYLE)
    label.append(": ", style=_OP_STYLE)
    label.append(type(value).__qualname__, style=_TYPE_STYLE)
    label.append(" = ", style=_OP_STYLE)
    label.append(shorten(str(value), 50), style=_VALUE_STYLE)
    return label


def _rich_item_label(value: object) -> Text:
    label = Text()
    label.append(shorten(str(value), 50), style=_VALUE_STYLE)
    return label


def _rich_named_node(name: str, node: Node) -> Tree:
    child = node.__rich__()
    child.label = Text()
    child.label.append(name, style=_ATTR_STYLE)
    child.label.append(": ", style=_OP_STYLE)
    child.label.append(type(node).__qualname__, style=_TYPE_STYLE)
    child.label.append(" = ", style=_OP_STYLE)
    child.label.append(shorten(str(node), 50), style=_VALUE_STYLE)
    return child


def _rich_value_child(name: str, value: object) -> Tree | Text:
    if isinstance(value, Node):
        return _rich_named_node(name, value)
    if isinstance(value, (dict, frozendict)):
        return _rich_mapping_tree(name, value)
    if isinstance(value, (tuple, frozenset)):
        return _rich_container_tree(name, value)
    return _rich_scalar_label(name, value)


def _rich_mapping_tree(name: str, mapping: dict | frozendict) -> Tree:
    child = Tree(_rich_attr_type_label(name, mapping), guide_style=_ATTR_STYLE)

    for index, (item_key, item_value) in enumerate(mapping.items()):
        #entry_label = Text()
        #entry_label.append(f"item[{index}]", style=_ATTR_STYLE)
        entry = Tree(Text(), guide_style=_ATTR_STYLE, hide_root=True)

        entry.add(_rich_value_child("key", item_key))
        entry.add(_rich_value_child("value", item_value))

        child.add(entry)

    return child


def _rich_container_tree(name: str, values: Iterable[object]) -> Tree:
    child = Tree(_rich_attr_type_label(name, values), guide_style=_ATTR_STYLE)

    for item in values:
        if isinstance(item, Node):
            child.add(item)
        else:
            child.add(_rich_item_label(item))

    return child

class SyntaxError(Node):
    ...