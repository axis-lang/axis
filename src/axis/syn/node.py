from __future__ import annotations
from typing import Any, Callable, ClassVar, Protocol, Self

import protomorph as pm

from protobase import Inmutable

from .outline import EmbeddedOutlineNode, FromOutlineNodeMixin, SegregatedOutlineNode


class Node(FromOutlineNodeMixin, abstract=True):
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


class Statement(Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Statement"
    grammar_parser_name: ClassVar[str] = "statement"


class SymLike(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def at(self) -> str | None: ...


class ScopeLike(Protocol):
    def lookup(self, sym: SymLike, *, origin: Node) -> pm.Val: ...


class BoundLoweringError(Exception):
    pass


class Expr(Statement, abstract=True):
    grammar_context_infix: ClassVar[str] = "Expr"
    grammar_parser_name: ClassVar[str] = "expr"

    def to_bound(self, scope: ScopeLike) -> pm.Val | None:
        _ = scope
        raise BoundLoweringError(
            f"unsupported bound expression: {type(self).__qualname__}"
        )

    def to_anchor(self, scope_ref: pm.Anchor | None) -> pm.Anchor:
        _ = scope_ref
        from axis import log

        log.error("Unsupported anchor expression").label(self).throw()


class Block(EmbeddedOutlineNode, Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Block"


class Item(Node, abstract=True):
    grammar_context_infix: ClassVar[str] = "Item"


class SegregatedItem[P: FromOutlineNodeMixin](
    Item, SegregatedOutlineNode[P], abstract=True
):
    pass


class EmbeddedItem(Item, EmbeddedOutlineNode, abstract=True):
    pass


class MatchSpec(Inmutable):
    capture_name: str | None = None
    match_all: bool = False
    filter_any: frozenset[str] = frozenset()


class SyntaxError(Node): ...
