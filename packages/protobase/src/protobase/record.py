# %%
from copy import deepcopy
from typing import TYPE_CHECKING, Literal, Self, dataclass_transform

from .object import attr_info_of, attrs_of, Object
from .derived import derived
from .type import Type
from .utils import compile_function, dict_split

__all__ = ["Record", "mutate"]


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


def impl_hash_method(cls):
    # TODO: Tansolo los atributos que participen en hash y eq (identity)
    attrs = (f"self.{attr.name}" for attr in attr_info_of(cls).values())

    return compile_function(
        "def __hash__(self):",
        f"    return hash(({', '.join(attrs)}))",
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
