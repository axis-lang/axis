#%%
from axis.core import syn, src, sem, val, toc
from axis import std
from rich import print


ol = std.Unit.build_ouline_spec()
file = src.File.from_path("codebase/std-core.tests.src/test.ax")

# Parsing step
unit = ol.parse_outline(file)

# root binding
root_binding = sem.Binding(
    parent=None,
    ref=val.Ref.root,
    item=None, # sera el elemento que defina dependencias del codebase
)
for binding in sem.Binding.generate_from(unit, parent=root_binding):
    print(binding.ref)
