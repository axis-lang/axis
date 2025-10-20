"""
Panifica la implementacion de un prototipo de un algebra de tipos para este lenguaje

este sistema de tipado debe soportar yuxtaposicion de expresiones:
let a: Array[_, _] Real = ((1,0), (0,1)) # Matriz identidad 2x2

y tambien debe soportar la coercion de tipos:
let b: Array[_, _] Complex = a  # Matriz identidad 2x2

fn mul_reduce(a: T, b: T) -> N

    val T: Array[..] N
    val N: Number

def MyGroup
takes: 
    val name: Text

    val members: List (
        name: Text
        age: Natural
        role: Or["admin", "editor"] = "editor"
    )

def List: Array[_] # una lista ES un array de logitud no especifica

"""

from __future__ import annotations
from typing import Any, Iterable, Sequence, Tuple, Optional, Dict, List as PyList, Union
from protobase import Record
# (agregamos nuevos tipos de ayuda)
from typing import MutableMapping

# ============================================================
#  Proto Algebra de Tipos (Prototipo)
# ============================================================

# Sentinel para dimensión desconocida explícita (_)
class DimWildcard(Record, consed=True):
    def __repr__(self) -> str:
        return "_"

DIM_WILDCARD = DimWildcard()

# Representa "cualquier número de dimensiones extra" (.. en el docstring)
VARIADIC_DIMS = Ellipsis


class Type(Record, consed=True):
    name: str

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


# Escalar base
class ScalarType(Type, consed=True):
    pass


class NumberType(ScalarType, consed=True):
    name: str = "Number"


class RealType(NumberType, consed=True):
    name: str = "Real"


class ComplexType(NumberType, consed=True):
    name: str = "Complex"


class NaturalType(RealType, consed=True):
    name: str = "Natural"


class TextType(ScalarType, consed=True):
    name: str = "Text"


Number = NumberType()
Real = RealType()
Complex = ComplexType()
Natural = NaturalType()
Text = TextType()

# Union restringido a literales (Or["admin","editor"])
class OrType(Type):
    options: Tuple[Any, ...]

    @property
    def name(self) -> str:
        return "Or" + str(list(self.options))

    def __contains__(self, v: Any) -> bool:
        return v in self.options


# Tipo para arrays con shape (tupla de dimensiones) y tipo base (element)
class ArrayType(Type):
    shape: Tuple[Union[int, DimWildcard], ...]  # dimensiones conocidas o _
    element: Type

    @property
    def name(self) -> str:
        dims = ", ".join(str(d) for d in self.shape)
        return f"Array[{dims}] {self.element}"

    def rank(self) -> int:
        return len(self.shape)


# Alias List = Array[_]
def ListOf(elem: Type) -> ArrayType:
    return ArrayType(shape=(DIM_WILDCARD,), element=elem)


# Tupla heterogénea
class TupleType(Type):
    items: Tuple[Type, ...]

    @property
    def name(self) -> str:
        return "(" + ", ".join(str(t) for t in self.items) + ")"


# Estructuras estilo record (para MyGroup / miembros)
class StructField(Record):
    name: str
    type: Type
    default: Any = None


class StructType(Type):
    fields: Tuple[StructField, ...]

    @property
    def name(self) -> str:
        inner = ", ".join(f"{f.name}: {f.type}" for f in self.fields)
        return f"Struct {{ {inner} }}"


# Funciones
class FunctionType(Type):
    params: Tuple[Type, ...]
    result: Type
    type_params: Tuple[Type, ...] = ()

    @property
    def name(self) -> str:
        ps = ", ".join(str(p) for p in self.params)
        return f"fn({ps}) -> {self.result}"


# ============================================================
#  Coerciones
# ============================================================

# Orden simple de promoción
COERCION_CHAIN: PyList[Type] = [Natural, Real, Complex]

def can_coerce(src: Type, dst: Type) -> bool:
    if src == dst:
        return True
    # escalares numéricos
    if isinstance(src, ScalarType) and isinstance(dst, ScalarType):
        try:
            si = COERCION_CHAIN.index(src)
            di = COERCION_CHAIN.index(dst)
            return si <= di
        except ValueError:
            return False
    # Arrays: se puede si element es coercible y shape compatible
    if isinstance(src, ArrayType) and isinstance(dst, ArrayType):
        return shapes_compatible(src.shape, dst.shape) and can_coerce(src.element, dst.element)
    return False


def shapes_compatible(a: Tuple[Any, ...], b: Tuple[Any, ...]) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if DIM_WILDCARD in (x, y):
            continue
        if x != y:
            return False
    return True


def is_assignable(src: Type, dst: Type) -> bool:
    if src == dst:
        return True
    return can_coerce(src, dst)


# ============================================================
#  Unificación
# ============================================================

def unify(t1: Type, t2: Type) -> Optional[Type]:
    if t1 == t2:
        return t1
    # Escalares con coerción mínima común
    if isinstance(t1, ScalarType) and isinstance(t2, ScalarType):
        for t in COERCION_CHAIN:
            if can_coerce(t1, t) and can_coerce(t2, t):
                return t
        return None
    # Arrays
    if isinstance(t1, ArrayType) and isinstance(t2, ArrayType):
        el = unify(t1.element, t2.element)
        if el is None:
            return None
        shape = unify_array_shape(t1.shape, t2.shape)
        if shape is None:
            return None
        return ArrayType(shape=shape, element=el)
    return None


def unify_array_shape(a: Tuple[Any, ...], b: Tuple[Any, ...]) -> Optional[Tuple[Any, ...]]:
    if len(a) != len(b):
        return None
    out = []
    for x, y in zip(a, b):
        if x == y:
            out.append(x)
        elif x == DIM_WILDCARD:
            out.append(y)
        elif y == DIM_WILDCARD:
            out.append(x)
        else:
            return None
    return tuple(out)


# ============================================================
#  Inferencia desde literales de tuplas (ej: matriz identidad)
# ============================================================

def infer_array_from_tuple(obj: Any) -> Optional[ArrayType]:
    # Espera estructura de tuplas anidadas rectangular
    def collect(o, depth=0):
        if isinstance(o, tuple):
            if not o:
                return (0,), None
            dims = []
            sub_el_type = None
            lengths = set()
            for el in o:
                shape, el_t = collect(el, depth + 1)
                if shape is None:
                    return None, None
                lengths.add(shape[0])
                dims.append(shape)
                sub_el_type = unify(sub_el_type, el_t) if sub_el_type else el_t
            if len(lengths) != 1:
                return None, None
            inner_shape = dims[0]
            return (len(o),) + inner_shape, sub_el_type
        else:
            base_type = infer_scalar(o)
            return (), base_type

    def infer_scalar(v):
        if isinstance(v, int):
            if v >= 0:
                return Natural
            return Real
        if isinstance(v, float):
            return Real
        if isinstance(v, complex):
            return Complex
        if isinstance(v, str):
            return Text
        return None

    shape, elem_type = collect(obj)
    if shape is None or elem_type is None:
        return None
    return ArrayType(shape=tuple(shape), element=elem_type)


# ============================================================
#  Ejemplos construidos (para los casos del docstring)
# ============================================================

# Array[_, _] Real   (plantilla con comodines)
Matrix2DRealTemplate = ArrayType(shape=(DIM_WILDCARD, DIM_WILDCARD), element=Real)
Matrix2DComplexTemplate = ArrayType(shape=(DIM_WILDCARD, DIM_WILDCARD), element=Complex)

# List alias (una dimensión desconocida)
def List(t: Type) -> ArrayType:
    return ListOf(t)

# Or["admin","editor"]
RoleType = OrType(options=("admin", "editor"))

# Struct MyGroup.members entry sketch
MemberStruct = StructType(fields=(
    StructField(name="name", type=Text),
    StructField(name="age", type=Natural),
    StructField(name="role", type=RoleType, default="editor"),
))

MyGroupType = StructType(fields=(
    StructField(name="name", type=Text),
    StructField(name="members", type=List(MemberStruct)),
))

# Firma ejemplo mul_reduce: (T, T) -> N con restricciones (no se aplican todavía)
MulReduceType = FunctionType(
    params=(
        ArrayType(shape=(DIM_WILDCARD, DIM_WILDCARD), element=TypeVar(name="N")),
        ArrayType(shape=(DIM_WILDCARD, DIM_WILDCARD), element=TypeVar(name="N")),
    ),
    result=TypeVar(name="N"),
    type_params=(TypeVar(name="N"),),
)

IdFunctionType = FunctionType(
    params=(TypeVar(name="T"),),
    result=TypeVar(name="T"),
    type_params=(TypeVar(name="T"),),
)

# ============================================================
#  API Pública
# ============================================================

__all__ = [
    "Type", "ScalarType",
    "Number", "Real", "Complex", "Natural", "Text",
    "ArrayType", "TupleType", "StructType", "StructField",
    "FunctionType", "OrType",
    "List", "ListOf",
    "RoleType", "MemberStruct", "MyGroupType",
    "MulReduceType",
    "DIM_WILDCARD", "unify", "is_assignable", "infer_array_from_tuple",
    "Matrix2DRealTemplate", "Matrix2DComplexTemplate",
] + [
    "TypeVar", "InferenceVar", "InferenceContext",
    "instantiate", "infer_expr",
    "LiteralExpr", "VarExpr", "TupleExpr", "ArrayLiteralExpr", "CallExpr",
    "IdFunctionType",
]


# ============================================================
#  Demo rápida (prototipo)
# ============================================================

if __name__ == "__main__":
    identity2x2 = ((1, 0), (0, 1))
    inferred = infer_array_from_tuple(identity2x2)
    print("Inferido literal:", inferred)

    # Verificamos asignabilidad a plantilla Array[_, _] Real
    print("Asignable a Matrix Real Template?",
          is_assignable(inferred, Matrix2DRealTemplate))

    # Coerción a Complex
    candidate_complex = ArrayType(shape=inferred.shape, element=Complex)
    unified = unify(inferred, candidate_complex)
    print("Unificación Real/Complex ->", unified)

    # Chequeo contra plantilla Complex
    print("Asignable a Matrix Complex Template?",
          is_assignable(inferred, Matrix2DComplexTemplate))

    print("Tipo MyGroup:", MyGroupType)

    print("\n--- Inferencia Genérica ---")
    ctx = InferenceContext()
    env: Env = {
        "id": IdFunctionType,
        "mul_reduce": MulReduceType,
    }

    t_id_nat = infer_expr(CallExpr(func=VarExpr(name="id"), args=(LiteralExpr(value=5),)), env, ctx)
    print("id(5) ::", ctx.finalize(t_id_nat))

    t_id_real = infer_expr(CallExpr(func=VarExpr(name="id"), args=(LiteralExpr(value=5.0),)), env, ctx)
    print("id(5.0) ::", ctx.finalize(t_id_real))

    # Reusar inferencia de matriz identidad
    identity2x2 = ((1, 0), (0, 1))
    arr_type = infer_array_from_tuple(identity2x2)
    env["A"] = arr_type
    ctx2 = InferenceContext()
    call_mul = CallExpr(
        func=VarExpr(name="mul_reduce"),
        args=(VarExpr(name="A"), VarExpr(name="A")),
    )
    result_type = infer_expr(call_mul, env, ctx2)
    print("mul_reduce(A, A) ::", ctx2.finalize(result_type))