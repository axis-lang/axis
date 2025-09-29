from typing import ClassVar
from .mod import Mod

class Unit(Mod, frozen=True):
    outline_keyword: ClassVar[str] = "unit"
