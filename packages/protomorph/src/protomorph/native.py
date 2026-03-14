from __future__ import annotations

from decimal import Decimal
from types import NoneType, UnionType as PEP604Union
from typing import Any, Callable, TypeVar, Union, cast, get_args, get_origin

from protobase import Record, attr_info_of, frozendict, mutate

from .base import Builtin, Const, Data, _PENDING_BUILTINS
from .bridge import BRIDGE, DEFAULT_BRIDGE, SemanticBridgeBase
from .qualifiers import NominalQualifier
from .refs import Anchor, Spec
from .struct import Struct
from .types import NominalType, StructType, Type, UnionType
from .vars import ContextProto, Var, VarType

__all__ = [
    "NativeGenericVarType",
    "NativeRegistry",
    "NativeBackend",
    "DEFAULT_NATIVE_REGISTRY",
    "DEFAULT_NATIVE_BACKEND",
    "register_native_type",
    "register_python_type",
    "register_builtin",
    "drain_pending_builtins",
    "type_from_python",
    "build_builtin_type",
    "builtin_runtime_type_args",
]


type PythonTransform = Callable[..., Type]


class TypeBuildContext(ContextProto):
    def lookup_bound(self, name: str) -> Type | None:
        _ = name
        return None


class BuiltinContext(ContextProto):
    builtin_cls: type[Builtin]

    def lookup_bound(self, name: str) -> Type | None:
        _ = name
        return None


class NativeGenericVarType(VarType[ContextProto]):
    ANCHOR = "dom.Type.Var.Generic"


class NativeRegistry:
    def __init__(self) -> None:
        self.type_by_python: dict[object, Type] = {}
        self.python_transforms: dict[object, PythonTransform] = {}
        self.builtin_by_anchor: dict[Anchor, type[Builtin]] = {}
        self._templates_by_builtin: dict[
            type[Builtin], tuple[Struct[str, Type], frozenset[Var]]
        ] = {}
        self._resolved_fields_by_spec: dict[Spec, Struct[str, Type]] = {}
        self._drained_builtin_count = 0

    def register_native_type(self, native: object, type_: Type) -> None:
        self.type_by_python[native] = type_

    def register_python_type(self, origin: object, transform: PythonTransform) -> None:
        self.python_transforms[origin] = transform

    def register_builtin(self, builtin_cls: type[Builtin]) -> None:
        from . import api

        anchor = api.anchor(builtin_cls._anchor_path())
        self.builtin_by_anchor[anchor] = builtin_cls
        self._templates_by_builtin.pop(builtin_cls, None)
        self._resolved_fields_by_spec.clear()

    def drain_pending_builtins(self) -> None:
        pending = _PENDING_BUILTINS[self._drained_builtin_count :]
        if not pending:
            return

        self._drained_builtin_count = len(_PENDING_BUILTINS)
        for builtin_cls in pending:
            self.register_builtin(builtin_cls)

    def template_for(self, builtin_cls: type[Builtin]) -> tuple[Struct[str, Type], frozenset[Var]]:
        self.drain_pending_builtins()

        cached = self._templates_by_builtin.get(builtin_cls)
        if cached is not None:
            return cached

        attrs = attr_info_of(builtin_cls)
        if not attrs:
            template = cast(Struct[str, Type], Struct.Empty), frozenset()
            self._templates_by_builtin[builtin_cls] = template
            return template

        vars: set[Var] = set()
        field_types: dict[str, Type] = {}
        ctx = BuiltinContext(builtin_cls=builtin_cls)
        for name, attr_info in attrs.items():
            field_types[name] = type_from_python(
                attr_info.type,
                ctx=ctx,
                vars=vars,
                registry=self,
            )

        template = Struct.new(**field_types), frozenset(vars)
        self._templates_by_builtin[builtin_cls] = template
        return template

    def class_for(self, type_: NominalType) -> type[Builtin] | None:
        self.drain_pending_builtins()
        return self.builtin_by_anchor.get(type_.spec_ref.anchor)

    def fields(self, type_: NominalType) -> Struct[str, Type] | None:
        builtin_cls = self.class_for(type_)
        if builtin_cls is None:
            return None

        template, vars = self.template_for(builtin_cls)
        if not vars:
            return template

        spec = type_.spec_ref
        cached = self._resolved_fields_by_spec.get(spec)
        if cached is not None:
            return cached

        resolved = template.map(
            lambda field_type: self._substitute_type(field_type, spec, builtin_cls)
        )
        self._resolved_fields_by_spec[spec] = resolved
        return resolved

    def construct(self, type_: NominalType, args: tuple[Data, ...]) -> Data:
        builtin_cls = self.class_for(type_)
        if builtin_cls is None:
            raise ValueError(f"No registered builtin class for {type_!r}")

        fields = self.fields(type_)
        if fields is None:
            if args:
                raise ValueError(
                    f"Cannot construct {builtin_cls.__name__}: expected no args, got {len(args)}"
                )
            try:
                return cast(Data, builtin_cls())
            except Exception as exc:
                raise ValueError(
                    f"Cannot construct {builtin_cls.__name__} without args"
                ) from exc

        if len(args) != len(fields):
            raise ValueError(
                f"Cannot construct {builtin_cls.__name__}: expected {len(fields)} args, got {len(args)}"
            )

        attrs: dict[str, Data] = {}
        for key, value in zip(fields.index.keys, args):
            if key is None:
                raise ValueError(
                    f"Cannot construct {builtin_cls.__name__}: positional fields are unsupported"
                )
            attrs[key] = value

        try:
            return cast(Data, builtin_cls(**attrs))
        except Exception as exc:
            raise ValueError(
                f"Cannot construct {builtin_cls.__name__} from {attrs!r}"
            ) from exc

    def _matches_builtin_context(self, var: Var, builtin_cls: type[Builtin]) -> bool:
        if not isinstance(var.type, NativeGenericVarType):
            return False
        ctx = var.type.ctx
        return isinstance(ctx, BuiltinContext) and ctx.builtin_cls is builtin_cls

    def _resolve_var(self, var: Var, spec: Spec, builtin_cls: type[Builtin]) -> Type:
        from . import api

        if not self._matches_builtin_context(var, builtin_cls):
            return var

        args = spec.args
        if args is None:
            return api.ANY_TYPE

        binding = args.get(cast(str, var.data), default=None)
        if isinstance(binding, Var):
            return binding
        if isinstance(binding, Const) and isinstance(binding.data, Type):
            return cast(Type, binding.data)
        return api.ANY_TYPE

    def _substitute_value(
        self,
        value: Const | Var,
        spec: Spec,
        builtin_cls: type[Builtin],
    ) -> Const | Var:
        from . import api

        if isinstance(value, Var):
            substituted = self._substitute_type(value, spec, builtin_cls)
            return cast(Const | Var, api.val(substituted))

        if isinstance(value, Const) and isinstance(value.data, Type):
            substituted = self._substitute_type(cast(Type, value.data), spec, builtin_cls)
            if substituted is value.data:
                return value
            return cast(Const | Var, api.val(substituted))

        return value

    def _substitute_spec(self, spec: Spec, builtin_cls: type[Builtin]) -> Spec:
        from . import api

        args = spec.args
        if args is None:
            return spec

        positional: list[Const | Var] = []
        nominal: dict[str, Const | Var] = {}
        changed = False
        for key, value in zip(args.index.keys, args.values):
            typed = cast(Const | Var, value)
            substituted = self._substitute_value(typed, spec, builtin_cls)
            if substituted is not typed:
                changed = True
            if key is None:
                positional.append(substituted)
            else:
                nominal[key] = substituted

        if not changed:
            return spec

        return api.spec_ref(spec.anchor, api.struct(*positional, **nominal))

    def _substitute_type(self, type_: Type, spec: Spec, builtin_cls: type[Builtin]) -> Type:
        if isinstance(type_, Var):
            return self._resolve_var(type_, spec, builtin_cls)

        if isinstance(type_, NominalQualifier):
            new_spec = self._substitute_spec(type_.spec_ref, builtin_cls)
            new_underlying = self._substitute_type(type_.underlying, spec, builtin_cls)
            if new_spec is type_.spec_ref and new_underlying is type_.underlying:
                return type_
            return mutate(type_, spec_ref=new_spec, underlying=new_underlying)

        if isinstance(type_, NominalType):
            new_spec = self._substitute_spec(type_.spec_ref, builtin_cls)
            if new_spec is type_.spec_ref:
                return type_
            return mutate(type_, spec_ref=new_spec)

        if isinstance(type_, StructType):
            new_attrs = type_.meta_attrs.map(
                lambda meta_attr: self._substitute_type(meta_attr, spec, builtin_cls)
            )
            if new_attrs is type_.meta_attrs:
                return type_
            return mutate(type_, meta_attrs=new_attrs)

        if isinstance(type_, UnionType):
            new_types = frozenset(
                self._substitute_type(member, spec, builtin_cls)
                for member in type_.types
            )
            if new_types == type_.types:
                return type_
            return UnionType(types=new_types)

        return type_


class NativeBackend(SemanticBridgeBase, Record):
    registry: NativeRegistry

    def fields(self, type: Type) -> Struct[str, Type] | None:
        if isinstance(type, NominalType):
            return self.registry.fields(type)
        return None

    def class_for(self, type: NominalType) -> type[Builtin] | None:
        return self.registry.class_for(type)

    def construct(self, type: NominalType, args: tuple[Data, ...]) -> Data:
        return self.registry.construct(type, args)


DEFAULT_NATIVE_REGISTRY = NativeRegistry()
DEFAULT_NATIVE_BACKEND = NativeBackend(registry=DEFAULT_NATIVE_REGISTRY)

_TYPE_BUILD_CTX = TypeBuildContext()


def _active_registry(registry: NativeRegistry | None = None) -> NativeRegistry:
    if registry is not None:
        return registry

    bridge = BRIDGE.get(DEFAULT_BRIDGE)
    if isinstance(bridge, NativeBackend):
        return bridge.registry
    return DEFAULT_NATIVE_REGISTRY


def register_native_type(
    native: object,
    type_: Type,
    *,
    registry: NativeRegistry | None = None,
) -> None:
    _active_registry(registry).register_native_type(native, type_)


def register_python_type(
    origin: object,
    transform: PythonTransform,
    *,
    registry: NativeRegistry | None = None,
) -> None:
    _active_registry(registry).register_python_type(origin, transform)


def register_builtin(
    builtin_cls: type[Builtin],
    *,
    registry: NativeRegistry | None = None,
) -> None:
    _active_registry(registry).register_builtin(builtin_cls)


def drain_pending_builtins(*, registry: NativeRegistry | None = None) -> None:
    _active_registry(registry).drain_pending_builtins()


def type_from_python(
    annotation: Any,
    *,
    ctx: ContextProto | None = None,
    vars: set[Var] | None = None,
    registry: NativeRegistry | None = None,
) -> Type:
    registry = _active_registry(registry)
    ctx = _TYPE_BUILD_CTX if ctx is None else ctx

    if isinstance(annotation, Type):
        return annotation

    if annotation is None:
        return _empty_type()

    if annotation is Any:
        return _any_type()

    if isinstance(annotation, TypeVar):
        var = cast(Var, Var(NativeGenericVarType(ctx=ctx), annotation.__name__))
        if vars is not None:
            vars.add(var)
        return var

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union or origin is PEP604Union:
        return union_type(*(type_from_python(arg, ctx=ctx, vars=vars, registry=registry) for arg in args))

    scalar = registry.type_by_python.get(annotation)
    if scalar is not None:
        return scalar

    if origin is not None:
        return _transform_generic(origin, args, ctx, vars, registry)

    if isinstance(annotation, type):
        if issubclass(annotation, Builtin):
            return build_builtin_type(annotation, registry=registry)
        return _any_type()

    return _any_type()


def _coerce_builtin_type_arg(arg: object | Type, registry: NativeRegistry) -> Type:
    if isinstance(arg, Type):
        return arg

    projected = type_from_python(arg, registry=registry)
    if projected is _any_type() and arg is not Any:
        raise TypeError(f"Cannot project Builtin type argument {arg!r} to protomorph.Type")
    return projected


def build_builtin_type(
    builtin_cls: type[Builtin],
    *args: object | Type,
    registry: NativeRegistry | None = None,
) -> Type:
    registry = _active_registry(registry)
    registry.register_builtin(builtin_cls)
    registry.drain_pending_builtins()

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

    bindings: dict[str, Type] = {}
    for param, projected_arg in zip(parameters, projected_args):
        name = getattr(param, "__name__", None)
        if not isinstance(name, str):
            raise TypeError(f"Unsupported type parameter {param!r} in {builtin_cls.__name__}")
        bindings[name] = projected_arg

    return nominal_type(builtin_cls._anchor_path(), _spec_from_types(**bindings))


def builtin_runtime_type_args(value: Builtin) -> tuple[object | Type, ...] | None:
    orig_class = getattr(value, "__orig_class__", None)
    if orig_class is None:
        return None

    origin = get_origin(orig_class)
    if origin is None or not isinstance(origin, type) or origin is not value.__class__:
        return None

    runtime_args = get_args(orig_class)
    if not runtime_args:
        return ()

    extracted: list[object | Type] = []
    for arg in runtime_args:
        if isinstance(arg, Type) or isinstance(arg, type) or arg is Any:
            extracted.append(arg)
            continue

        if isinstance(arg, TypeVar) or get_origin(arg) is not None:
            extracted.append(arg)
            continue

        return None

    return tuple(extracted)


def _transform_generic(
    origin: object,
    args: tuple[Any, ...],
    ctx: ContextProto,
    vars: set[Var] | None,
    registry: NativeRegistry,
) -> Type:
    transform = registry.python_transforms.get(origin)
    if transform is not None:
        converted = tuple(
            type_from_python(arg, ctx=ctx, vars=vars, registry=registry)
            if arg is not Ellipsis
            else arg
            for arg in args
        )
        return transform(*converted)

    if isinstance(origin, type) and issubclass(origin, Builtin):
        return build_builtin_type(origin, *args, registry=registry)

    return _any_type()


def _spec_from_types(**bindings: Type) -> Const | None:
    if not bindings:
        return None

    from . import api

    return api.struct(
        **{name: cast(Const | Var, api.val(type_)) for name, type_ in bindings.items()}
    )


def _tuple_transform(*args: Type) -> Type:
    if len(args) == 2 and args[1] is Ellipsis:
        return nominal_qual("std.List", _spec_from_types(), underlying=args[0])
    return StructType(meta_attrs=Struct.new(*args))


def _any_type() -> Type:
    from . import api

    return api.ANY_TYPE


def _empty_type() -> Type:
    from . import api

    return api.EMPTY_TYPE


def nominal_type(anchor: str, spec: Const | None = None) -> NominalType:
    from . import api

    return api.nominal_type(anchor, spec)


def nominal_qual(anchor: str, spec: Const | None = None, *, underlying: Type) -> NominalQualifier:
    from . import api

    return api.nominal_qual(anchor, spec, underlying=underlying)


def union_type(*types: Type) -> UnionType:
    from . import api

    return api.union_type(*types)


def _bootstrap_defaults() -> None:
    from . import api

    registry = DEFAULT_NATIVE_REGISTRY
    registry.type_by_python.clear()
    registry.python_transforms.clear()
    registry._resolved_fields_by_spec.clear()

    api.TYPE_BY_NATIVE.clear()
    scalar_types = {
        bool: api.BOOLEAN_TYPE,
        int: api.INTEGER_TYPE,
        float: api.DECIMAL_TYPE,
        Decimal: api.DECIMAL_TYPE,
        str: api.TEXT_TYPE,
        NoneType: api.EMPTY_TYPE,
    }
    api.TYPE_BY_NATIVE.update(scalar_types)
    for native, type_ in scalar_types.items():
        registry.register_native_type(native, type_)

    set_transform = lambda value_type: nominal_qual(
        "std.Set",
        _spec_from_types(),
        underlying=value_type,
    )
    map_transform = lambda key_type, value_type: nominal_qual(
        "std.Map",
        _spec_from_types(K=key_type),
        underlying=value_type,
    )
    list_transform = lambda value_type: nominal_qual(
        "std.List",
        _spec_from_types(),
        underlying=value_type,
    )

    registry.register_python_type(dict, map_transform)
    registry.register_python_type(frozendict, map_transform)
    registry.register_python_type(list, list_transform)
    registry.register_python_type(set, set_transform)
    registry.register_python_type(frozenset, set_transform)
    registry.register_python_type(tuple, _tuple_transform)
    registry.register_python_type(PEP604Union, lambda *types: union_type(*types))
    registry.drain_pending_builtins()
