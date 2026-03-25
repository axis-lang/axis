from __future__ import annotations

from typing import cast

from . import (
    Builtin,
    VaryingType,
    NativeType,
    Type,
    UnionType,
    LeafCarrier,
    Placeholder,
    placeholder,
    native_type,
    wrap,
)

INT_TYPE = wrap(int)
STR_TYPE = wrap(str)
FLOAT_TYPE = wrap(float)

print(VaryingType.of(INT_TYPE, STR_TYPE, FLOAT_TYPE))


class A[T](Builtin):
    elements: tuple[T, ...]
    # other : Tuple[Id, T]  # TODO: needs Tuple annotation support


class B[*T](Builtin):
    elements: tuple[int, *T, float]


# ── Generic NativeType: A[T] ───────────────────────────────

A_type = native_type(A)
print("\n=== NativeType(A) ===")
print("A_type:", A_type)
print("arity:", A_type.arity)

for i in range(A_type.arity):
    f = A_type.item_at(i)
    print(f"  field[{i}]: key={f.key}, type={f.value}")

# Specialize A[T] → A[int]
T_ph = placeholder("T")
A_int = A_type.specialize({T_ph: INT_TYPE})
print("\n=== A specialized to int ===")
print("A_int:", A_int)
for i in range(A_int.arity):
    f = A_int.item_at(i)
    print(f"  field[{i}]: key={f.key}, type={f.value}")

# ── Generic NativeType: B[*T] ─────────────────────────────

B_type = native_type(B)
print("\n=== NativeType(B) ===")
print("B_type:", B_type)
print("arity:", B_type.arity)

for i in range(B_type.arity):
    f = B_type.item_at(i)
    print(f"  field[{i}]: key={f.key}, type={f.value}")

# Specialize B[*T] → B[int, str, float]
T_star = placeholder("*T")
B_concrete = B_type.specialize({
    T_star: cast(Type, VaryingType.of(INT_TYPE, STR_TYPE, FLOAT_TYPE)),
})
print("\n=== B specialized to (int, str, float) ===")
print("B_concrete:", B_concrete)
print("arity:", B_concrete.arity)
for i in range(B_concrete.arity):
    f = B_concrete.item_at(i)
    print(f"  field[{i}]: key={f.key}, type={f.value}")

# ── Substitution example ─────────────────────────────────────

T = placeholder("T")

# VaryingType(int, <T>, str) — a heterogeneous tuple with a hole
vt = VaryingType.of(INT_TYPE, T, z=STR_TYPE)
print("\noriginal:", vt)

# Wrap in a Val for type-level traversal
vt_carrier = wrap(vt)
print("carrier:", vt_carrier)
print("is_leaf:", vt_carrier.is_leaf)

# NativeType reflects Tuple's own fields: index, values
# children[0] = index (leaf), children[1] = values (TupleCarrier)
children = list(vt_carrier)
print("top children:", children)

values_carrier = vt_carrier[1]  # the 'values' tuple
print("values carrier:", values_carrier)
print("values elements:", list(values_carrier))

# values[1] is the placeholder T, wrapped as a leaf
ph_carrier = values_carrier[1]
print("placeholder leaf:", ph_carrier, "data:", ph_carrier.fetch())

# Find it via deep_iter too
leaves = list(vt_carrier.deep_iter())
print("all leaves:", leaves)
print("placeholder in leaves:", ph_carrier in leaves)

# Substitute: replace the leaf carrying T with one carrying FLOAT_TYPE
target = ph_carrier
replacement = LeafCarrier(ph_carrier.descriptor, FLOAT_TYPE)
result_carrier = vt_carrier.subst({target: replacement})
result = result_carrier.fetch()
print("after subst:", result)

# Verify: should be VaryingType(int, float, str)
expected = VaryingType.of(INT_TYPE, FLOAT_TYPE, z=STR_TYPE)
print("matches expected:", result == expected)
