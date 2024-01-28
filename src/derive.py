# %%
from curses import use_default_colors
from typing import Callable, NoReturn, Protocol, Any

from traitlets import default

from trust import Trust


_implementation_for_protocol: dict[type, Callable[[type], type]] = {}


def derive(*protocols: Protocol):
    def transformation(cls: type) -> type:
        if not issubclass(cls, Trust):
            raise TypeError(
                f"Cannot derive {', '.join(map(lambda p: p.__qualname__, protocols))} for {cls.__qualname__}."
                f" {cls.__qualname__} is not a Trust class."
            )
        for proto in protocols:
            if transform := _implementation_for_protocol.get(proto, False):
                cls = transform(cls)
                continue

            raise NotImplementedError(
                f"Cannot derive {proto.__qualname__} for {cls.__qualname__}."
                f" No implementation for {proto.__qualname__} is registered."
            )

        return cls

    return transformation


def impl(protocol: Protocol):
    def registration(transformer: Callable[[type], type]):
        _implementation_for_protocol[protocol] = transformer
        return transformer

    return registration


class Init(Protocol):
    def __init__(self, *args, **kwargs) -> None:
        ...


class Hash(Protocol):
    def __hash__(self) -> int:
        ...


class Eq(Protocol):
    def __eq__(self, other: Any) -> bool:
        ...


class Cmp(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...

    def __gt__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: Any) -> bool:
        ...


class Repr(Protocol):
    def __repr__(self) -> str:
        ...


class Immutable(Protocol):
    def __setattr__(self, __name: str, __value: Any) -> NoReturn:
        ...


def compile_method(
    *source,
    name: str,
    locals: dict[str, Any] | None = None,
    globals: dict[str, Any] | None = None,
) -> Any:
    """
    Define a method with the given name, code, defaults, and annotations.

    Args:
        name (str): The name of the method.
        code (str): The code of the method.
        defaults (tuple[Any, ...] | None, optional): The default values for the method arguments. Defaults to None.
        annotations (dict[str, Any] | None, optional): The type annotations for the method arguments. Defaults to None.

    Returns:
        Any: The defined method.
    """
    if locals is None:
        locals = {}

    source = "\n".join(source)
    exec(source, globals, locals)
    method_func = locals[name]
    method_func.__source__ = source
    return method_func


@impl(Init)
def make_init(cls: type[Trust], use_descriptors=True):
    if use_descriptors:
        cls.__init__ = compile_method(
            f'def __init__(self, {", ".join(cls.fields)}):',
            *[f"\tglobal {field}_setter" for field in cls.fields],
            *[f"\t{field}_setter(self, {field})" for field in cls.fields],
            name="__init__",
            globals={
                f"{field}_setter": cls.__dict__[field].__set__ for field in cls.fields
            },
        )
    else:
        cls.__init__ = compile_method(
            f'def __init__(self, {", ".join(cls.fields)}):',
            *[f"\tself.{field} = {field}" for field in cls.fields],
            name="__init__",
        )
    cls.__init__.__defaults__ = cls.__defaults__

    return cls


@impl(Hash)
def make_hash(cls: type[Trust]):
    cls.__hash__ = compile_method(
        f"def __hash__(self):",
        f'\treturn hash(({" ".join(f"self.{field}," for field in cls.fields)}))',
        name="__hash__",
    )
    return cls


@impl(Eq)
def make_eq(cls: type[Trust]):
    cls.__eq__ = compile_method(
        f"def __eq__(self, other):",
        f"\tif type(self) != type(other):",
        f"\t\treturn NotImplemented",
        *[
            f"\tif self.{field} != other.{field}:\n\t\treturn False"
            for field in cls.fields
        ],
        f"\treturn True",
        name="__eq__",
    )
    return cls


@impl(Immutable)
def make_immutable(cls: type[Trust]):
    cls = make_init(cls, use_descriptors=True)

    cls.__setattr__ = compile_method(
        f"def __setattr__(self, name, value):",
        "\traise AttributeError("
        '\t\tf"Cannot set the attribute `{name}`. "'
        '\t\tf"The class `{type(self).__name__}` is a immutable."'
        "\t) from None",
        name="__setattr__",
    )

    return cls


@derive(Immutable, Hash, Eq)
class Item(Trust):
    value: int = 9


item = Item()
# item.value = 3


hash(Item())

# %%
