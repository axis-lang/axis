# %%
from copy import deepcopy
from dataclasses import MISSING
from functools import cached_property
from itertools import chain, filterfalse
from types import GenericAlias, MappingProxyType, UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    NamedTuple,
    TypeVar,
    Optional,
    Self,
    Sequence,
    Union,
    dataclass_transform,
    get_args,
    get_origin,
    get_type_hints,
    TypeAliasType, 
)
from warnings import warn
from weakref import WeakKeyDictionary

from ..utils import compile_function, dict_split
from .derived import derived
from .type import Type


AnnotatedType = type(Annotated[int, ...])


def _unwrap_type_alias(anno: Any):
    while isinstance(anno, TypeAliasType):
        anno = anno.__value__
    return anno


def normalize_type(anno: Any):
    anno = _unwrap_type_alias(anno)

    if get_origin(anno) is Annotated:
        anno = anno.__origin__

    if isinstance(anno, (type, GenericAlias, UnionType, TypeVar)):
        origin = get_origin(anno)
        if origin is None:
            return anno

        args = get_args(anno)
        if not args:
            return anno

        normalized_args = tuple(_unwrap_type_alias(arg) for arg in args)
        if normalized_args == args:
            return anno

        try:
            if origin is Union:
                return Union[normalized_args]
            return origin[normalized_args]
        except TypeError:
            return anno

    if get_origin(anno) in (Union,):
        return anno

    raise TypeError(f"Invalid annotation type {type(anno)}")


class AttrInfo(NamedTuple):
    name: str
    annotation: Any
    default: Any
    super: Optional[Self]

    @property
    def has_default(self):
        return self.default is not MISSING

    @property
    def type(self) -> Any:
        try:
            return normalize_type(self.annotation)
        except TypeError as e:
            e.add_note(f"Error in attribute '{self.name}'")
            raise

    @property
    def type_origin(self) -> Any:
        return get_origin(self.type) or self.type

    @property
    def type_args(self) -> tuple[Any, ...]:
        return get_args(self.type)

    @property
    def metadata(self) -> tuple[Any, ...]:
        if get_origin(self.annotation) is Annotated:
            return self.annotation.__metadata__
        return ()


def protodata_of(cls: Type):
    if not issubclass(cls.__class__, Type):
        raise TypeError(f"{cls} is not a protobase type")

    return cls.__dict__.get("__protodata__")


_ATTRS_CACHE = WeakKeyDictionary()


def attr_info_of(cls) -> dict[str, AttrInfo]:
    if not isinstance(cls, type):
        cls = type(cls)

    if cls in _ATTRS_CACHE:
        return _ATTRS_CACHE[cls]

    def _collect_proto_attrs(cls):
        try:
            meta = protodata_of(cls)
        except TypeError:
            return {}

        hints = get_type_hints(cls, include_extras=True)

        attrs = {}
        for base in reversed(cls.__mro__[1:]):
            for attr, info in _collect_proto_attrs(base).items():
                attrs.setdefault(attr, []).extend(info)

        for attr, default_value in meta.get("attrs").items():
            info = (cls, hints.get(attr), default_value)
            attrs.setdefault(attr, []).append(info)

        return attrs

    proto_attrs = _collect_proto_attrs(cls)

    attrs = {}
    for attr_name, infos in proto_attrs.items():
        attr = None
        for _cls, hint, default in infos:
            attr = AttrInfo(
                name=attr_name,
                annotation=hint,
                default=default,
                super=attr,
            )

        attrs[attr_name] = attr

    attrs = MappingProxyType(attrs)
    _ATTRS_CACHE[cls] = attrs

    if hasattr(cls, "__class_check__"):
        cls.__class_check__()

    return attrs


class DefaultFactory:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return deepcopy(self.value)


def impl_init_method(cls):

    strict_nominal_args = False  # from meta info

    positional_attrs, nominal_attrs = dict_split(
        attr_info_of(cls), lambda info: info.has_default
    )

    if strict_nominal_args:
        if len(nominal_attrs):
            args = ["self", *positional_attrs, "*", *nominal_attrs]
        else:
            args = ["self", *positional_attrs]
        kwdefaults = {k: MISSING for k, in nominal_attrs}
        defaults = ()
    else:
        args = ["self", *positional_attrs, *nominal_attrs]
        kwdefaults = {}
        defaults = (MISSING,) * len(nominal_attrs)

    attrs_factories = {
        f"_{attr}_factory": DefaultFactory(info.default)
        for attr, info in nominal_attrs.items()
    }

    return compile_function(  # default value es deepcopy factory
        f"def __init__({', '.join(args)}):",
        *[
            f"    object.__setattr__(self, '{attr}', {attr})"
            for attr in positional_attrs
        ],
        *[
            f"    object.__setattr__(self, '{attr}', {attr} if {attr} is not __MISSING__ else _{attr}_factory())"
            for attr in nominal_attrs
        ],
        "    return",
        globals={**attrs_factories, "__MISSING__": MISSING},
        __kwdefaults__=kwdefaults,
        __defaults__=defaults,
    )


def impl_state_method(cls):
    attrs = attr_info_of(cls)
    return compile_function(  # default value es deepcopy factory
        f"def __state__(self):",
        f"    return dict(",
        *[f"      {attr}=self.{attr}," for attr in attrs],
        f"    )",
    )


def slots_of(cls_or_mro: type | Sequence[type]):
    mro = cls_or_mro.__mro__ if isinstance(cls_or_mro, type) else cls_or_mro

    return tuple(
        chain.from_iterable(getattr(base, "__slots__", ()) for base in reversed(mro))
    )


def is_abstract(cls) -> bool:
    return getattr(cls, "__isabstract__", False)



def _unique_everseen(iterable, seen: set):
    "Yield unique elements, preserving order. Remember all elements ever seen."
    for element in filterfalse(seen.__contains__, iterable):
        seen.add(element)
        yield element


def _is_classvar_annotation(anno, module):
    import typing
    from dataclasses import _is_classvar, _is_type

    # workaround for cls param
    def cls(): ...

    # cls = object()
    cls.__module__ = module

    return _is_classvar(anno, typing) or (
        isinstance(anno, str)
        and _is_type(anno, cls, typing, typing.ClassVar, _is_classvar)
    )


@dataclass_transform(eq_default=False, order_default=False)
class Object(metaclass=Type, abstract=True):
    """
    Base class for all objects in the protobase class system.
    init, state
    """

    __isabstract__: ClassVar[bool]

    @staticmethod
    def __class_build__(bld: Type.Builder):  # Type.Proto

        inherited_abstract = all(bld.mro_data("abstract").values())
        abstract = bld.args.pop("abstract", False)

        # inherited_hub = any(bld.mro_data("hub").values())
        # hub = bld.args.pop("hub", inherited_hub is False and abstract is False)
        # if inherited_hub and hub:
        #     exc = TypeError("Cannot inherit from a hub class and be a hub class")
        #     exc.add_note(
        #         "A hub class is a class that is not abstract and does not inherit from an abstract class"
        #     )
        #     raise exc

        inherited_nested = any(bld.mro_data("nested").values())
        nested = bld.args.pop("nested", inherited_nested)

        if inherited_nested and not nested:
            raise TypeError("Cannot inherit from a nested class and not be nested")

        if nested:
            if len(bld.namespace.get("__qualname__").split(".")) <= 1:
                raise TypeError("Nested classes must be member of another class")

        def is_attr_member(nm, anno):
            return not _is_classvar_annotation(anno, bld.module)

        attrs = {
            nm: bld.namespace.pop(nm, MISSING)
            for nm, anno in bld.annotations.items()
            if is_attr_member(nm, anno)
        }

        user_slots = bld.namespace.pop("__slots__", ())

        attr_slots = tuple(attrs)

        member_slots = tuple(
            v.slotname(bld.name, k)
            for k, v in bld.namespace.items()
            if isinstance(v, Type.SlotMember)  #  TODO: Type.SlotMember
        )

        bld.add_slots(*user_slots, *member_slots, *attr_slots)

        for k, v in bld.namespace.items():
            if isinstance(v, cached_property):
                warn(
                    f"functools.cached_property '{k}' is not supported in protobase. Use protobase.cached_property instead."
                )

        sticky_members = {
            k: v
            for k, v in bld.namespace.items()
            if isinstance(v, Type.StickyMember)  # Type.StickyMember
        }

        bld.data(
            abstract=abstract,
            # hub=hub,
            nested=nested,
            attrs=attrs,
            # properties
            sticky=sticky_members,
        )

        @bld.prebuild
        def prebuild():

            bld.data(slots=bld._slots)

            slots = tuple(
                _unique_everseen(
                    chain(
                        # inherited slots
                        chain.from_iterable(bld.mro_data("slots").values()),
                        # self slots
                        bld._slots,
                    ),
                    # already defined slots
                    seen=set(slots_of(bld.mro)),
                )
                if not abstract
                else ()
            )

            bld.namespace["__slots__"] = slots

        @bld.postbuild
        def postbuild(cls):
            # assign sticky members
            for base_sticky_members in bld.mro_data("sticky").values():
                for k, v in base_sticky_members.items():
                    if k not in bld.namespace:
                        setattr(cls, k, v)

            # assign self as parent of nested classes
            # for k, v in cls.__dict__.items():
            #     if isinstance(v, type) and issubclass(v, Object):
            #         #if protodata_of(v).get("nested", False):
            #         setattr(v, "__parent__", cls)

            # set metadata
            setattr(
                cls, "__protodata__", bld._metadata
            )  ## TODO: deep frozen the protodata??
            cls.__isabstract__ = abstract

    if not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            if cls.__isabstract__:
                raise TypeError(
                    f"Cannot instantiate abstract class '{cls.__qualname__}'"
                )

            return object.__new__(cls)

        @derived(impl_init_method)
        def __init__(self, *args, **kwargs): ...

        @derived(impl_state_method)
        def __state__(self): ...


def attrs_of(obj: Object) -> dict[str, Any]:
    return obj.__state__()
