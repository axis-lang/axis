from .mod import Mod
from .unit import Unit
from .val import Val
from .def_ import Def
from .package import Package
from . import blocks

Mod.register_outline_children(Mod, must_be_indented=True)
Mod.register_outline_children(blocks.Use, must_be_indented=True)
Mod.register_outline_children(Val, must_be_indented=True)
Mod.register_outline_children(Def, must_be_indented=True)


Unit.register_outline_children(Mod, must_be_indented=False)
Unit.register_outline_children(blocks.Use, must_be_indented=False)
Unit.register_outline_children(Val, must_be_indented=False)
Unit.register_outline_children(Def, must_be_indented=False)


Def.register_outline_children(blocks.Where, must_be_indented=False)
Def.register_outline_children(blocks.Takes, must_be_indented=False)
Def.register_outline_children(blocks.Returns, must_be_indented=False)
blocks.Where.register_outline_children(Val, must_be_indented=True)
blocks.Takes.register_outline_children(Val, must_be_indented=True)
