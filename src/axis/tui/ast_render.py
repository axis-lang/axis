from __future__ import annotations

from textwrap import shorten
from typing import Iterable

from protobase import attrs_of, frozendict
from rich.text import Text
from rich.tree import Tree

from axis.syn.node import Node

_OP_STYLE = "yellow"
_ATTR_STYLE = "cyan"
_TYPE_STYLE = "green"
_VALUE_STYLE = "italic bright_black"


class NodeRenderer:
    def render(self, node: Node) -> Tree:
        tree = Tree(_rich_root_label(node), guide_style=_TYPE_STYLE)

        for attr, value in attrs_of(node).items():
            if value is None or value == ():
                continue
            tree.add(_rich_value_child(attr, value))

        return tree


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
    child = NodeRenderer().render(node)
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

    for item_key, item_value in mapping.items():
        entry = Tree(Text(), guide_style=_ATTR_STYLE, hide_root=True)
        entry.add(_rich_value_child("key", item_key))
        entry.add(_rich_value_child("value", item_value))
        child.add(entry)

    return child


def _rich_container_tree(name: str, values: Iterable[object]) -> Tree:
    child = Tree(_rich_attr_type_label(name, values), guide_style=_ATTR_STYLE)

    for item in values:
        if isinstance(item, Node):
            child.add(NodeRenderer().render(item))
        else:
            child.add(_rich_item_label(item))

    return child
