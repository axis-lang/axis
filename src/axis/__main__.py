# %%
from logging import root
from axis.core import syn, src, sem, val, toc
from axis import std
from axis.std import items
from rich import print

# update_codebases({
#     Path('codebase')
# })


ol = std.Unit.build_ouline_spec()
file = src.File.from_path("codebase/std-core.tests.src/test.ax")

# Parsing step
unit = ol.parse_outline(file)


class RootBinding(syn.Item.Binding):
    @property
    def ref(self):
        return val.Ref.root


root_binding = RootBinding(
    parent=None,
    item=std.items.Unit(
        path=std.expr.Sym.ROOT,
        children=(),
    ),
)

# la tabla de bindings es para cada package (por sus dependencias y definiciones propias)
bindings: dict[val.Ref, set[syn.Item.Binding]] = {}
for binding in syn.Item.Binding.generate_from(unit, parent=root_binding):
    bindings.setdefault(binding.ref, set()).add(binding)

# establece el contexto de flujo en el que hacer consultas..
for binding in bindings[val.Ref.from_expr("alpha.beta")]:
    print(binding.item.name)
    print(binding.scope)
