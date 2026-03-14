#%%
import protomorph as pm

class DummyContext(pm.ContextProto):
    pass

class DummyVarType(pm.VarType):
    pass

ctx = DummyContext()
T = pm.var(DummyVarType, ctx, 'T')

# std.MyType[T]
spec = pm.val({'T': T})
assert isinstance(spec, pm.Const)
assert isinstance(spec.__type__, pm.StructType)
print(spec.__type__.meta_attrs)

print(pm.nominal_type('std.MyType', spec)) # CRASH!
v = pm.val(pm.nominal_type('std.MyType', spec)) # Crash!
print(v) # CRASH!

