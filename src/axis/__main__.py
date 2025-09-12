# %%
from rich import print
from axis import sem, src, syn, val, expr, items

pkg = sem.Package.from_path('codebase/std-core.tests.src')

print(pkg.global_index)

