from __future__ import annotations
from decimal import Decimal
from operator import is_
from typing import ClassVar, Iterable, Optional, Self
from warnings import warn
from protobase import Record, attrs_of, mutate, Type
from rich.tree import Tree
from rich.text import Text
from textwrap import shorten, fill
from axis.core import src, log
from .building import AstBuilder

class Node(Record, frozen=True, abstract=True):
    __slots__ = ('__weakref__',)
    grammar_context_infix: ClassVar[str] = 'Node'

    @staticmethod
    def __class_build__(proto: Type.Builder):
        is_abstract = proto.data('abstract')
        
        if is_abstract:
            return

        @proto.postbuild
        def postbuild(cls: 'Node'):            
            from axis.core.syn.grammar import AxisParser
            ctx_name = f'{proto.name}{cls.grammar_context_infix}Context'
            ctx_class = getattr(AxisParser, ctx_name, None)
            if ctx_class is None:
                return warn(f'Grammar rule not found for {proto.name} ({ctx_name})')

            print(f'Binding {cls.__qualname__}.build() to {ctx_name}')
            @AstBuilder.build.register(ctx_class)
            def build(ast_builder, ctx, *args, **kwargs):
                return cls.build(*args, **kwargs)
       

    def __rich__(self):

        OP_STYLE = 'yellow'
        ATTR_STYLE = 'cyan'
        TYPE_STYLE = 'green'
        VALUE_STYLE = 'italic bright_black'

        label = Text(no_wrap=False)
        label.append(type(self).__qualname__, style=TYPE_STYLE)
        label.append(' = ', style=OP_STYLE)
        #label.append(shorten(str(self), 50), style=VALUE_STYLE)
        label.append(str(self), style=VALUE_STYLE)

        tree = Tree(label, guide_style=TYPE_STYLE)

        # primero los valores simples
        # luego los nodos
        # finalmente contenedores

        for attr, value in reversed(attrs_of(self).items()):
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

    def with_span_of(self, node: Node) -> Self:
        src.tag_span_from(node, self)
        return self

    def with_attrs(self, **kwargs) -> Self:
        result = mutate(self, **kwargs)
        src.tag_span_from(self, result)
        return result

    @property
    def span(self) -> src.Span | None:
        return src.Span.of(self)

    @property
    def as_label(self, *args, **kwargs) -> Self:
        return log.Label(self.span, *args, **kwargs)

    @classmethod
    def build(self, *args, **kwargs) -> Self:
        """
        Cada subclase no abstracta de node debe implementar este método.
        se vinculara directamente con el contexto en la gramatica a traves del nombre
        subclases de Expr, Item o Block tendran 
        """
        raise NotImplementedError(f'No build() method for {self.__qualname__}')