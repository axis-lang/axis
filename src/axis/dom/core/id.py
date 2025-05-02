"""
Antes de arrojar un error de tipado
(intentar) aplicar una transformacion (al tipo)
de una lista transformaciones ordenada por precedencia
de forma recurrente
"""

from __future__ import annotations

from itertools import chain
from pathlib import Path
from protobase import Record

class Id(Record, consed=True):
    parts: tuple[str]

    @classmethod
    def from_fs_path(cls, path: Path):
        parts = chain.from_iterable(part.split(".") for part in path.parts)
        return cls(parts=tuple(parts)[:-1])

    @property
    def codebase(self):
        return self.parts[0]

    @property
    def name(self):
        return self.parts[-1]

    @property
    def parent(self):
        return Id(parts=self.parts[:-1])

    def child(self, name: str):
        return Id(parts=self.parts + (name,))
    
    def __str__(self):
        return "::".join(self.parts)
    
