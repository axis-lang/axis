from __future__ import annotations
from typing import Optional
from protobase import Record

from .astnode import Node
from .expr import Expr


class Entity(Node):
    type Path = tuple[str]

    path: Path
    namespace: dict[str, Item] = {}
    children: list[Entity] = []

    @property
    def name(self) -> str:
        return self.path[-1]

class Item(Node):
    'Represents a non entity node'
    children: list[Node] = []

class Doc(Item):
    'Represents a documentation block'


class Namespace(Item): 
    "Represents a 'namespace:' block"
    values: list[Val]

class Val(Entity):
    "Represents a 'val name: bound = value' entity"
    bound: Expr
    value: Expr

class Where(Item): 
    "Represents a 'where:' block"
    class Val(Val):
        'A where value'

class Use(Item):
    "Represents a 'use {..}' block"
 
class Mod(Entity):
    "Represents a 'mod' entity"

class Def(Entity):
    "Represents a 'def' entity"



class Fn(Entity):
    "Represents a 'fn' entity"

    class Takes(Item):
        'Represents a "takes" block'

    class Returns(Item):
        'Represents a "returns" block'

    class Suite(Item):
        'Represents a "returns" block'

    takes: Takes
    returns: Returns
    suite: Suite