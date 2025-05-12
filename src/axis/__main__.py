#%%
from axis.core import syn, src
from axis import std
from rich import print


ol = std.Unit.build_ouline_spec()
file = src.File.from_path("codebase/std-core.tests.src/test.ax")
unit = ol.parse_outline(file)

print(unit)


# %%
