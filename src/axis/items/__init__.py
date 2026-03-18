from .item import *
from .mod import *
from .unit import *
from .claim import *
from .defs import *
from .global_ import *
from .package import *

from . import blocks

Mod.register_outline_children(Mod, must_be_indented=True)
Mod.register_outline_children(blocks.Use, must_be_indented=True)
Mod.register_outline_children(Def, must_be_indented=True)
Mod.register_outline_children(Claim, must_be_indented=True)
Mod.register_outline_children(Val, must_be_indented=True)

Unit.register_outline_children(Mod, must_be_indented=False)
Unit.register_outline_children(blocks.Use, must_be_indented=False)
Unit.register_outline_children(Def, must_be_indented=False)
Unit.register_outline_children(Claim, must_be_indented=False)
Unit.register_outline_children(Val, must_be_indented=False)
