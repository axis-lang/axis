# %%
from copy import deepcopy
from typing import TYPE_CHECKING, Literal, Self, dataclass_transform

from .object import attr_info_of, attrs_of, _default_factory, Object
from .derived import derived
from .missing import Missing
from .type import Type
from .utils import compile_function, dict_split

__all__ = ["Record", "mutate", "impl_new_method", "impl_consed_new_method"]


def impl_rich_repr_method(cls):

    attrs = attr_info_of(cls)
    positional_attrs, nominal_attrs = dict_split(attrs, lambda info: info.has_default)

    def __rich_repr__(self):
        for nm in positional_attrs.keys():
            yield None, getattr(self, nm),

        for nm, attr in nominal_attrs.items():
            if attr.has_default:
                yield nm, getattr(self, nm), attr.default
            else:
                yield nm, getattr(self, nm)

    return __rich_repr__


def impl_repr_method(cls):
    def _rich_attr_filter(attr_info: tuple) -> bool:
        if isinstance(attr_info, tuple):
            if len(attr_info) == 3 and attr_info[1] == attr_info[2]:
                return False
        return True

    def _rich_attr_map(attr_info: tuple) -> str:
        if isinstance(attr_info, tuple):
            if len(attr_info) == 1:
                return repr(attr_info[0])

            if attr_info[0] is None:
                return repr(attr_info[1])
            return f"{attr_info[0]}={attr_info[1]!r}"
        return f"{attr_info!r}"

    def __repr__(self):
        attrs = filter(_rich_attr_filter, self.__rich_repr__())
        attrs = map(_rich_attr_map, attrs)
        return f"{cls.__qualname__}({', '.join(attrs)})"

    return __repr__


def impl_new_method(cls):
    """
    Compile a __new__ for Inmutable subclasses that:
      1. Allocates via object.__new__
      2. Calls self.__init__(*args, **kwargs) (preserving custom __init__ signatures)
      3. Reads populated attribute slots to build the canonical key tuple
      4. Pre-populates __hash_cache__ = hash(key)

    For classes whose __init__ calls hash(self) before __new__ completes
    (e.g. via flux.input), __hash__ has a lazy fallback. See Inmutable.__hash__.
    Classes with zero attributes get key = () correctly.
    """
    attr_names = list(attr_info_of(cls).keys())

    if attr_names:
        key_expr = "({},)".format(", ".join(
            f"_ogetattr__(self, {nm!r})" for nm in attr_names
        ))
    else:
        key_expr = "()"

    return compile_function(
        "def __new__(cls, *args, **kwargs):",
        "    self = _object_new__(cls)",
        "    self.__init__(*args, **kwargs)",
        f"    _osetattr__(self, '__hash_cache__', hash({key_expr}))",
        "    return self",
        globals={
            "_object_new__": object.__new__,
            "_osetattr__": object.__setattr__,
            "_ogetattr__": object.__getattribute__,
        },
    )


def impl_consed_new_method(cls):
    """
    Compile a __new__ for Consed subclasses that:
      1. Resolves the canonical key inline (same logic as impl_new_method)
      2. Looks up the key in cls.__consign__ (WeakValueDictionary) — hit: return cached
      3. Miss: allocates, inits, builds key from slots, sets __hash_cache__, stores in consign

    All in one compiled function — no delegation to super().__new__ to avoid
    recomputing the key twice.
    """
    attr_infos = list(attr_info_of(cls).values())
    positional = [a for a in attr_infos if not a.has_default]
    nominal    = [a for a in attr_infos if a.has_default]

    fn_args  = ["cls", *[a.name for a in positional], *[a.name for a in nominal]]
    defaults = (Missing,) * len(nominal)

    nominal_factories = {
        f"_{a.name}_factory": _default_factory(a.default)
        for a in nominal
    }

    # Resolve defaults inline for the key (before __init__ is called)
    attr_names = [a.name for a in attr_infos]
    resolved_names = [
        a.name if not a.has_default else f"_{a.name}_val"
        for a in attr_infos
    ]

    # Lines that resolve nominal defaults into local vars
    resolve_lines = [
        f"    _{a.name}_val = {a.name} if {a.name} is not _Missing__ else _{a.name}_factory()"
        for a in nominal
    ]

    if attr_names:
        key_expr = "({},)".format(", ".join(resolved_names))
    else:
        key_expr = "()"

    # Build __init__ call args using the resolved local vars
    init_positional = ", ".join(a.name for a in positional)
    init_nominal    = ", ".join(f"{a.name}=_{a.name}_val" for a in nominal)
    init_call_args  = ", ".join(filter(None, [init_positional, init_nominal]))

    return compile_function(
        f"def __new__({', '.join(fn_args)}):",
        *resolve_lines,
        f"    _key__ = {key_expr}",
        f"    existing = cls.__consign__.get(_key__)",
        f"    if existing is not None: return existing",
        f"    self = _object_new__(cls)",
        f"    _osetattr__(self, '__hash_cache__', hash(_key__))",
        f"    self.__init__({init_call_args})",
        f"    cls.__consign__[_key__] = self",
        f"    return self",
        globals={
            **nominal_factories,
            "_Missing__": Missing,
            "_object_new__": object.__new__,
            "_osetattr__": object.__setattr__,
        },
        __defaults__=defaults,
    )


def impl_eq_method(cls):
    attrs = attr_info_of(cls)
    return compile_function(
        "def __eq__(self, other):",
        "    if self is other: return True",
        "    if type(self) != type(other): return NotImplemented",
        f"    return ({' and '.join(f'self.{attr} == other.{attr}' for attr in attrs)})",
    )


def impl_cmp_method(
    cls,
    op: Literal["__lt__", "__gt__"],
):
    attrs = list(attr_info_of(cls))
    return compile_function(
        f"def {op}(self, other):",
        "    if type(self) != type(other): return NotImplemented",
        # "    if self is other: return False",
        *[
            f"    if (res := self.{x}.{op}(other.{x})) or self.{x}.__ne__(other.{x}): return res"
            for x in attrs[:-1]
        ],
        f"    return self.{attrs[-1]}.{op}(other.{attrs[-1]})",
    )


class RecordMeta(Type):
    if not TYPE_CHECKING:
        def __call__(cls, *args, **kwargs):
            return cls.__new__(cls, *args, **kwargs)


@dataclass_transform(eq_default=True, order_default=True)
class Record(Object, metaclass=RecordMeta, abstract=True):
    """
    Base class for all mutable objects in the protobase class system.
    eq, hash, order,
    """

    if not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            self = super().__new__(cls)
            self.__init__(*args, **kwargs)
            return self

        @derived(impl_rich_repr_method)
        def __rich_repr__(self): ...

        @derived(impl_repr_method)
        def __repr__(self): ...

        @derived(impl_eq_method)
        def __eq__(self, other): ...

        @derived(impl_cmp_method, "__lt__")
        def __lt__(self, other): ...

        @derived(impl_cmp_method, "__gt__")
        def __gt__(self, other): ...

        def __hash__(self):
            return object.__hash__(self)

        def __ne__(self, other):
            res = self.__eq__(other)
            return NotImplemented if res is NotImplemented else not res

        def __le__(self, other: Self):
            res = self.__gt__(other)
            return NotImplemented if res is NotImplemented else not res

        def __ge__(self, other: Self):
            res = self.__lt__(other)
            return NotImplemented if res is NotImplemented else not res

        def __copy__(self):
            copy = object.__new__(self.__class__)
            for nm, attr in attr_info_of(self).items():
                if nm == "__weakref__":
                    continue
                value = getattr(self, nm)
                if isinstance(value, Record):
                    value = value.__copy__()
                setattr(copy, nm, value)

            return copy

        def __deepcopy__(self, memo):
            if id(self) in memo:
                return memo[id(self)]
            copy = object.__new__(self.__class__)
            memo[id(self)] = copy
            for nm, attr in attr_info_of(self).items():
                if nm == "__weakref__":
                    continue
                value = getattr(self, nm)
                value = deepcopy(value, memo)
                setattr(copy, nm, value)
            return copy


def mutate[T: Record](record: T, **new_attrs) -> T:
    """
    create a copy of the record with the new attributes
    """
    attrs = attrs_of(record)
    attrs.update(new_attrs)
    return record.__class__(**attrs)
