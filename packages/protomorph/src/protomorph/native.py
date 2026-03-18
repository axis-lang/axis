from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import Any, Callable, TypeVar, Union, cast, get_args, get_origin

# Top-level runtime imports - needed for inheritance/descriptors
from protobase import Consed, flux, frozendict

# Import protomorph for internal use and type hints
import protomorph as pm

__all__ = [
    "NativeGenericVarType",
    "NativeRegistry", 
    "NativeBackend",
    "register_native_type",
    "register_python_type", 
    "register_atomic_layout",
    "type_from_python",
    "build_builtin_type", 
    "builtin_runtime_type_args",
]

# Type aliases
type PythonTransform = Callable[..., pm.Type]

# === Global State - Sources of Truth ===

# Mutable global mappings - single source of truth
_NATIVE_TYPES: dict[type, pm.Type] = {}
_PYTHON_TRANSFORMS: dict[type, PythonTransform] = {}
_ATOMIC_LAYOUTS: dict[str, pm.AtomicLayout] = {}

# Bootstrap guard
_BOOTSTRAPPED = False

# === Context Classes ===

class TypeBuildContext(pm.ContextProto):
    def lookup_bound(self, name: str) -> pm.Type | None:
        _ = name
        return None


class BuiltinContext(pm.ContextProto):
    builtin_cls: type[pm.Builtin]

    def lookup_bound(self, name: str) -> pm.Type | None:
        _ = name
        return None


class NativeGenericVarType(pm.VarType[pm.ContextProto]):
    ANCHOR = "std.types.NativeGenericVarType"


# === Singleton Registry ===

class NativeRegistry(Consed):
    """Singleton registry for native type mappings and builtin types.
    
    Uses protobase.flux for automatic cache invalidation and dependency tracking.
    All mutations happen through global register_* functions.
    """
    
    # === Flux Sources of Truth ===
    
    @flux.property
    def all_builtins(self) -> frozenset[type[pm.Builtin]]:
        """All builtin classes discovered during class construction."""
        return frozenset(pm.ALL_BUILTINS)
    
    @flux.property
    def native_types(self) -> frozendict[type, pm.Type]:
        """Native type mappings from global state"""
        return frozendict(_NATIVE_TYPES)
    
    @flux.property
    def python_transforms(self) -> frozendict[type, PythonTransform]:
        """Python transforms from global state"""
        return frozendict(_PYTHON_TRANSFORMS)
    
    @flux.property
    def atomic_layouts(self) -> frozendict[pm.Anchor, pm.AtomicLayout]:
        """Atomic layouts from global state"""
        return frozendict({
            pm.anchor(anchor_str): layout 
            for anchor_str, layout in _ATOMIC_LAYOUTS.items()
        })
    
    # === Flux Cached Queries ===
    
    @flux.method
    def template_for(self, builtin_cls: type[pm.Builtin]) -> tuple[pm.Struct[str, pm.Type], frozenset[pm.Var]]:
        """Get template for builtin class. Cached per class."""
        # Import here to avoid circulars  
        from protobase import attr_info_of
        
        attrs = attr_info_of(builtin_cls)
        if not attrs:
            return cast(pm.Struct[str, pm.Type], pm.Struct.Empty), frozenset()

        vars: set[pm.Var] = set()
        field_types: dict[str, pm.Type] = {}
        ctx = BuiltinContext(builtin_cls=builtin_cls)
        
        for name, attr_info in attrs.items():
            field_types[name] = type_from_python(
                attr_info.type,
                ctx=ctx,
                vars=vars,
                registry=self,
            )

        return pm.Struct.new(**field_types), frozenset(vars)
    
    @flux.method
    def class_for(self, type_: pm.NominalType) -> type[pm.Builtin] | None:
        """Get builtin class for nominal type. Cached per type."""
        anchor = type_.spec_ref.anchor
        
        # Look for builtin with matching anchor
        for builtin_cls in self.all_builtins:
            if pm.anchor(builtin_cls._anchor_path()) == anchor:
                return builtin_cls
        return None
    
    @flux.method
    def layout_for_spec(self, spec: pm.Spec) -> pm.Layout | None:
        """Compute layout for specific spec. Cached per spec."""
        anchor = spec.anchor
        
        # Try atomic layout first
        atomic_layout = self.atomic_layouts.get(anchor)
        if atomic_layout is not None:
            return atomic_layout
        
        # Try builtin layout
        builtin_cls = None
        for cls in self.all_builtins:
            if pm.anchor(cls._anchor_path()) == anchor:
                builtin_cls = cls
                break
        
        if builtin_cls is None:
            return None
        
        template, vars = self.template_for(builtin_cls)
        if not vars:
            return pm.StructLayout(fields=template, builtin_cls=builtin_cls)
        
        # Substitute type variables
        resolved = template.map(
            lambda field_type: self._substitute_type(field_type, spec, builtin_cls)
        )
        return pm.StructLayout(fields=resolved, builtin_cls=builtin_cls)
    
    # === Public Interface ===
    
    def layout(self, type_: pm.NominalType) -> pm.Layout | None:
        """Public layout method for nominal types."""
        return self.layout_for_spec(type_.spec_ref)
    
    def construct(self, type_: pm.NominalType, args: tuple[pm.Data, ...]) -> pm.Data:
        """Construct instance of builtin type."""
        resolved_layout = self.layout(type_)
        if not isinstance(resolved_layout, pm.StructLayout):
            raise ValueError(f"No materializable layout for {type_!r}")
        layout = resolved_layout
        builtin_cls = layout.builtin_cls
        if builtin_cls is None:
            raise ValueError(f"No materializable layout for {type_!r}")

        if len(args) != len(layout.fields):
            raise ValueError(
                f"Cannot construct {builtin_cls.__name__}: expected {len(layout.fields)} args, got {len(args)}"
            )

        attrs = {
            key: value
            for key, value in zip(layout.fields.index.keys, args)
            if key is not None
        }
        return cast(pm.Data, builtin_cls(**attrs))
    
    # === Private Helpers ===
    
    def _resolve_var(self, var: pm.Var, spec: pm.Spec, builtin_cls: type[pm.Builtin]) -> pm.Type:
        """Resolve type variable in builtin context."""
        if not isinstance(var.__type__, NativeGenericVarType):
            return var
        ctx = var.__type__.ctx
        if not isinstance(ctx, BuiltinContext) or ctx.builtin_cls is not builtin_cls:
            return var

        args = spec.args
        if args is None or args.index.is_empty:
            return _any_type()

        name = var.__data__
        if not isinstance(name, str):
            return _any_type()

        binding = args.get(name, default=None)
        # Import here to avoid circulars
        resolved = pm.as_type(binding)
        return resolved if resolved is not None else _any_type()

    def _substitute_spec(self, spec: pm.Spec, builtin_cls: type[pm.Builtin]) -> pm.Spec:
        """Substitute type variables in spec."""
        # Import here to avoid circulars
        return pm._subst_spec(
            spec,
            lambda value: (
                pm.val(self._resolve_var(value, spec, builtin_cls))
                if isinstance(value, pm.Var)
                else None
            ),
        )

    def _substitute_type(self, type_: pm.Type, spec: pm.Spec, builtin_cls: type[pm.Builtin]) -> pm.Type:
        """Substitute type variables in type."""
        # Import here to avoid circulars
        return pm._subst_type(
            type_,
            lambda value: (
                pm.val(self._resolve_var(value, spec, builtin_cls))
                if isinstance(value, pm.Var)
                else None
            ),
        )


# === Singleton Backend ===

class NativeBackend(pm.SemanticBridgeBase, Consed):
    """Singleton semantic bridge using global native registry."""
    
    registry: NativeRegistry
    
    def layout(self, type: pm.Type) -> pm.Layout | None:
        if isinstance(type, pm.NominalType):
            return self.registry.layout(type)
        return super().layout(type)

    def construct(self, type: pm.NominalType, args: tuple[pm.Data, ...]) -> pm.Data:
        return self.registry.construct(type, args)


# === Global Registration API with Flux Invalidation ===

def register_native_type(native_type: type, proto_type: pm.Type) -> None:
    """Register native type mapping globally."""
    _NATIVE_TYPES[native_type] = proto_type
    # Invalidate flux property
    NativeRegistry.native_types.invalidate_for(pm.NATIVE_REGISTRY)


def register_python_type(origin: type, transform: PythonTransform) -> None:
    """Register python transform globally."""  
    _PYTHON_TRANSFORMS[origin] = transform
    # Invalidate flux property
    NativeRegistry.python_transforms.invalidate_for(pm.NATIVE_REGISTRY)


def register_atomic_layout(anchor: str | pm.Anchor, layout: pm.AtomicLayout) -> None:
    """Register atomic layout globally."""
    if isinstance(anchor, pm.Anchor):
        anchor = anchor.path
    _ATOMIC_LAYOUTS[anchor] = layout
    # Invalidate flux property
    NativeRegistry.atomic_layouts.invalidate_for(pm.NATIVE_REGISTRY)


# === Type Conversion Functions ===

_TYPE_BUILD_CTX = TypeBuildContext()


def type_from_python(
    annotation: Any,
    *,
    ctx: pm.ContextProto | None = None,
    vars: set[pm.Var] | None = None,
    registry: NativeRegistry | None = None,
) -> pm.Type:
    """Convert Python type annotation to protomorph Type."""
    # Use global registry if none specified
    registry = registry if registry is not None else pm.NATIVE_REGISTRY
    ctx = _TYPE_BUILD_CTX if ctx is None else ctx

    if isinstance(annotation, pm.Type):
        return annotation

    if annotation is None:
        return _empty_type()

    if annotation is Any:
        return _any_type()

    if isinstance(annotation, TypeVar):
        var = cast(pm.Var, pm.Var(NativeGenericVarType(ctx=ctx), annotation.__name__))
        if vars is not None:
            vars.add(var)
        return var

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union or origin is PEP604Union:
        return union_type(*(type_from_python(arg, ctx=ctx, vars=vars, registry=registry) for arg in args))

    # Check native type mappings
    scalar = registry.native_types.get(annotation)
    if scalar is not None:
        return scalar

    if origin is not None:
        return _transform_generic(origin, args, ctx, vars, registry)

    if isinstance(annotation, type):
        if issubclass(annotation, pm.Builtin):
            return build_builtin_type(annotation, registry=registry)
        return _any_type()

    return _any_type()


def _transform_generic(
    origin: type,
    args: tuple[Any, ...],
    ctx: pm.ContextProto,
    vars: set[pm.Var] | None,
    registry: NativeRegistry,
) -> pm.Type:
    """Transform generic Python type to protomorph type."""
    transform = registry.python_transforms.get(origin)
    if transform is not None:
        converted = tuple(
            type_from_python(arg, ctx=ctx, vars=vars, registry=registry)
            if arg is not Ellipsis
            else arg
            for arg in args
        )
        return transform(*converted)

    if isinstance(origin, type) and issubclass(origin, pm.Builtin):
        return build_builtin_type(origin, *args, registry=registry)

    return _any_type()


def _coerce_builtin_type_arg(arg: object | pm.Type, registry: NativeRegistry) -> pm.Type:
    """Coerce builtin type argument to protomorph Type."""
    if isinstance(arg, pm.Type):
        return arg

    projected = type_from_python(arg, registry=registry)
    if projected is _any_type() and arg is not Any:
        raise TypeError(f"Cannot project Builtin type argument {arg!r} to protomorph.Type")
    return projected


def build_builtin_type(
    builtin_cls: type[pm.Builtin],
    *args: object | pm.Type,
    registry: NativeRegistry | None = None,
) -> pm.Type:
    """Build nominal type for builtin class."""
    # Use global registry if none specified
    registry = registry if registry is not None else pm.NATIVE_REGISTRY
    
    # Builtin auto-discovery ensures all builtins are registered
    # No need to check or register - they're automatically discovered

    parameters = tuple(getattr(builtin_cls, "__parameters__", ()))
    expected = len(parameters)
    received = len(args)

    if expected == 0:
        if received != 0:
            raise TypeError(f"{builtin_cls.__name__} expects no type arguments, got {received}")
        return nominal_type(builtin_cls._anchor_path())

    if received == 0:
        return nominal_type(builtin_cls._anchor_path())

    if received != expected:
        raise TypeError(f"{builtin_cls.__name__} expects {expected} type arguments, got {received}")

    projected_args = tuple(_coerce_builtin_type_arg(arg, registry) for arg in args)

    bindings: dict[str, pm.Type] = {}
    for param, projected_arg in zip(parameters, projected_args):
        name = getattr(param, "__name__", None)
        if not isinstance(name, str):
            raise TypeError(f"Unsupported type parameter {param!r} in {builtin_cls.__name__}")
        bindings[name] = projected_arg

    return nominal_type(builtin_cls._anchor_path(), _spec_from_types(**bindings))


def builtin_runtime_type_args(value: pm.Builtin) -> tuple[object | pm.Type, ...] | None:
    """Extract runtime type arguments from builtin instance."""
    orig_class = getattr(value, "__orig_class__", None)
    if orig_class is None:
        return None

    origin = get_origin(orig_class)
    if origin is None or not isinstance(origin, type) or origin is not value.__class__:
        return None

    runtime_args = get_args(orig_class)
    if not runtime_args:
        return ()

    extracted: list[object | pm.Type] = []
    for arg in runtime_args:
        if isinstance(arg, pm.Type) or isinstance(arg, type) or arg is Any:
            extracted.append(arg)
            continue

        if isinstance(arg, TypeVar) or get_origin(arg) is not None:
            extracted.append(arg)
            continue

        return None

    return tuple(extracted)


# === Helper Functions ===

def _spec_from_types(**bindings: pm.Type) -> pm.Const | None:
    """Create spec from type bindings."""
    if not bindings:
        return None

    return pm.struct(**{name: cast(pm.Const | pm.Var, pm.val(type_)) for name, type_ in bindings.items()})


def _tuple_transform(*args: pm.Type) -> pm.Type:
    """Transform tuple type annotation."""
    if len(args) == 2 and args[1] is Ellipsis:
        return nominal_qual("std.qualifiers.List", _spec_from_types(), underlying=args[0])
    return pm.StructType(meta_attrs=pm.Struct.new(*args))


def _any_type() -> pm.Type:
    """Get ANY_TYPE."""
    return pm.ANY_TYPE


def _empty_type() -> pm.Type:
    """Get EMPTY_TYPE."""  
    return pm.EMPTY_TYPE


def nominal_type(anchor: str, spec: pm.Const | None = None) -> pm.NominalType:
    """Create nominal type."""
    return pm.nominal_type(anchor, spec)


def nominal_qual(anchor: str, spec: pm.Const | None = None, *, underlying: pm.Type) -> pm.NominalQualifier:
    """Create nominal qualifier."""
    return pm.nominal_qual(anchor, spec, underlying=underlying)


def union_type(*types: pm.Type) -> pm.UnionType:
    """Create union type."""
    return pm.union_type(*types)
