#%%
from functools import singledispatchmethod
from types import NoneType
from typing import Any, ClassVar
from axis.core import syn, src, sem
from axis import std
from rich import print
from protobase import frozendict

ol = std.Unit.build_ouline_spec()
file = src.File.from_path("codebase/std-core.tests.src/test.ax")
unit = ol.parse_outline(file)


scoping = sem.ScopingPass(None, std.Sym.ROOT)
scoping.process_item(unit)


# %%
from protobase import Object

#{..}

unify_fn = syn.Match.expr("$a + $b")


result = unify_fn('1 + 2')


# %%
