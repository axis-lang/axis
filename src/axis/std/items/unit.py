from typing import ClassVar
from .mod import Mod

class Unit(Mod):
    """
    """
    keyword: ClassVar =  "unit"
    grammar: ClassVar = "unit: 'unit' expression ':' EOF;"
