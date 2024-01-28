# %%
from __future__ import annotations

from enum import Enum
from typing import (
    Annotated,
    Any,
    ClassVar,
    Iterator,
    dataclass_transform,
    get_origin,
    get_type_hints,
)
from weakref import WeakKeyDictionary, ref


@dataclass_transform()
class PureMeta(type):
    """
    Metaclass for the Pure class.
    """

    __instances__: WeakKeyDictionary
    __fields__: tuple[str, ...]

    def __new__(mcs, name, bases, namespace, /, ignore_fields: tuple[str, ...] = ()):
        annotations = namespace.get("__annotations__", {})

        field_names = tuple(
            nm for nm, anno in annotations.items() if nm not in ignore_fields
        )

        defaults = []
        for field in field_names:
            if not field in namespace:
                assert (
                    len(defaults) == 0
                ), f"default field {field} followed by no default field"
                continue

            defaults.append(namespace.pop(field))

        args = ",".join(field_names)
        arg_dict = ",".join(f"{field}={field}" for field in field_names)

        init_fn = (
            eval(
                f"lambda s, {args}: _pure_init(s, dict({arg_dict}))",
                {"_pure_init": _pure_init},
            )
            if len(field_names) > 0
            else lambda s: None
        )
        init_fn.__defaults__ = tuple(defaults)
        init_fn.__annotations__ = annotations

        namespace.update(
            {
                "__slots__": (*namespace.get("__slots__", ()), *field_names),
                "__instances__": WeakKeyDictionary(),
                "__init__": init_fn,
                "__fields__": field_names,
            }
        )

        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        instances = cls.__instances__
        instance = super().__call__(*args, **kwds)
        if instance in instances:
            return instances[instance]()
        instances[instance] = ref(instance)
        return instance

    def __len__(cls) -> int:
        """Get the number of fields of a pure class."""
        return len(cls.__fields__)

    def __iter__(cls) -> Iterator[FieldInfo]:
        """Get the field info of a pure class."""
        type_hints = get_type_hints(cls)

        no_default_count = len(cls) - len(cls.__init__.__defaults__)
        defaults = (undefined,) * no_default_count + cls.__init__.__defaults__

        for n, nm in enumerate(cls.__fields__):
            yield FieldInfo(
                nm,
                type_hints.get(nm, undefined),
                defaults[n],
            )


# def _pure_setattr(pure: Pure, name: str, value: Any) -> None:
#     type(pure).__dict__[name].__set__(pure, value)


def _pure_init(obj: Pure, values: dict[str, Any]) -> None:
    dct = type(obj).__dict__
    for nm, val in values.items():
        dct[nm].__set__(obj, val)


# @dataclass_transform()
class Pure(metaclass=PureMeta, ignore_fields=("__fields__",)):
    """
    A base class for creating pure objects.

    Pure objects are immutable and have no side effects.
    Pure objects are interned, meaning that two pure objects with the same
    values are the same object. The 'is' operator can be used to compare
    pure objects.
    """

    __slots__ = (
        "__weakref__",
        "__hash_cached__",
    )
    __fields__: ClassVar[tuple[str, ...]]

    def __hash__(self) -> int:
        if not hasattr(self, "__hash_cached__"):
            tup = tuple(getattr(self, field) for field in self.__fields__)
            Pure.__dict__["__hash_cached__"].__set__(self, hash(tup))

        return getattr(self, "__hash_cached__")

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        return type(self) is type(other) and all(
            getattr(self, field) == getattr(other, field) for field in self.__fields__
        )

    def __setattr__(self, __name: str, __value: Any) -> None:
        raise AttributeError("Pure objects are immutable")

    def __delattr__(self, __name: str) -> None:
        raise AttributeError("Pure objects are immutable")

    def __repr__(self) -> str:
        cls = type(self)
        hints = get_type_hints(cls, include_extras=True)

        fields = (
            f"{getattr(self, field)!r}"
            if Tag.POSITIONAL_ONLY.in_type_hint(hints[field])
            else f"{field}={getattr(self, field)!r}"
            for field in self.__fields__
            if not Tag.EXCLUDE_REPR.in_type_hint(hints[field])
        )

        return f"{type(self).__name__}({', '.join(fields)})"

    def __rich_repr__(self) -> Iterator[tuple[str, Any]]:
        for field in type(self):
            if field.has_default:
                yield field.name, getattr(self, field.name), field.default
            else:
                yield field.name, getattr(self, field.name)


class Doc(Pure):
    """A documentation comment."""

    text: str


class Undefined(Pure):
    """A class representing an undefined value."""


undefined = Undefined()


class Tag(str, Enum):
    POSITIONAL_ONLY = "positional-only"
    KEYWORD_ONLY = "keyword-only"
    EXCLUDE_REPR = "ignore-repr"

    def in_type_hint(self, hint: Any) -> bool:
        if get_origin(hint) is Annotated:
            return self.value in hint.__metadata__
        return False


class FieldInfo(Pure):
    name: Annotated[str, Doc("The name of the field.")]
    type: Annotated[Any, Doc("The type of the field.")]
    default: Annotated[Any | Undefined, Doc("Default value")] = undefined

    @property
    def has_default(self) -> bool:
        return self.default is not undefined


# %%
