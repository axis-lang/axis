#%%
'''
ref es parte del RSVDG?
'''

from __future__ import annotations
from pathlib import Path
from typing import ClassVar, Optional
from protobase import Record


class Ref(Record, consed=True, abstract=True):
    ROOT: ClassVar[Root]
    parent: Optional[Ref]

    # value protocol

    def member(self, name: str) -> Child:
        return Child(self, name)
    

class Root(Ref):
    parent: None = None

ROOT = Ref.ROOT = Root(None)



class Child(Ref):
    'parent.memeber'
    name: str


class Index(Ref):
    "parent[..indice]"
    #indice: Tuple


class Call(Ref):
    "parent(..argument)"
    #argument: Tuple


class Param(Ref):
    name: str


class Hiperparam(Ref):
    name: str


class Codebase(Ref):
    path: Path

    @property
    def parts(self) -> str:
        return tuple(self.path.name.split(".")[:-1])

    def mod(self, path: Path) -> Unit:
        return Unit(parent=self, path=path)

    def __str__(self):
        return "::".join(self.parts)

    def __repr__(self):
        return f"ref.Codebase({str(self)})"

    def __rich__(self):
        return f"[blue]{str(self)}[/]"


class Unit(Ref):
    parent: Codebase
    path: Path

    @property
    def rel_path(self):
        return self.path.relative_to(self.parent.path)

    def __repr__(self):
        return f"ref.Mod({self.rel_path})"
