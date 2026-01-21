# %%
from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar, Literal, Self, dataclass_transform
from weakref import WeakKeyDictionary, ref

from .core import attr_info_of, derived, attrs_of
from .core.object import Object, Type
from .inmutable import check_inmutable, register_inmutable
from .utils import compile_function, dict_split

__all__ = ["Record", 'mutate']


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

    __consign__: ClassVar[WeakKeyDictionary[Self, ref[Self]]]
    __isfrozen__: ClassVar[bool]
    __isconsed__: ClassVar[bool]

    @staticmethod
    def __class_build__(bld: Type.Builder):  # Type.Proto
        inherited_consed = any(bld.mro_data("consed").values())
        inherited_frozen = any(bld.mro_data("frozen").values())

        consed = bld.args.pop("consed", inherited_consed)
        frozen = bld.args.pop("frozen", consed or inherited_frozen)

        if inherited_frozen and not frozen:
            raise TypeError("Cannot inherit from a frozen class and not be frozen")

        if inherited_consed and not consed:
            raise TypeError("Cannot inherit from a consed class and not be consed")

        if consed and not frozen:
            raise TypeError("Cannot be consed a not frozen class")

        if frozen:
            bld.add_slots("__hash_cache__")

        if consed:
            bld.add_slots("__weakref__")

        bld.data(frozen=frozen, consed=consed)

        @bld.postbuild
        def post(cls):
            cls.__isfrozen__ = frozen
            cls.__isconsed__ = consed

            if frozen:
                cls.__setattr__ = _frozen_setattr
                register_inmutable(cls)

            if consed and not cls.__isabstract__:
                cls.__consign__ = WeakKeyDictionary()

    @classmethod
    def __class_check__(cls):
        if cls.__isfrozen__:

            inmutability_errors = []

            for nm, attr in attr_info_of(cls).items():
                try:
                    check_inmutable(attr.type)
                except TypeError as exc:
                    exc.add_note(
                        f"Attribute {nm!r} of {cls.__name__!r} is not inmutable"
                    )
                    inmutability_errors.append(exc)

            if inmutability_errors:
                raise ExceptionGroup(
                    f"Errors in inmutability of {cls.__name__!r}",
                    inmutability_errors,
                )

    if not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            self = super().__new__(cls)
            self.__init__(*args, **kwargs)
            if cls.__isconsed__:
                try:
                    return cls.__consign__.setdefault(self, ref(self))()
                except TypeError as exc:
                    raise ValueError(f"Cannot hash-consed object {self}") from exc
            return self

        def __hash__(self):
            if not self.__class__.__isfrozen__:
                return super().__hash__()

            try:
                return self.__hash_cache__
            except AttributeError:
                pass
            hash = super().__hash__()
            object.__setattr__(self, "__hash_cache__", hash)
            return hash

        @derived(impl_rich_repr_method)
        def __rich_repr__(self): ...

        @derived(impl_repr_method)
        def __repr__(self): ...

        @derived(impl_hash_method)
        def __hash__(self): ...

        @derived(impl_eq_method)
        def __eq__(self, other): ...

        @derived(impl_cmp_method, "__lt__")
        def __lt__(self, other): ...

        @derived(impl_cmp_method, "__gt__")
        def __gt__(self, other): ...

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
            if self.__isfrozen__:
                return self
            
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
            if self.__isfrozen__:
                return self
            
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

def _frozen_setattr(self, name, value):
    raise AttributeError(
        f"Can't set attribute {name!r} on {self.__class__.__name__!r} object is frozen"
    )
