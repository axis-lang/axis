#%%
from axis.core import syn, src, sem, ref
from axis import std
from rich import print


ol = std.Unit.build_ouline_spec()
file = src.File.from_path("codebase/std-core.tests.src/test.ax")

# Parsing step
units = [ol.parse_outline(file)]

def gen_content_manifest_entries():
    for unit in units:
        yield from unit.generate_content_manifest_entries(ref.Ref.root)

for ref, it  in gen_content_manifest_entries():
    print(str(ref))

# # Discover step
# root_binding = sem.Binder(None, std.Sym.ROOT)
# for unit in units:
#     root_binding.discover(unit) # para cada source unit del codebase
# """
# Primera pasada de discovery, construye la tabla de simbolos (exports) con los elementos presentes en 
# todas las unidades del codebase. la tabla de simbolos es un es un indice de referencias que despues
# sera consultado para construir los contextos en la fase de binding. la tabla de simbolos es un indice 
# de items (no de entidades).
# """


# # procesa los imports y exports
# #print(root_binding)


# # Step 4 binding
# """
# una vez tenemos los imports y exports podemos resolverlos para disgregar los items
# """

# #################################################

# # Step 5 reintegracion de items


# # %%
# from protobase import Object

# #{..}


# unify_fn = syn.Match.from_expr("$a + $b")


# result = unify_fn('1 + 2')


# # %%
