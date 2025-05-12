from .mod import Mod
from .unit import Unit
from .use import Use
from .val import Val
from .def_ import Def


Mod.child_block_type(Mod, must_be_indented=True)
Mod.child_block_type(Use, must_be_indented=True)
Mod.child_block_type(Val, must_be_indented=True)
Mod.child_block_type(Def, must_be_indented=True)

Unit.child_block_type(Mod, must_be_indented=False)
Unit.child_block_type(Use, must_be_indented=False)
Unit.child_block_type(Val, must_be_indented=False)
Unit.child_block_type(Def, must_be_indented=False)
