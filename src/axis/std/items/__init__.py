from .mod import Mod
from .unit import Unit
from .use import Use
from .val import Val
from .def_ import Def


Mod.add_child_block(Mod, must_be_indented=True)
Mod.add_child_block(Use, must_be_indented=True)
Mod.add_child_block(Val, must_be_indented=True)
Mod.add_child_block(Def, must_be_indented=True)

Unit.add_child_block(Mod, must_be_indented=False)
Unit.add_child_block(Use, must_be_indented=False)
Unit.add_child_block(Val, must_be_indented=False)
Unit.add_child_block(Def, must_be_indented=False)
