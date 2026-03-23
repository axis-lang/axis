#%%
from protomorph.core import *
from protomorph.core.native import meta_from_native

a = Integer.wrap(1)
b = Integer.wrap(3)


t = Tuple.of(a, b)

tt = Tuple.of(Integer, t, t)

print(tt)

# %%
