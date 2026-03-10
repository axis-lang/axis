"""
typespec
~~~~~~~~
Introspección estructurada de tipos Python con soporte completo para Annotated.

Soporta Python 3.10+ con compatibilidad hacia 3.13/3.14 (PEP 649).

Uso rápido::

    from typing import Annotated
    from dataclasses import dataclass
    from typespec import inspect_type, inspect_class, inspect_func, get_annotated_metadata

    # Tipo aislado
    node = inspect_type(Annotated[int, "descripción"])
    node.is_annotated   # True
    node.metadata       # ["descripción"]
    node.inner.raw      # int

    # Clase
    @dataclass
    class User:
        name: Annotated[str, "El nombre del usuario"]
        age: Annotated[int, "La edad"] = 0

    info = inspect_class(User)
    info.fields["name"].metadata   # ["El nombre del usuario"]
    info.fields["age"].has_default # True

    # Función
    def process(x: Annotated[int, "valor entrada"]) -> Annotated[str, "resultado"]:
        ...

    sig = inspect_func(process)
    sig.params["x"].metadata           # ["valor entrada"]
    sig.return_annotation.metadata     # ["resultado"]
"""

from .inspector import (
    ClassInfo,
    FieldInfo,
    FuncInfo,
    ParamInfo,
    TypeSpecInspector,
    get_annotated_metadata,
    inspect_class,
    inspect_func,
    inspect_type,
    strip_annotated,
)
from .nodes import TypeKind, TypeNode
from .resolver import AnnotationResolver, EvalStrategy

__version__ = "0.1.0"
__all__ = [
    # Funciones de conveniencia
    "inspect_type",
    "inspect_class",
    "inspect_func",
    "get_annotated_metadata",
    "strip_annotated",
    # Clases de resultado
    "TypeNode",
    "TypeKind",
    "ClassInfo",
    "FieldInfo",
    "FuncInfo",
    "ParamInfo",
    # Clases de configuración
    "TypeSpecInspector",
    "AnnotationResolver",
    "EvalStrategy",
]
