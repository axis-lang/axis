"""Concrete syntax tree"""

from __future__ import annotations
from ast import TypeAlias
from typing import Optional
from protobase import Object, traits


class EntityDefinition(Object, traits.Basic):
    """
    fn
    """

    meta_parameters: Optional[list[Parameter]]


class Module(EntityDefinition):
    id: tuple[str]

    entities: list[EntityDefinition]


class Parameter(Object, traits.Basic):
    "Base for generics and function params"

    name: str
    bound: Optional[ExprNode]
    default: Optional[ExprNode]
    doc: Optional[str]
    # extra: list[]


class SuiteNode(Object, traits.Basic): ...


class ExprNode(Object, traits.Basic): ...


class FunctionDef(EntityDefinition):
    entity_name: str
