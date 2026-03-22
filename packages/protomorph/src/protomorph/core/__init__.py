from contextvars import ContextVar

from .foundation import (
    Builtin,
    Data,
    Discriminant,
    Pure,
    Val,
    Meta,
    Omega,
    OMEGA,
    Ground,
    ground,
)
from .variant import Union, UnionGround, Variant
from .index import IndexKeyMeta, Index
from .schema import (
    Schema,
    UniformSchema,
    VaryingSchema,
)
from .tuple_ import Tuple
from .native import NativeType, NativeHost, NATIVE_HOST, Id, Integer, Text, Bool
from .hosted import Host, Spec, Qual, Hosted
from .placeholder import Var, Placeholder
from .traversal import deep_zip, ZipWalker
from .unification import unify
# from .constructors import (
#     union_of,
#     index_of,
#     uniform_tuple_of,
#     varying_tuple_of,
# )

HOST: ContextVar[Host] = ContextVar("BACKEND", default=NATIVE_HOST)

__all__ = [
    # Foundation
    "Builtin",
    "Data",
    "Discriminant",
    "Pure",
    "Val",
    "Meta",
    "Omega",
    "OMEGA",
    # Ground
    "Ground",
    # Variant
    "Union",
    "UnionGround",
    "Variant",
    # Index
    "IndexKeyMeta",
    "Index",
    # Schema
    "Schema",
    "Tuple",
    "UniformSchema",
    "VaryingSchema",
    # Native
    "NativeType",
    "NativeHost",
    "NATIVE_HOST",
    "Id",
    "Integer",
    "Text",
    "Bool",
    
    # Hosted
    "Host",
    "NativeHost",
    "HOST",
    "Spec",
    "Qual",
    "Hosted",
    # Placeholder
    "Var",
    "Placeholder",
    # Traversal
    "deep_zip",
    "ZipWalker",
    # Unification
    "unify",
    # Constructors
    "ground",
    # "union_of",
    # "index_of",
    # "uniform_tuple_of",
    # "varying_tuple_of",
]
