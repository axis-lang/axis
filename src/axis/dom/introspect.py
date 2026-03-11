"""Introspection of Python type hints -> dom Types.

Provides an `Introspector` protocol and a `ContextVar`-based mechanism
for resolving nominal types into their structural fields.  This powers
the `dir`/`get` decomposition for opaque NominalType values whose
internal structure is known only through Python annotations.

Two-phase model
----------------
Phase 1 -- entry registration (at class-creation time):
    When a ``Builtin`` subclass is created, ``__class_post_build__``
    appends it to ``_PENDING_CLASSES``.  On the first introspection
    lookup, ``_drain_pending`` registers a ``BuiltinEntry`` keyed by
    ``dom.Anchor``.

Phase 2 -- specialization (at query time):
    ``NativeIntrospector.fields()`` looks up the ``BuiltinEntry`` by
    anchor. If the entry is generic, it substitutes placeholders using
    specialization data from the ``Spec`` and caches the resolved
    fields keyed by the full ``Spec``.
"""

from __future__ import annotations

from typing import ClassVar

from protobase import Record, frozendict, attr_info_of, mutate, Consed, cached_property
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
    cast,
)
from types import NoneType, UnionType as PEP604Union
from decimal import Decimal

from axis import dom
from .core import _PENDING_CLASSES



_ENTRIES_BY_ANCHOR: dict[dom.Anchor, BuiltinEntry] = {}
_RESOLVED_FIELDS_BY_SPEC: dict[dom.Spec, dom.Struct[str, dom.Type]] = {}

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
# Introspector protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class Introspector(Protocol):
    """Maps a ``NominalType`` to its named fields, or ``None`` if opaque."""

    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None: ...

    def class_for(self, type: dom.NominalType) -> type[dom.Builtin] | None: ...

# ---------------------------------------------------------------------------
# BuiltinEntry -- per-anchor builtin registration entry (replaces Bound)
# ---------------------------------------------------------------------------

class BuiltinEntry(dom.ContextProto, Consed):
    """Entry in the introspection registry for a Builtin class.
    
    Serves as both the registration record and the ContextProto for
    generic variables created from this builtin's TypeVar annotations.
    
    Replaces the old Bound dataclass with a richer, cached structure.
    """
    anchor: dom.Anchor
    builtin_cls: type[dom.Builtin]
    
    def lookup_bound(self, name: str) -> dom.Type | None:
        """ContextProto implementation. Returns None by default.
        
        Could be enhanced to return TypeVar bounds/constraints in the future.
        """
        return None
    
    @cached_property
    def template(self) -> tuple[dom.Struct[str, dom.Type], frozenset[dom.Var]]:
        """Compute the field template with tracked generic vars.
        
        Returns (fields, vars) tuple computed from the builtin class annotations.
        """
        attrs = attr_info_of(self.builtin_cls)
        if not attrs:
            return dom.Struct.Empty, frozenset()
        
        vars: set[dom.Var] = set()
        field_dict: dict[str, dom.Type] = {}
        for name, attr_info in attrs.items():
            field_dict[name] = _python_to_axis_type(attr_info.type, ctx=self, vars=vars)
        
        struct = dom.Struct.new(**field_dict)
        return struct, frozenset(vars)
    
    @property  
    def fields(self) -> dom.Struct[str, dom.Type]:
        """Field structure with generic placeholders."""
        return self.template[0]
    
    @property
    def vars(self) -> frozenset[dom.Var]:
        """Set of generic Var instances that appear in fields."""
        return self.template[1]
    
    @property
    def is_generic(self) -> bool:
        """True if this builtin has generic type parameters."""
        return bool(self.vars)


# ---------------------------------------------------------------------------
# VarGenericType -- metatype for Python TypeVar placeholders
# ---------------------------------------------------------------------------

class VarGenericType(dom.VarType[BuiltinEntry]):
    """Metatype created during phase-1 introspection for ``TypeVar`` fields."""
    ANCHOR: ClassVar[str] = "dom.Type.Var.Generic"



# ---------------------------------------------------------------------------
# Generic substitution (phase 2)
# ---------------------------------------------------------------------------

def _resolve_generics(
    entry: BuiltinEntry,
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

        return entry.fields.map(substitute_any)

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

    return entry.fields.map(substitute)


# ---------------------------------------------------------------------------
# NativeIntrospector
# ---------------------------------------------------------------------------

class NativeIntrospector(Record):
    """Default introspector backed by ``_ENTRIES_BY_ANCHOR``."""

    def fields(self, type: dom.NominalType) -> dom.Struct[str, dom.Type] | None:
        _drain_pending()

        spec = type.spec_ref
        anchor = spec.anchor
        anchor_path = ".".join(anchor.data)

        if anchor_path in _LITERAL_ANCHORS:
            return None

        # Fast path: already resolved for this exact spec.
        cached = _RESOLVED_FIELDS_BY_SPEC.get(spec)
        if cached is not None:
            return cached

        entry = _ENTRIES_BY_ANCHOR.get(anchor)
        if entry is None:
            return None

        if not entry.is_generic:
            return entry.fields

        # Phase 2: substitute generics from specialization.
        resolved_fields = _resolve_generics(entry, spec)
        _RESOLVED_FIELDS_BY_SPEC[spec] = resolved_fields

        return resolved_fields

    def class_for(self, type: dom.NominalType) -> type[dom.Builtin] | None:
        """Return the Python class for a NominalType, or None if not registered."""
        _drain_pending()
        
        spec = type.spec_ref
        anchor = spec.anchor
        entry = _ENTRIES_BY_ANCHOR.get(anchor)
        
        return entry.builtin_cls if entry is not None else None


DEFAULT_INTROSPECTOR: Introspector = NativeIntrospector()

INTROSPECTOR: ContextVar[Introspector | None] = ContextVar(
    "axis.dom.introspect.INTROSPECTOR",
    default=DEFAULT_INTROSPECTOR,
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
    ctx: dom.ContextProto,
    vars: set[dom.Var] | None = None,
) -> dom.Type:
    """Convert a Python type annotation to an axis.dom Type.

    Args:
        annotation: Python type annotation to convert
        ctx: Context for any generic variables created
        vars: Optional set to collect created Var instances
    """
    if annotation is Any:
        return dom.ANY_TYPE

    if isinstance(annotation, TypeVar):
        var = dom.var(dom.VarGenericType, ctx, annotation.__name__) # type: ignore
        if vars is not None:
            vars.add(var)
        return var

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        return dom._union_type(
            *[_python_to_axis_type(arg, ctx, vars) for arg in args]
        )

    # Scalar mappings (no children to recurse into).
    scalar = _SCALAR_TYPES.get(annotation)
    if scalar is not None:
        return scalar

    # Generic types with parameters -> registry lookup.
    if origin is not None:
        return _transform_generic(origin, args, ctx, vars)

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


class _TypeBuildContext(dom.ContextProto):
    """Context used to project explicit Builtin type arguments."""

    def lookup_bound(self, name: str) -> dom.Type | None:
        return None


_TYPE_BUILD_CTX = _TypeBuildContext()


def _coerce_builtin_type_arg(arg: type | dom.Type) -> dom.Type:
    """Project a Builtin type argument to ``dom.Type``."""
    if isinstance(arg, dom.Type):
        return arg

    projected = _python_to_axis_type(arg, ctx=_TYPE_BUILD_CTX)
    if projected is dom.ANY_TYPE and arg is not Any:
        raise TypeError(f"Cannot project Builtin type argument {arg!r} to dom.Type")
    return projected


def _validate_builtin_type_arg(
    param: TypeVar,
    raw_arg: type | dom.Type,
    projected_arg: dom.Type,
) -> None:
    """Validate one TypeVar binding.

    Bounds/constraints validation is intentionally deferred. This function
    is the integration point for the next iteration.
    """
    _ = (param, raw_arg, projected_arg)


def _build_builtin_type(
    builtin_cls: type[dom.Builtin],
    *args: type | dom.Type,
) -> dom.Type:
    """Build the ``dom.Type`` descriptor for a Builtin class.

    Arity is strict: explicit type arguments must match the class TypeVars.
    """
    parameters = tuple(getattr(builtin_cls, "__parameters__", ()))
    expected = len(parameters)
    received = len(args)

    if expected == 0:
        if received != 0:
            raise TypeError(
                f"{builtin_cls.__name__} expects no type arguments, got {received}"
            )
        return dom._nominal_type(builtin_cls._anchor_path())

    if received != expected:
        raise TypeError(
            f"{builtin_cls.__name__} expects {expected} type arguments, got {received}"
        )

    projected_args = tuple(_coerce_builtin_type_arg(arg) for arg in args)

    bindings: dict[str, dom.Type] = {}
    for param, raw_arg, projected_arg in zip(parameters, args, projected_args):
        if isinstance(param, TypeVar):
            _validate_builtin_type_arg(param, raw_arg, projected_arg)

        name = getattr(param, "__name__", None)
        if not isinstance(name, str):
            raise TypeError(
                f"Unsupported type parameter {param!r} in {builtin_cls.__name__}"
            )
        bindings[name] = projected_arg

    spec = _spec_from_types(**bindings)
    return dom._nominal_type(builtin_cls._anchor_path(), spec)


def _builtin_runtime_type_args(value: dom.Builtin) -> tuple[type | dom.Type, ...] | None:
    """Extract explicit runtime type args from a generic Builtin instance.

    Uses ``__orig_class__`` when present (e.g. ``Box[int](...)``). Returns
    None when runtime args are unavailable.
    """
    orig_class = getattr(value, "__orig_class__", None)
    if orig_class is None:
        return None

    origin = get_origin(orig_class)
    if origin is None or not isinstance(origin, type):
        return None
    if origin is not value.__class__:
        return None

    runtime_args = get_args(orig_class)
    if not runtime_args:
        return ()

    extracted: list[type | dom.Type] = []
    for arg in runtime_args:
        if isinstance(arg, dom.Type):
            extracted.append(arg)
        elif isinstance(arg, type):
            extracted.append(arg)
        else:
            return None
    return tuple(extracted)


def _transform_generic(
    origin: object,
    args: tuple[Any, ...],
    ctx: dom.ContextProto,
    vars: set[dom.Var] | None,
) -> dom.Type:
    """Project a generic Python type via the transform registry."""
    transform = _PY_TO_AX_TRANSFORMS.get(origin)
    if transform is not None:
        converted = tuple(
            _python_to_axis_type(arg, ctx, vars) if arg is not Ellipsis else arg
            for arg in args
        )
        return transform(*converted)

    # Builtin generic aliases delegate to Builtin._type().
    if isinstance(origin, type) and issubclass(origin, dom.Builtin):
        builtin_origin = cast(type[dom.Builtin], origin)
        return builtin_origin._type(*cast(tuple[type | dom.Type, ...], args))

    return dom.ANY_TYPE


def _try_builtin_mapping(annotation: type) -> dom.Type:
    """Map a Python class to an Axis nominal type via the introspection registry."""
    _drain_pending()

    if issubclass(annotation, dom.Builtin):
        builtin_cls = cast(type[dom.Builtin], annotation)
        return builtin_cls._type()

    return dom.ANY_TYPE


# ---------------------------------------------------------------------------
# Lazy introspection drain (phase 1)
# ---------------------------------------------------------------------------

def _drain_pending() -> None:
    """Process pending Builtin classes into ``_ENTRIES_BY_ANCHOR``."""
    if not _PENDING_CLASSES:
        return

    while _PENDING_CLASSES:
        cls = _PENDING_CLASSES.pop()
        anchor = dom._anchor(cls._anchor_path())
        entry = BuiltinEntry(anchor=anchor, builtin_cls=cls)
        _ENTRIES_BY_ANCHOR[anchor] = entry


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def _spec_from_types(**bindings: dom.Type) -> dom.Const | None:
    """Build a specialization ``Const[StructType]`` from named type bindings."""
    if not bindings:
        return None
    return dom._struct(
        **{
            name: cast(dom.Pure | dom.Var, dom.val(t))
            for name, t in bindings.items()
        }
    )


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

    _map = lambda K, V: dom._nominal_qual(
        'std.Map', _spec_from_types(K=K), underlying=V,
    )

    _list = lambda T: dom._nominal_qual(
        'std.List', _spec_from_types(), underlying=T,
    )

    register_py_to_ax(
        dom.Struct,
        lambda K, V: dom._nominal_qual(
            'Struct', _spec_from_types(K=K), underlying=V,
        ),
    )
    register_py_to_ax(
        frozendict,
        _map,
    )
    register_py_to_ax(dict, _map)
    register_py_to_ax(list, _list)
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
