from __future__ import annotations
from decimal import Decimal
from typing import ClassVar, Iterable, Optional, Self
from protobase import Record, attrs_of, mutate, Type
from rich.tree import Tree
from rich.text import Text
from textwrap import shorten
from axis.core import src, log

class Node(Record, frozen=True, abstract=True):
    __slots__ = ('__weakref__',)
    def __rich__(self):

        OP_STYLE = 'yellow'
        ATTR_STYLE = 'cyan'
        TYPE_STYLE = 'green'
        VALUE_STYLE = 'italic bright_black'

        label = Text()
        label.append(type(self).__qualname__, style=TYPE_STYLE)
        label.append(' = ', style=OP_STYLE)
        label.append(shorten(str(self), 50), style=VALUE_STYLE)

        tree = Tree(label, guide_style=TYPE_STYLE)

        for attr, value in attrs_of(self).items():
            if value is None or value == ():
                continue

            if isinstance(value, Node):
                child = value.__rich__()
                child.label = Text()
                child.label.append(attr, style=ATTR_STYLE)
                child.label.append(': ', style=OP_STYLE)
                child.label.append(type(value).__qualname__, style=TYPE_STYLE)
                child.label.append(' = ', style=OP_STYLE)
                child.label.append(shorten(str(value), 50), style=VALUE_STYLE)
                tree.add(child)
                continue
            
            if isinstance(value, (tuple, frozenset)): # CONTAINER TYPES
                child_label = Text()
                child_label.append(attr, style=ATTR_STYLE)
                child_label.append(': ', style=OP_STYLE)
                child_label.append(type(value).__qualname__, style=TYPE_STYLE)
                child = Tree(child_label, guide_style=ATTR_STYLE)

                for item in value:
                    if isinstance(item, Node):
                        child.add(item)
                    else:
                        item_label = Text()
                        item_label.append(shorten(str(item), 50), style=VALUE_STYLE)
                        child.add(item_label)

                tree.add(child)
                continue

            attr_label = Text()
            attr_label.append(attr, style=ATTR_STYLE)
            attr_label.append(': ', style=OP_STYLE)
            attr_label.append(type(value).__qualname__, style=TYPE_STYLE)
            attr_label.append(' = ', style=OP_STYLE)
            attr_label.append(Text(shorten(str(value), 50), style=VALUE_STYLE))
            tree.add(attr_label)


        return tree

    #@@classmethod
    def with_span_of(self, node: Node) -> Self:
        #result = cls(**attrs)
        src.tag_span_from(node, self)
        return self

    def with_attrs(self, **kwargs) -> Self:
        result = mutate(self, **kwargs)
        src.tag_span_from(self, result)
        return result

    @property
    def span(self) -> src.Span | None:
        return src.Span.of(self)

    def label(self, *args, **kwargs) -> Self:
        return log.Label(self.span, *args, **kwargs)
