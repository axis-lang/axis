"""
typespec.resolver
~~~~~~~~~~~~~~~~~
Estrategias de evaluación y resolución de anotaciones de tipos.

El problema central: las anotaciones en Python pueden estar en varios estados:
  1. Objeto tipo real ya evaluado (int, list[str], Annotated[int, ...])
  2. String literal por PEP 563 (from __future__ import annotations)
  3. ForwardRef (creado internamente por typing cuando hay strings)
  4. Lazy/unevaluated en PEP 649 (Python 3.14+)

Esta capa abstrae todos esos casos.
"""

from __future__ import annotations

import inspect
import sys
import typing
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .nodes import TypeNode


# ---------------------------------------------------------------------------
# Detección de versión y disponibilidad de annotationlib (Python 3.14+)
# ---------------------------------------------------------------------------

PY_VERSION = sys.version_info[:2]
HAS_ANNOTATIONLIB = False

if PY_VERSION >= (3, 14):
    try:
        import annotationlib  # type: ignore[import]
        HAS_ANNOTATIONLIB = True
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Estrategias de evaluación
# ---------------------------------------------------------------------------

class EvalStrategy:
    """
    Encapsula la estrategia de cómo se evalúan las anotaciones stringificadas.

    En el ecosistema Python hay varios escenarios:
    - EAGER: evaluar todo inmediatamente (comportamiento clásico)
    - LAZY: dejar ForwardRefs sin resolver hasta que se necesiten (PEP 649)
    - STRING: devolver strings tal cual, sin evaluar
    """

    EAGER = "eager"
    LAZY = "lazy"
    STRING = "string"

    def __init__(
        self,
        mode: str = EAGER,
        globalns: dict[str, Any] | None = None,
        localns: dict[str, Any] | None = None,
        include_extras: bool = True,
    ) -> None:
        if mode not in (self.EAGER, self.LAZY, self.STRING):
            raise ValueError(f"mode debe ser uno de: eager, lazy, string. Recibido: {mode!r}")
        self.mode = mode
        self.globalns = globalns
        self.localns = localns
        self.include_extras = include_extras

    @classmethod
    def default(cls) -> EvalStrategy:
        """Estrategia por defecto: eager con include_extras=True."""
        return cls(mode=cls.EAGER, include_extras=True)


# ---------------------------------------------------------------------------
# Resolvedor principal
# ---------------------------------------------------------------------------

class AnnotationResolver:
    """
    Resuelve anotaciones de tipos desde cualquier objeto Python (clase, función,
    módulo) de forma robusta, manejando:

    - PEP 563 (from __future__ import annotations → strings)
    - PEP 649 (Python 3.14+ lazy annotations via annotationlib)
    - ForwardRefs no resueltas
    - classmethod / staticmethod / property
    - Herencia (MRO completo opcional)
    - inspect.get_annotations vs typing.get_type_hints

    Uso::

        resolver = AnnotationResolver()
        result = resolver.resolve(MyClass)
        # → dict[str, tipo_evaluado]
    """

    def __init__(self, strategy: EvalStrategy | None = None) -> None:
        self.strategy = strategy or EvalStrategy.default()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def resolve(
        self,
        obj: Any,
        *,
        follow_mro: bool = False,
    ) -> dict[str, Any]:
        """
        Resuelve todas las anotaciones del objeto.

        Args:
            obj: clase, función, módulo, o instancia con __class__.
            follow_mro: si True, recorre el MRO completo acumulando
                        anotaciones (las subclases sobreescriben las base).

        Returns:
            dict nombre → tipo (evaluado según la estrategia).
        """
        target = self._normalize_target(obj)

        if follow_mro and isinstance(target, type):
            return self._resolve_with_mro(target)

        return self._resolve_single(target)

    def resolve_param(self, func: Callable[..., Any], name: str) -> Any | None:
        """
        Resuelve la anotación de un parámetro específico de una función.
        Retorna None si el parámetro no tiene anotación.
        """
        hints = self.resolve(func)
        return hints.get(name)

    def resolve_return(self, func: Callable[..., Any]) -> Any | None:
        """
        Resuelve el tipo de retorno de una función.
        Retorna None si no hay anotación de retorno.
        """
        hints = self.resolve(func)
        return hints.get("return")

    def is_evaluable(self, obj: Any) -> bool:
        """
        Indica si el objeto tiene anotaciones resolubles sin errores.
        Útil para hacer preflight checks.
        """
        try:
            self.resolve(obj)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _normalize_target(self, obj: Any) -> Any:
        """
        Normaliza el objeto para que sea un target válido de resolución.
        Maneja: classmethod, staticmethod, property, instancias.
        """
        # classmethod / staticmethod → extraer __func__
        if isinstance(obj, classmethod):
            return obj.__func__
        if isinstance(obj, staticmethod):
            return obj.__func__
        # property → inspeccionar el getter
        if isinstance(obj, property):
            return obj.fget
        # instancia (no clase, no función, no módulo) → usar su clase
        if (
            not isinstance(obj, type)
            and not callable(obj)
            and not inspect.ismodule(obj)
            and hasattr(obj, "__class__")
        ):
            return obj.__class__
        return obj

    def _resolve_single(self, obj: Any) -> dict[str, Any]:
        """
        Resuelve anotaciones de un único objeto usando la estrategia configurada.
        Aplica múltiples fallbacks en orden de preferencia.
        """
        strategy = self.strategy

        if strategy.mode == EvalStrategy.STRING:
            # Devolvemos las anotaciones sin evaluar
            return self._get_raw_annotations(obj)

        if strategy.mode == EvalStrategy.LAZY:
            # Solo evalúa lo que ya es un objeto tipo real, deja strings/ForwardRefs
            raw = self._get_raw_annotations(obj)
            return {k: self._soft_eval(v, obj) for k, v in raw.items()}

        # EAGER: intentar evaluación completa con varios fallbacks
        return self._resolve_eager(obj, strategy)

    def _resolve_eager(self, obj: Any, strategy: EvalStrategy) -> dict[str, Any]:
        """
        Intenta resolver anotaciones en modo eager.
        Orden de intento:
          1. annotationlib (Python 3.14+) si disponible
          2. typing.get_type_hints (más completo, resuelve ForwardRefs)
          3. inspect.get_annotations(eval_str=True) (3.10+)
          4. __annotations__ raw + eval manual con namespace del módulo
        """
        # --- 1. annotationlib (3.14+) ---
        if HAS_ANNOTATIONLIB:
            result = self._try_annotationlib(obj, strategy)
            if result is not None:
                return result

        # --- 2. typing.get_type_hints ---
        result = self._try_get_type_hints(obj, strategy)
        if result is not None:
            return result

        # --- 3. inspect.get_annotations ---
        result = self._try_inspect_get_annotations(obj)
        if result is not None:
            return result

        # --- 4. Fallback: raw + eval manual ---
        return self._resolve_raw_with_eval(obj, strategy)

    def _try_annotationlib(
        self, obj: Any, strategy: EvalStrategy
    ) -> dict[str, Any] | None:
        """Usa annotationlib de Python 3.14 si está disponible."""
        try:
            import annotationlib  # type: ignore[import]
            format_ = annotationlib.Format.VALUE  # type: ignore[attr-defined]
            hints = annotationlib.get_annotations(  # type: ignore[attr-defined]
                obj,
                format=format_,
                eval_str=True,
            )
            if not strategy.include_extras:
                hints = {k: typing._strip_extras(v) for k, v in hints.items()}  # type: ignore[attr-defined]
            return hints
        except Exception:
            return None

    def _try_get_type_hints(
        self, obj: Any, strategy: EvalStrategy
    ) -> dict[str, Any] | None:
        """Usa typing.get_type_hints con namespace del módulo del objeto."""
        try:
            globalns = strategy.globalns
            localns = strategy.localns

            # Si no se provee globalns, intentamos obtener el módulo del objeto
            if globalns is None:
                module_name = getattr(obj, "__module__", None)
                if module_name and module_name in sys.modules:
                    globalns = vars(sys.modules[module_name])

            return typing.get_type_hints(
                obj,
                globalns=globalns,
                localns=localns,
                include_extras=strategy.include_extras,
            )
        except Exception:
            return None

    def _try_inspect_get_annotations(self, obj: Any) -> dict[str, Any] | None:
        """Usa inspect.get_annotations disponible desde Python 3.10."""
        if not hasattr(inspect, "get_annotations"):
            return None
        try:
            return inspect.get_annotations(obj, eval_str=True)
        except Exception:
            return None

    def _resolve_raw_with_eval(
        self, obj: Any, strategy: EvalStrategy
    ) -> dict[str, Any]:
        """
        Fallback final: toma __annotations__ crudo y evalúa strings manualmente.
        Construye el namespace de evaluación con typing + módulo del objeto.
        """
        raw = self._get_raw_annotations(obj)
        if not raw:
            return {}

        ns = self._build_eval_namespace(obj, strategy)

        result: dict[str, Any] = {}
        for name, annotation in raw.items():
            if isinstance(annotation, str):
                try:
                    result[name] = eval(annotation, ns)  # noqa: S307
                except Exception:
                    # Si no podemos evaluar, dejamos el ForwardRef
                    result[name] = typing.ForwardRef(annotation)
            elif isinstance(annotation, typing.ForwardRef):
                try:
                    result[name] = annotation._evaluate(ns, None, frozenset())
                except Exception:
                    result[name] = annotation
            else:
                result[name] = annotation

        if not strategy.include_extras:
            result = {k: typing._strip_extras(v) for k, v in result.items()}  # type: ignore[attr-defined]

        return result

    def _soft_eval(self, annotation: Any, obj: Any) -> Any:
        """Evaluación suave: solo resuelve ForwardRefs triviales, deja strings."""
        if isinstance(annotation, typing.ForwardRef):
            try:
                ns = self._build_eval_namespace(obj, self.strategy)
                return annotation._evaluate(ns, None, frozenset())
            except Exception:
                return annotation
        return annotation

    def _get_raw_annotations(self, obj: Any) -> dict[str, Any]:
        """Obtiene __annotations__ sin evaluar, nunca falla."""
        return getattr(obj, "__annotations__", {}).copy()

    def _build_eval_namespace(
        self, obj: Any, strategy: EvalStrategy
    ) -> dict[str, Any]:
        """
        Construye el namespace para eval(), combinando:
        - builtins de typing
        - módulo del objeto
        - globalns/localns provistos por el usuario
        """
        ns: dict[str, Any] = {}

        # Base: todo lo de typing
        ns.update(vars(typing))

        # Módulo del objeto
        module_name = getattr(obj, "__module__", None)
        if module_name and module_name in sys.modules:
            ns.update(vars(sys.modules[module_name]))

        # Overrides del usuario
        if strategy.globalns:
            ns.update(strategy.globalns)
        if strategy.localns:
            ns.update(strategy.localns)

        return ns

    def _resolve_with_mro(self, cls: type) -> dict[str, Any]:
        """
        Recorre el MRO en orden inverso (base primero) y acumula anotaciones.
        Las clases más específicas sobreescriben las de las base.
        """
        accumulated: dict[str, Any] = {}

        # MRO en orden inverso: object → Base → Child
        for klass in reversed(cls.__mro__):
            if klass is object:
                continue
            # Solo anotaciones propias de esta clase (no heredadas)
            own_annotations = klass.__dict__.get("__annotations__", {})
            if not own_annotations:
                continue

            # Resolver solo las anotaciones propias de esta clase en su contexto
            try:
                resolved = self._resolve_single(klass)
                # Filtrar solo las que son de esta clase
                for name in own_annotations:
                    if name in resolved:
                        accumulated[name] = resolved[name]
            except Exception:
                # Fallback: tomar las raw
                accumulated.update(own_annotations)

        return accumulated
