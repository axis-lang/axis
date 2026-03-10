"""Introspection of Python type hints -> dom Types.

Provides an `Introspector` protocol and a `ContextVar`-based mechanism
for resolving nominal types into their structural fields.  This powers
the `dir`/`get` decomposition for opaque NominalType values whose
internal structure is known only through Python annotations.

Two-phase model
----------------
Phase 1 -- template registration (at class-creation time):
    When a ``Builtin`` subclass is created, ``__class_post_build__``
    appends it to ``_PENDING_CLASSES``.  On the first introspection
    lookup, ``_drain_pending`` processes them: each field annotation is
    converted via ``_python_to_axis_type`` (which maps ``TypeVar`` ->
    ``Var.generic`` placeholders), and the result is stored as a
    ``Bound`` keyed by ``dom.Anchor``.

Phase 2 -- specialization (at query time):
    ``NativeIntrospector.fields()`` looks up the ``Bound`` by anchor.
    If the bound carries generic vars, it substitutes them using the
    specialization data from the ``Spec`` and caches the resolved
    result keyed by the full ``Spec``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from protobase import Record, frozendict, attr_info_of, mutate
from protobase.inmutable import register_inmutable
from contextvars import ContextVar
from typing import (
    Protocol,
    runtime_checkable,
    get_origin,
    get_args,
    Any,
    Callable,
    TypeVar,
    Union,
)
from types import NoneType, UnionType as PEP604Union
from decimal import Decimal

from axis import dom
from .core import _PENDING_CLASSES


# ---------------------------------------------------------------------------
# Introspector protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class Introspector(Protocol):
    """Maps a ``NominalType`` to its named fields, or ``None`` if opaque."""

    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None: ...


# ---------------------------------------------------------------------------
# IntrospectionContext — implements ContextProto for generic type vars
# ---------------------------------------------------------------------------

class IntrospectionContext(dom.ContextProto):
    """Context for generic type variables created during introspection.

    Implements ContextProto. Since introspection-phase variables are
    placeholders (resolved later via specialization), lookup_bound
    always returns None.

    The anchor is created lazily to avoid circular import issues
    (dom._anchor is not available when introspect.py is first imported
    from dom/__init__.py).
    """

    # _SINGLETON_ANCHOR: dom.Anchor | None = None

    # @classmethod
    # def _get_anchor(cls) -> dom.Anchor:
    #     if cls._SINGLETON_ANCHOR is None:
    #         cls._SINGLETON_ANCHOR = dom.Anchor(
    #             data=("dom", "introspect")
    #         )
    #     return cls._SINGLETON_ANCHOR

    # @property
    # def anchor(self) -> dom.Anchor:
    #     return self._get_anchor()

    def lookup_bound(self, name: str) -> dom.Type | None:
        return None

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, other):
        return self is other


# Singleton context for all introspection-phase variables
_INTROSPECTION_CTX = IntrospectionContext()


# ---------------------------------------------------------------------------
# VarGenericType -- metatype for Python TypeVar placeholders
# ---------------------------------------------------------------------------

class VarGenericType(dom.VarType):
    """Metatype created during phase-1 introspection for ``TypeVar`` fields."""
    ANCHOR: ClassVar[str] = "dom.Type.Var.Generic"

    @property
    def __type__(self) -> dom.Type:
        return dom._nominal_type("dom.Type.Var.Generic")


# ---------------------------------------------------------------------------
# Bound -- per-anchor field template (phase 1 output)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Bound:
    """Field structure of a Builtin, with tracked generic placeholders.

    ``vars`` is the set of ``Var`` instances that appear in
    ``fields``.  When empty, the bound is fully concrete and can be
    returned as-is.
    """
    fields: dom.Struct[str, dom.Type]
    vars: frozenset[dom.Var]

    @property
    def is_generic(self) -> bool:
        return bool(self.vars)


_BOUNDS_BY_ANCHOR: dict[dom.Anchor, Bound] = {}
_BOUNDS_BY_SPEC: dict[dom.Spec, Bound] = {}

_LITERAL_ANCHORS = {
    "std.Integer",
    "std.Text",
    "std.Boolean",
    "std.Decimal",
    "std.Empty",
    "std.Natural",
    "std.Whole",
}


# ---------------------------------------------------------------------------
# Generic substitution (phase 2)
# ---------------------------------------------------------------------------

def _resolve_generics(
    bound: Bound,
    spec: dom.Spec,
) -> dom.Struct[str, dom.Type]:
    """Substitute ``Var`` placeholders using specialization data.

    If the spec carries no specialization, all placeholders are
    replaced with ``dom.ANY_TYPE``.
    """
    specialization = spec.specialization
    if specialization is None:
        # No specialization: replace all Var with ANY_TYPE
        def substitute_any(field_type: dom.Type) -> dom.Type:
            if isinstance(field_type, dom.Var):
                return dom.ANY_TYPE

            # Recursive cases for container types
            if isinstance(field_type, dom.NominalQualifier):
                new_underlying = substitute_any(field_type.underlying)
                if new_underlying is field_type.underlying:
                    return field_type
                return mutate(field_type, underlying=new_underlying)

            if isinstance(field_type, dom.StructType):
                new_fields = field_type.fields.map(substitute_any)
                if new_fields is field_type.fields:
                    return field_type
                return mutate(field_type, fields=new_fields)

            if isinstance(field_type, dom.UnionType):
                new_types = frozenset(substitute_any(t) for t in field_type.types)
                if new_types == field_type.types:
                    return field_type
                return dom.UnionType(types=new_types)

            return field_type

        return bound.fields.map(substitute_any)

    # Build a keyed view over the specialization data so we can look up
    # bindings by name (e.g. "T" -> INTEGER_TYPE).
    spec_data = dom.Struct(
        index=specialization.type.fields.index,
        values=specialization.data,
    )

    def substitute(field_type: dom.Type) -> dom.Type:
        # Base case: substitute Var
        if isinstance(field_type, dom.Var):
            binding = spec_data.get(field_type.data, default=None)
            return binding if isinstance(binding, dom.Type) else dom.ANY_TYPE

        # Recursive cases for container types
        if isinstance(field_type, dom.NominalQualifier):
            new_underlying = substitute(field_type.underlying)
            if new_underlying is field_type.underlying:
                return field_type
            return mutate(field_type, underlying=new_underlying)

        if isinstance(field_type, dom.StructType):
            new_fields = field_type.fields.map(substitute)
            if new_fields is field_type.fields:
                return field_type
            return mutate(field_type, fields=new_fields)

        if isinstance(field_type, dom.UnionType):
            new_types = frozenset(substitute(t) for t in field_type.types)
            if new_types == field_type.types:
                return field_type
            return dom.UnionType(types=new_types)

        # Other types pass through unchanged
        return field_type

    return bound.fields.map(substitute)


# ---------------------------------------------------------------------------
# NativeIntrospector
# ---------------------------------------------------------------------------

class NativeIntrospector(Record):
    """Default introspector backed by ``_BOUNDS_BY_ANCHOR``."""

    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None:
        _drain_pending()

        spec = type.spec_ref
        anchor = spec.anchor
        anchor_path = ".".join(anchor.data)

        if anchor_path in _LITERAL_ANCHORS:
            return None

        # Fast path: already resolved for this exact spec.
        cached = _BOUNDS_BY_SPEC.get(spec)
        if cached is not None:
            return cached.fields

        bound = _BOUNDS_BY_ANCHOR.get(anchor)
        if bound is None:
            return None

        if not bound.is_generic:
            return bound.fields

        # Phase 2: substitute generics from specialization.
        resolved_fields = _resolve_generics(bound, spec)
        resolved = Bound(fields=resolved_fields, vars=frozenset())
        _BOUNDS_BY_SPEC[spec] = resolved

        return resolved_fields


INTROSPECTOR: ContextVar[Introspector | None] = ContextVar(
    "axis.dom.introspect.INTROSPECTOR",
    default=NativeIntrospector(),
)


# ---------------------------------------------------------------------------
# PyAx interop: Python -> Axis type projection registry
# ---------------------------------------------------------------------------

_PY_TO_AX_TRANSFORMS: dict[object, Callable[..., dom.Type]] = {}


def register_py_to_ax(origin: object, transform: Callable[..., dom.Type]) -> None:
    """Register a Python origin type -> Axis type transform.

    The *transform* receives type arguments already converted to
    ``dom.Type`` via ``_python_to_axis_type`` (except ``Ellipsis``,
    which passes through unchanged so transforms can distinguish
    e.g. ``tuple[int, ...]`` from ``tuple[int]``).
    """
    _PY_TO_AX_TRANSFORMS[origin] = transform


# ---------------------------------------------------------------------------
# Python type annotation -> dom.Type conversion
# ---------------------------------------------------------------------------

def _python_to_axis_type(
    annotation: Any,
    vars: set[dom.Var] | None = None,
) -> dom.Type:
    """Convert a Python type annotation to an axis.dom Type.

    When *vars* is provided, any ``Var`` created for a
    ``TypeVar`` is added to the set so the caller can build the
    ``Bound.vars`` frozenset without a post-hoc scan.
    """
    if annotation is Any:
        return dom.ANY_TYPE

    if isinstance(annotation, TypeVar):

        var = dom.var(dom.VarGenericType, _INTROSPECTION_CTX, annotation.__name__)
        if vars is not None:
            vars.add(var)
        return var

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        return dom._union_type(
            *[_python_to_axis_type(arg, vars) for arg in args]
        )

    # Scalar mappings (no children to recurse into).
    scalar = _SCALAR_TYPES.get(annotation)
    if scalar is not None:
        return scalar

    # Generic types with parameters -> registry lookup.
    if origin is not None:
        return _transform_generic(origin, args, vars)

    # Named Builtin class -> introspection registry lookup.
    if isinstance(annotation, type):
        return _try_builtin_mapping(annotation)

    return dom.ANY_TYPE


_SCALAR_TYPES: dict[type, dom.Type] = {}


def _init_scalar_types() -> None:
    """Populate the scalar type table (called once at bootstrap)."""
    _SCALAR_TYPES.update({
        int: dom.INTEGER_TYPE,
        str: dom.TEXT_TYPE,
        bool: dom.BOOLEAN_TYPE,
        float: dom.DECIMAL_TYPE,
        Decimal: dom.DECIMAL_TYPE,
        NoneType: dom.EMPTY_TYPE,
    })


def _transform_generic(
    origin: type,
    args: tuple[Any, ...],
    vars: set[dom.Var] | None,
) -> dom.Type:
    """Project a generic Python type via the transform registry."""
    converted = tuple(
        _python_to_axis_type(arg, vars) if arg is not Ellipsis else arg
        for arg in args
    )

    transform = _PY_TO_AX_TRANSFORMS.get(origin)
    if transform is not None:
        return transform(*converted)

    return dom.ANY_TYPE


def _try_builtin_mapping(annotation: type) -> dom.Type:
    """Map a Python class to an Axis nominal type via the introspection registry."""
    _drain_pending()

    # Match by ANCHOR class attribute if the annotation is a Builtin subclass.
    anchor_str = getattr(annotation, "ANCHOR", None)
    if anchor_str is not None:
        anchor = dom._anchor(anchor_str)
        if anchor in _BOUNDS_BY_ANCHOR:
            return dom._nominal_type(anchor)

    return dom.ANY_TYPE


# ---------------------------------------------------------------------------
# Lazy introspection drain (phase 1)
# ---------------------------------------------------------------------------

def _drain_pending() -> None:
    """Process pending Builtin classes into ``_BOUNDS_BY_ANCHOR``."""
    if not _PENDING_CLASSES:
        return

    while _PENDING_CLASSES:
        cls = _PENDING_CLASSES.pop()
        attrs = attr_info_of(cls)
        if not attrs:
            continue

        vars: set[dom.Var] = set()
        field_dict: dict[str, dom.Type] = {}
        for name, attr_info in attrs.items():
            field_dict[name] = _python_to_axis_type(attr_info.type, vars)

        struct = dom.Struct.new(**field_dict)
        bound = Bound(fields=struct, vars=frozenset(vars))

        anchor = dom._anchor(cls.ANCHOR)
        _BOUNDS_BY_ANCHOR[anchor] = bound


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def _spec_from_types(**bindings: dom.Type) -> dom.Const | None:
    """Build a specialization ``Const[StructType]`` from named type bindings."""
    if not bindings:
        return None
    return dom._struct(**{name: t.as_val for name, t in bindings.items()})


def _tuple_transform(*args: dom.Type) -> dom.Type:
    """``tuple[V, ...]`` -> ``std.List V``  |  ``tuple[A, B, C]`` -> ``StructType``."""
    if len(args) == 2 and args[1] is Ellipsis:
        element = args[0]
        return dom._nominal_qual(
            'std.List', _spec_from_types(), underlying=element,
        )
    return dom.StructType(fields=dom.Struct.new(*args))


def _register_default_py_to_ax() -> None:
    """Populate the PyAx transform registry with standard mappings."""
    _set = lambda V: dom._nominal_qual(
        'std.Set', _spec_from_types(), underlying=V,
    )

    register_py_to_ax(
        dom.Struct,
        lambda K, V: dom._nominal_qual(
            'Struct', _spec_from_types(K=K), underlying=V,
        ),
    )
    register_py_to_ax(
        frozendict,
        lambda K, V: dom._nominal_qual(
            'std.Map', _spec_from_types(K=K, V=V), underlying=V,
        ),
    )
    register_py_to_ax(set, _set)
    register_py_to_ax(frozenset, _set)
    register_py_to_ax(tuple, _tuple_transform)
    register_py_to_ax(PEP604Union, lambda *args: dom._union_type(*args))


def _bootstrap_introspection() -> None:
    """Initialize the introspection system.

    Registers default Python -> Axis type transforms and populates the
    scalar table.  The ``INTROSPECTOR`` ContextVar already defaults to
    a ``NativeIntrospector``, so no explicit ``set()`` is needed.
    """
    _init_scalar_types()
    _register_default_py_to_ax()
