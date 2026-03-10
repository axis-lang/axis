"""
typespec.inspector
~~~~~~~~~~~~~~~~~~
API de alto nivel para introspección estructurada de tipos.

Combina AnnotationResolver (evaluación) + TypeNode (representación) para
ofrecer una interfaz ergonómica orientada a casos de uso comunes:

- Inspeccionar clases y dataclasses
- Extraer metadatos de Annotated
- Analizar firmas de funciones
- Validar estructuras de tipos
- Soportar patrones de "marcadores" en Annotated

Uso rápido::

    from typespec import inspect_type, inspect_class, inspect_func

    # Un tipo aislado
    node = inspect_type(Annotated[int, "descripcion", Validator(min=0)])
    node.metadata              # ["descripcion", Validator(min=0)]
    node.inner.raw             # int

    # Una clase completa
    info = inspect_class(MyModel)
    info.fields["name"].metadata  # metadatos de Annotated en el campo 'name'

    # Una función
    sig = inspect_func(my_func)
    sig.params["x"].annotation.is_optional  # True si el param es Optional
"""

from __future__ import annotations

import dataclasses
import inspect as _inspect
import typing
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator

from .nodes import TypeKind, TypeNode
from .resolver import AnnotationResolver, EvalStrategy


# ---------------------------------------------------------------------------
# FieldInfo: información de un campo/atributo
# ---------------------------------------------------------------------------

@dataclass
class FieldInfo:
    """
    Información estructurada sobre un campo de una clase.

    Incluye:
    - nombre y tipo como TypeNode
    - si tiene valor por defecto
    - si es ClassVar o Final
    - metadatos de Annotated directamente accesibles
    """

    name: str
    annotation: TypeNode
    has_default: bool = False
    is_classvar: bool = False
    is_final: bool = False
    source_class: type | None = None
    # Sentinel: None significa "no hay default", otherwise el valor real
    default: Any = None

    @property
    def metadata(self) -> list[Any]:
        """Acceso directo a los metadatos de Annotated."""
        node = self.annotation
        # Atravesar ClassVar / Final para llegar al Annotated
        if node.kind in (TypeKind.CLASSVAR, TypeKind.FINAL) and node.inner:
            node = node.inner
        if node.is_annotated:
            return node.all_metadata
        return []

    def get_metadata_of_type(self, meta_type: type) -> list[Any]:
        """Filtra metadatos por tipo."""
        return [m for m in self.metadata if isinstance(m, meta_type)]

    def first_metadata_of_type(self, meta_type: type) -> Any | None:
        for m in self.metadata:
            if isinstance(m, meta_type):
                return m
        return None

    @property
    def base_type(self) -> Any:
        """El tipo base sin wrappers (Annotated/ClassVar/Final/Optional quitados)."""
        return self.annotation.base_type

    @property
    def is_optional(self) -> bool:
        """True si el campo acepta None."""
        node = self.annotation
        if node.kind in (TypeKind.CLASSVAR, TypeKind.FINAL) and node.inner:
            node = node.inner
        if node.is_annotated and node.inner:
            node = node.inner
        return node.is_optional or node.is_nullable

    def __repr__(self) -> str:
        return (
            f"FieldInfo(name={self.name!r}, "
            f"annotation={self.annotation!r}, "
            f"has_default={self.has_default}, "
            f"metadata={self.metadata!r})"
        )


# ---------------------------------------------------------------------------
# ClassInfo: información de una clase
# ---------------------------------------------------------------------------

@dataclass
class ClassInfo:
    """
    Información estructurada sobre una clase completa.

    Acceso a campos por nombre, iteración, filtros por metadatos.
    """

    cls: type
    fields: dict[str, FieldInfo] = field(default_factory=dict)
    is_dataclass: bool = False
    resolver: AnnotationResolver = field(
        default_factory=AnnotationResolver, repr=False
    )

    @property
    def name(self) -> str:
        return self.cls.__name__

    @property
    def instance_fields(self) -> dict[str, FieldInfo]:
        """Campos que NO son ClassVar ni Final de clase."""
        return {
            name: fi
            for name, fi in self.fields.items()
            if not fi.is_classvar
        }

    @property
    def class_vars(self) -> dict[str, FieldInfo]:
        """Solo los ClassVar."""
        return {
            name: fi
            for name, fi in self.fields.items()
            if fi.is_classvar
        }

    def fields_with_metadata(
        self, meta_type: type
    ) -> dict[str, FieldInfo]:
        """
        Filtra campos que tienen al menos un metadato del tipo dado.

        Ejemplo::

            @dataclass
            class Validator:
                min_val: int

            info = inspect_class(MyModel)
            validated = info.fields_with_metadata(Validator)
        """
        return {
            name: fi
            for name, fi in self.fields.items()
            if fi.get_metadata_of_type(meta_type)
        }

    def iter_fields(self) -> Iterator[FieldInfo]:
        yield from self.fields.values()

    def __repr__(self) -> str:
        return f"ClassInfo(cls={self.name!r}, fields={list(self.fields.keys())})"


# ---------------------------------------------------------------------------
# ParamInfo: información de un parámetro de función
# ---------------------------------------------------------------------------

@dataclass
class ParamInfo:
    """Información de un parámetro de función."""

    name: str
    annotation: TypeNode | None
    kind: str  # POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, KEYWORD_ONLY, etc.
    has_default: bool = False
    default: Any = _inspect.Parameter.empty

    @property
    def metadata(self) -> list[Any]:
        if self.annotation and self.annotation.is_annotated:
            return self.annotation.all_metadata
        return []

    @property
    def base_type(self) -> Any:
        if self.annotation is None:
            return None
        return self.annotation.base_type

    @property
    def is_optional(self) -> bool:
        if self.annotation is None:
            return False
        return self.annotation.is_optional or self.has_default

    def get_metadata_of_type(self, meta_type: type) -> list[Any]:
        return [m for m in self.metadata if isinstance(m, meta_type)]


@dataclass
class FuncInfo:
    """
    Información estructurada sobre una función o método.
    """

    func: Callable[..., Any]
    params: dict[str, ParamInfo] = field(default_factory=dict)
    return_annotation: TypeNode | None = None

    @property
    def name(self) -> str:
        return getattr(self.func, "__name__", repr(self.func))

    @property
    def positional_params(self) -> dict[str, ParamInfo]:
        return {
            name: p
            for name, p in self.params.items()
            if p.kind in (
                _inspect.Parameter.POSITIONAL_OR_KEYWORD,
                _inspect.Parameter.POSITIONAL_ONLY,
            )
        }

    @property
    def keyword_params(self) -> dict[str, ParamInfo]:
        return {
            name: p
            for name, p in self.params.items()
            if p.kind == _inspect.Parameter.KEYWORD_ONLY
        }

    def params_with_metadata(self, meta_type: type) -> dict[str, ParamInfo]:
        return {
            name: p
            for name, p in self.params.items()
            if p.get_metadata_of_type(meta_type)
        }


# ---------------------------------------------------------------------------
# Inspector principal
# ---------------------------------------------------------------------------

class TypeSpecInspector:
    """
    Inspector principal que combina resolución y estructuración de tipos.

    Punto de entrada principal de la librería. Instanciable con estrategia
    personalizada, o usar las funciones de nivel de módulo para casos simples.

    Ejemplo::

        inspector = TypeSpecInspector()
        class_info = inspector.inspect_class(MyModel, follow_mro=True)
        func_info = inspector.inspect_func(my_function)
        type_node = inspector.inspect_type(Annotated[int, "meta"])
    """

    def __init__(self, strategy: EvalStrategy | None = None) -> None:
        self.resolver = AnnotationResolver(strategy)

    # ------------------------------------------------------------------
    # inspect_type: tipo aislado → TypeNode
    # ------------------------------------------------------------------

    def inspect_type(self, tp: Any) -> TypeNode:
        """
        Parsea un tipo Python en un TypeNode navegable.

        Args:
            tp: cualquier tipo: int, Annotated[str, ...], list[int], etc.

        Returns:
            TypeNode con toda la información estructurada.
        """
        return TypeNode.from_type(tp)

    # ------------------------------------------------------------------
    # inspect_class: clase → ClassInfo
    # ------------------------------------------------------------------

    def inspect_class(
        self,
        cls: type,
        *,
        follow_mro: bool = False,
    ) -> ClassInfo:
        """
        Inspecciona todos los campos anotados de una clase.

        Args:
            cls: la clase a inspeccionar.
            follow_mro: si True, incluye campos heredados del MRO completo.

        Returns:
            ClassInfo con todos los FieldInfo resueltos.
        """
        resolved = self.resolver.resolve(cls, follow_mro=follow_mro)
        is_dc = dataclasses.is_dataclass(cls)

        # Construir mapa de defaults desde dataclass si aplica
        dc_fields: dict[str, dataclasses.Field[Any]] = {}
        if is_dc:
            dc_fields = {f.name: f for f in dataclasses.fields(cls)}

        # Defaults desde __init__ si no es dataclass
        init_defaults: dict[str, Any] = {}
        if not is_dc and hasattr(cls, "__init__"):
            try:
                sig = _inspect.signature(cls.__init__)
                for pname, param in sig.parameters.items():
                    if pname == "self":
                        continue
                    if param.default is not _inspect.Parameter.empty:
                        init_defaults[pname] = param.default
            except (ValueError, TypeError):
                pass

        fields: dict[str, FieldInfo] = {}
        for name, tp in resolved.items():
            node = TypeNode.from_type(tp)

            # Detectar ClassVar y Final
            is_classvar = node.kind == TypeKind.CLASSVAR
            is_final = node.kind == TypeKind.FINAL

            # Default desde dataclass
            has_default = False
            default_val: Any = dataclasses.MISSING

            if is_dc and name in dc_fields:
                dc_f = dc_fields[name]
                if dc_f.default is not dataclasses.MISSING:
                    has_default = True
                    default_val = dc_f.default
                elif dc_f.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
                    has_default = True
                    default_val = dc_f.default_factory  # guardamos la factory
            elif name in init_defaults:
                has_default = True
                default_val = init_defaults[name]
            elif hasattr(cls, name):
                # Variable de clase con valor
                cls_val = getattr(cls, name)
                if not callable(cls_val) and not isinstance(cls_val, (classmethod, staticmethod, property)):
                    has_default = True
                    default_val = cls_val

            # Determinar source_class (de qué clase viene en MRO)
            source = None
            if follow_mro:
                for klass in cls.__mro__:
                    if name in getattr(klass, "__annotations__", {}):
                        source = klass
                        break

            fields[name] = FieldInfo(
                name=name,
                annotation=node,
                has_default=has_default,
                default=default_val,
                is_classvar=is_classvar,
                is_final=is_final,
                source_class=source,
            )

        return ClassInfo(
            cls=cls,
            fields=fields,
            is_dataclass=is_dc,
            resolver=self.resolver,
        )

    # ------------------------------------------------------------------
    # inspect_func: función → FuncInfo
    # ------------------------------------------------------------------

    def inspect_func(self, func: Callable[..., Any]) -> FuncInfo:
        """
        Inspecciona los parámetros y tipo de retorno de una función.

        Soporta: funciones normales, métodos, classmethod, staticmethod,
                 lambdas (sin anotaciones), funciones con *args/**kwargs.

        Args:
            func: la función a inspeccionar.

        Returns:
            FuncInfo con todos los ParamInfo y el return_annotation.
        """
        # Normalizar: classmethod/staticmethod → __func__
        if isinstance(func, classmethod):
            func = func.__func__
        elif isinstance(func, staticmethod):
            func = func.__func__

        resolved = self.resolver.resolve(func)
        return_tp = resolved.pop("return", None)

        try:
            sig = _inspect.signature(func)
        except (ValueError, TypeError):
            sig = None

        params: dict[str, ParamInfo] = {}

        if sig is not None:
            for pname, param in sig.parameters.items():
                if pname == "self" or pname == "cls":
                    continue

                ann = resolved.get(pname)
                ann_node = TypeNode.from_type(ann) if ann is not None else None

                params[pname] = ParamInfo(
                    name=pname,
                    annotation=ann_node,
                    kind=param.kind.name,
                    has_default=param.default is not _inspect.Parameter.empty,
                    default=param.default,
                )
        else:
            # Sin signature: usar solo lo que tenemos en resolved
            for pname, ann in resolved.items():
                params[pname] = ParamInfo(
                    name=pname,
                    annotation=TypeNode.from_type(ann),
                    kind="POSITIONAL_OR_KEYWORD",
                )

        return_node = TypeNode.from_type(return_tp) if return_tp is not None else None

        return FuncInfo(
            func=func,
            params=params,
            return_annotation=return_node,
        )

    # ------------------------------------------------------------------
    # inspect_annotated: extracción especializada de Annotated
    # ------------------------------------------------------------------

    def inspect_annotated(self, tp: Any) -> tuple[Any, list[Any]]:
        """
        Extrae el tipo base y los metadatos de un Annotated.
        Si el tipo no es Annotated, retorna (tp, []).

        Returns:
            (tipo_base, [metadatos...])

        Ejemplo::

            base, meta = inspector.inspect_annotated(Annotated[int, "doc", Validator()])
            # base = int, meta = ["doc", Validator()]
        """
        origin = typing.get_origin(tp)
        if origin is typing.Annotated:
            args = typing.get_args(tp)
            inner, *metadata = args
            return inner, metadata
        return tp, []

    def strip_annotated(self, tp: Any) -> Any:
        """Quita todos los wrappers Annotated recursivamente."""
        node = TypeNode.from_type(tp)
        return node.base_type


# ---------------------------------------------------------------------------
# API de módulo (funciones de conveniencia)
# ---------------------------------------------------------------------------

_default_inspector = TypeSpecInspector()


def inspect_type(tp: Any) -> TypeNode:
    """
    Parsea un tipo en un TypeNode navegable.

    >>> inspect_type(Annotated[int, "meta"]).is_annotated
    True
    """
    return _default_inspector.inspect_type(tp)


def inspect_class(
    cls: type,
    *,
    follow_mro: bool = False,
    strategy: EvalStrategy | None = None,
) -> ClassInfo:
    """
    Inspecciona los campos anotados de una clase.

    >>> @dataclass
    ... class Model:
    ...     name: Annotated[str, "El nombre"]
    >>> info = inspect_class(Model)
    >>> info.fields["name"].metadata
    ['El nombre']
    """
    inspector = TypeSpecInspector(strategy) if strategy else _default_inspector
    return inspector.inspect_class(cls, follow_mro=follow_mro)


def inspect_func(
    func: Callable[..., Any],
    *,
    strategy: EvalStrategy | None = None,
) -> FuncInfo:
    """
    Inspecciona los parámetros y retorno de una función.

    >>> def greet(name: Annotated[str, "el nombre"]) -> str: ...
    >>> info = inspect_func(greet)
    >>> info.params["name"].metadata
    ['el nombre']
    """
    inspector = TypeSpecInspector(strategy) if strategy else _default_inspector
    return inspector.inspect_func(func)


def get_annotated_metadata(tp: Any) -> list[Any]:
    """
    Atajo para extraer metadatos de un Annotated directamente.

    >>> get_annotated_metadata(Annotated[int, "doc", 42])
    ['doc', 42]
    >>> get_annotated_metadata(int)
    []
    """
    _, meta = _default_inspector.inspect_annotated(tp)
    return meta


def strip_annotated(tp: Any) -> Any:
    """
    Quita Annotated y retorna el tipo base.

    >>> strip_annotated(Annotated[Annotated[int, "inner"], "outer"])
    <class 'int'>
    """
    return _default_inspector.strip_annotated(tp)
