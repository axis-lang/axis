"""
typespec.nodes
~~~~~~~~~~~~~~
Representación estructurada de tipos resueltos.

Un TypeNode es el resultado de parsear un tipo Python en un árbol navegable.
Cada nodo sabe si es Annotated, Union, Generic, TypeVar, etc., y expone
su información de forma uniforme sin necesidad de llamar get_origin/get_args
directamente.

Ejemplo::

    node = TypeNode.from_type(Annotated[dict[str, list[int]], "meta"])
    node.is_annotated         # True
    node.metadata             # ["meta"]
    node.inner.origin         # dict
    node.inner.args[1].origin # list
"""

from __future__ import annotations

import typing
from dataclasses import dataclass, field
from typing import Any, Callable

# Tipos especiales que reconocemos
_ANNOTATED = typing.Annotated
_UNION = typing.Union
_LITERAL = typing.Literal
_CLASSVAR = typing.ClassVar
_FINAL = typing.Final
_OPTIONAL = "Optional"  # Union[X, None]


# ---------------------------------------------------------------------------
# Clasificación de tipos
# ---------------------------------------------------------------------------

class TypeKind:
    """Categorías de tipos que puede representar un TypeNode."""

    SIMPLE    = "simple"      # int, str, bool, float, bytes…
    ANNOTATED = "annotated"   # Annotated[X, ...]
    UNION     = "union"       # Union[X, Y] / X | Y
    OPTIONAL  = "optional"    # Optional[X] == Union[X, None]
    GENERIC   = "generic"     # list[X], dict[K, V], Tuple[X, ...], etc.
    CALLABLE  = "callable"    # Callable[[args], ret]
    LITERAL   = "literal"     # Literal["a", 1, ...]
    CLASSVAR  = "classvar"    # ClassVar[X]
    FINAL     = "final"       # Final[X]
    TYPEVAR   = "typevar"     # T, KT, VT…
    PARAMSPEC = "paramspec"   # P (ParamSpec)
    TYPEVARTUPLE = "typevartuple"  # *Ts
    NONE_TYPE = "none"        # type(None) / None
    FORWARD   = "forward"     # ForwardRef sin resolver
    UNKNOWN   = "unknown"     # cualquier otra cosa


# ---------------------------------------------------------------------------
# TypeNode
# ---------------------------------------------------------------------------

@dataclass
class TypeNode:
    """
    Nodo en el árbol de tipos.

    Atributos principales:
        kind:       categoría del tipo (TypeKind.*)
        raw:        el objeto tipo original (ej: Annotated[int, "x"])
        origin:     el origen genérico (ej: list, dict, Union)
        args:       argumentos genéricos como lista de TypeNode
        metadata:   metadatos de Annotated (solo si kind=ANNOTATED)
        inner:      tipo "interior" para Annotated, Optional, ClassVar, Final
        name:       nombre para TypeVar, ParamSpec, ForwardRef
        literal_values: valores para Literal
        is_nullable: True si el tipo admite None (Optional / Union con None)
    """

    kind: str
    raw: Any

    # Componentes según el tipo
    origin: Any = None
    args: list[TypeNode] = field(default_factory=list)
    metadata: list[Any] = field(default_factory=list)
    inner: TypeNode | None = None
    name: str | None = None
    literal_values: list[Any] = field(default_factory=list)
    is_nullable: bool = False

    # ---------------------------------------------------------------------------
    # Propiedades de conveniencia
    # ---------------------------------------------------------------------------

    @property
    def is_annotated(self) -> bool:
        return self.kind == TypeKind.ANNOTATED

    @property
    def is_union(self) -> bool:
        return self.kind in (TypeKind.UNION, TypeKind.OPTIONAL)

    @property
    def is_optional(self) -> bool:
        return self.kind == TypeKind.OPTIONAL

    @property
    def is_generic(self) -> bool:
        return self.kind == TypeKind.GENERIC

    @property
    def is_simple(self) -> bool:
        return self.kind == TypeKind.SIMPLE

    @property
    def is_typevar(self) -> bool:
        return self.kind == TypeKind.TYPEVAR

    @property
    def is_forward_ref(self) -> bool:
        return self.kind == TypeKind.FORWARD

    @property
    def is_literal(self) -> bool:
        return self.kind == TypeKind.LITERAL

    @property
    def base_type(self) -> Any:
        """
        El tipo "base" sin wrappers Annotated/Optional/ClassVar/Final.
        Para un Annotated[int, ...] retorna int.
        Para un Optional[str] retorna str.
        Para un int retorna int.
        """
        if self.inner is not None:
            return self.inner.base_type
        return self.raw

    @property
    def all_metadata(self) -> list[Any]:
        """
        Todos los metadatos de Annotated en este nodo y sus hijos Annotated.
        Útil para Annotated anidados.
        """
        result = list(self.metadata)
        if self.inner and self.inner.is_annotated:
            result.extend(self.inner.all_metadata)
        return result

    def get_metadata_of_type(self, meta_type: type) -> list[Any]:
        """
        Filtra los metadatos de Annotated por tipo.

        Ejemplo::

            @dataclass
            class Constraint:
                min_val: int

            node = TypeNode.from_type(Annotated[int, Constraint(min_val=0)])
            constraints = node.get_metadata_of_type(Constraint)
        """
        return [m for m in self.all_metadata if isinstance(m, meta_type)]

    def first_metadata_of_type(self, meta_type: type) -> Any | None:
        """Como get_metadata_of_type pero retorna solo el primer match."""
        for m in self.all_metadata:
            if isinstance(m, meta_type):
                return m
        return None

    def walk(self) -> typing.Iterator[TypeNode]:
        """
        Recorre el árbol de TypeNodes en pre-order (self primero, luego hijos).
        Incluye inner y args.
        """
        yield self
        if self.inner is not None:
            yield from self.inner.walk()
        for arg in self.args:
            yield from arg.walk()

    def find_all(self, predicate: Callable[[TypeNode], bool]) -> list[TypeNode]:
        """Retorna todos los nodos del árbol que satisfacen el predicado."""
        return [node for node in self.walk() if predicate(node)]

    def find_annotated(self) -> list[TypeNode]:
        """Retorna todos los nodos Annotated en el árbol."""
        return self.find_all(lambda n: n.is_annotated)

    # ---------------------------------------------------------------------------
    # Constructor principal
    # ---------------------------------------------------------------------------

    @classmethod
    def from_type(cls, tp: Any) -> TypeNode:
        """
        Construye un TypeNode a partir de cualquier objeto tipo de Python.

        Soporta:
        - Tipos simples: int, str, bool, None, type(None)
        - Annotated[X, ...]
        - Union[X, Y], Optional[X], X | Y (en 3.10+)
        - Genéricos: list[X], dict[K, V], tuple[X, ...], set[X]
        - Callable[[args], ret]
        - Literal["a", 1]
        - ClassVar[X], Final[X]
        - TypeVar, ParamSpec, TypeVarTuple
        - ForwardRef (no resuelto)
        - TypeAliasType (3.12+)
        """
        return _TypeNodeBuilder.build(tp)

    def __repr__(self) -> str:
        parts = [f"TypeNode(kind={self.kind!r}"]
        if self.origin is not None:
            parts.append(f", origin={self.origin!r}")
        if self.name:
            parts.append(f", name={self.name!r}")
        if self.inner is not None:
            parts.append(f", inner={self.inner!r}")
        if self.args:
            parts.append(f", args=[{len(self.args)} items]")
        if self.metadata:
            parts.append(f", metadata={self.metadata!r}")
        if self.literal_values:
            parts.append(f", literal_values={self.literal_values!r}")
        parts.append(")")
        return "".join(parts)


# ---------------------------------------------------------------------------
# Builder interno (no expuesto directamente)
# ---------------------------------------------------------------------------

class _TypeNodeBuilder:

    @classmethod
    def build(cls, tp: Any) -> TypeNode:
        # None literal (como tipo de retorno)
        if tp is None or tp is type(None):
            return TypeNode(kind=TypeKind.NONE_TYPE, raw=tp)

        # ForwardRef no resuelta
        if isinstance(tp, typing.ForwardRef):
            return TypeNode(
                kind=TypeKind.FORWARD,
                raw=tp,
                name=tp.__forward_arg__,
            )

        # TypeVar
        if isinstance(tp, typing.TypeVar):
            return TypeNode(
                kind=TypeKind.TYPEVAR,
                raw=tp,
                name=tp.__name__,
            )

        # ParamSpec (3.10+)
        if isinstance(tp, typing.ParamSpec):
            return TypeNode(
                kind=TypeKind.PARAMSPEC,
                raw=tp,
                name=tp.__name__,
            )

        # TypeVarTuple (3.11+)
        if isinstance(tp, typing.TypeVarTuple):
            return TypeNode(
                kind=TypeKind.TYPEVARTUPLE,
                raw=tp,
                name=tp.__name__,
            )

        # TypeAliasType (3.12+): desempacar su valor
        if hasattr(typing, "TypeAliasType") and isinstance(tp, typing.TypeAliasType):
            inner_node = cls.build(tp.__value__)
            return TypeNode(
                kind=TypeKind.GENERIC,  # tratar como alias
                raw=tp,
                origin=tp,
                name=tp.__name__,
                inner=inner_node,
            )

        origin = typing.get_origin(tp)
        args = typing.get_args(tp)

        # --- Annotated ---
        if origin is typing.Annotated:
            # args[0] es el tipo base, args[1:] son los metadatos
            inner_tp, *metadata = args
            inner_node = cls.build(inner_tp)
            return TypeNode(
                kind=TypeKind.ANNOTATED,
                raw=tp,
                origin=origin,
                inner=inner_node,
                metadata=list(metadata),
                is_nullable=inner_node.is_nullable,
            )

        # --- Literal ---
        if origin is typing.Literal:
            return TypeNode(
                kind=TypeKind.LITERAL,
                raw=tp,
                origin=origin,
                literal_values=list(args),
            )

        # --- ClassVar ---
        if origin is typing.ClassVar:
            inner_node = cls.build(args[0]) if args else None
            return TypeNode(
                kind=TypeKind.CLASSVAR,
                raw=tp,
                origin=origin,
                inner=inner_node,
            )

        # --- Final ---
        if origin is typing.Final:
            inner_node = cls.build(args[0]) if args else None
            return TypeNode(
                kind=TypeKind.FINAL,
                raw=tp,
                origin=origin,
                inner=inner_node,
            )

        # --- Union (incluyendo Optional y X | Y) ---
        if origin is typing.Union:
            none_type = type(None)
            non_none_args = [a for a in args if a is not none_type]
            has_none = none_type in args

            arg_nodes = [cls.build(a) for a in args]

            # Optional[X] == Union[X, None] con un solo tipo no-None
            if has_none and len(non_none_args) == 1:
                inner_node = cls.build(non_none_args[0])
                return TypeNode(
                    kind=TypeKind.OPTIONAL,
                    raw=tp,
                    origin=origin,
                    args=arg_nodes,
                    inner=inner_node,
                    is_nullable=True,
                )

            return TypeNode(
                kind=TypeKind.UNION,
                raw=tp,
                origin=origin,
                args=arg_nodes,
                is_nullable=has_none,
            )

        # --- Callable ---
        if origin is not None:
            import collections.abc
            if origin is collections.abc.Callable:
                arg_nodes = [cls.build(a) for a in args]
                return TypeNode(
                    kind=TypeKind.CALLABLE,
                    raw=tp,
                    origin=origin,
                    args=arg_nodes,
                )

        # --- Tipos genéricos (list[X], dict[K,V], etc.) ---
        if origin is not None and args:
            arg_nodes = [cls.build(a) for a in args]
            return TypeNode(
                kind=TypeKind.GENERIC,
                raw=tp,
                origin=origin,
                args=arg_nodes,
            )

        # --- Genérico sin parámetros (list, dict, etc.) ---
        if origin is not None:
            return TypeNode(
                kind=TypeKind.GENERIC,
                raw=tp,
                origin=origin,
            )

        # --- Tipo simple (int, str, clases custom, etc.) ---
        return TypeNode(
            kind=TypeKind.SIMPLE,
            raw=tp,
            name=getattr(tp, "__name__", None),
        )



