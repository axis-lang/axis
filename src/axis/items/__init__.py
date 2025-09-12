from .mod import Mod
from .unit import Unit
from .val import Val
from .def_ import Def
from axis import blocks

Mod.add_child_block(Mod, must_be_indented=True)
Mod.add_child_block(blocks.Use, must_be_indented=True)
Mod.add_child_block(Val, must_be_indented=True)
Mod.add_child_block(Def, must_be_indented=True)


Unit.add_child_block(Mod, must_be_indented=False)
Unit.add_child_block(blocks.Use, must_be_indented=False)
Unit.add_child_block(Val, must_be_indented=False)
Unit.add_child_block(Def, must_be_indented=False)


Def.add_child_block(blocks.Where, must_be_indented=False)
Def.add_child_block(blocks.Takes, must_be_indented=False)
Def.add_child_block(blocks.Returns, must_be_indented=False)
blocks.Where.add_child_block(Val, must_be_indented=True)
blocks.Takes.add_child_block(Val, must_be_indented=True)
