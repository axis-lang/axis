#%%
from axis.core import syn
from axis import std
from rich import print

e = syn.Expr.parse('Array[t:0..1, m:nat, n:nat] Real')
e = syn.Expr.parse('.. Disposition[key:String, t:Slice Nat, ] ..')




print(e)