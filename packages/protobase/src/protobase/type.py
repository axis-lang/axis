# %%
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import cache
from sys import modules
from typing import Any, Callable, Optional, Self, Sequence
from warnings import warn

from .missing import Missing as _MISSING, MissingType as _MISSING_TYPE

class Type(type):

    class SlotMember(ABC):
        """A class member that holds a slot"""

        @abstractmethod
        def slotname(self, owner_name: str, name: str) -> str: ...

    class StickyMember(ABC):
        """A class member that is sticky to the class and its subclasses."""

    @dataclass
    class Builder:
        metaclass: type
        name: str
        bases: tuple[type, ...]
        namespace: dict[str, Any]
        args: dict[str, Any]

        _metadata: dict[str, Any] = field(default_factory=dict, init=False)
        mro: list[type] = field(default_factory=list, init=False)
        _slots: list[str] = field(default_factory=list, init=False)

        def __post_init__(self):
            self.mro = _mro_sorted(self.bases)

            # Run class builders
            for base in reversed(self.mro):
                if "__class_build__" in base.__dict__:
                    base.__dict__["__class_build__"](self)

            if "__class_build__" in self.namespace:
                self.namespace["__class_build__"](self)

            if len(self.args):
                raise ValueError(
                    f"Unused class arguments in {self.name}: {', '.join(self.args.keys())}"
                )

        @property
        def module(self):
            return self.namespace.get("__module__", None)

        @property
        def qualname(self):
            return self.namespace.get("__qualname__", None)

        @property
        def id(self):
            return f"{self.module}:{self.qualname}"

        @property
        def annotations(self):
            return self.namespace.get("__annotations__", {})

        def data(self, *args, **kwargs):
            if "attrs" in kwargs:
                attrs = kwargs["attrs"]
                if isinstance(attrs, dict):
                    kwargs["attrs"] = {
                        name: (_MISSING if isinstance(value, _MISSING_TYPE) else value)
                        for name, value in attrs.items()
                    }
            self._metadata.update(kwargs)
            result = tuple(self._metadata.get(arg) for arg in args)
            return result[0] if len(result) == 1 else result

        def mro_data(self, name: str):
            return get_mro_protodata(self.mro, name)

        def add_slots(self, *slots):
            self._slots.extend(slots)

        prebuilders: list[Callable[[], None]] = field(
            default_factory=list, init=False
        )

        def prebuild(self, func: Callable[[], None]):
            self.prebuilders.append(func)
            return func

        postbuilders: list[Callable[[Self], None]] = field(
            default_factory=list, init=False
        )

        def postbuild(self, func: Callable[[Self], None]):
            self.postbuilders.append(func)
            return func

        def build(self) -> type:

            # Run prebuilders
            for prebuilder in self.prebuilders:
                prebuilder()

            # Create the class
            cls = type.__new__(
                self.metaclass,
                self.name,
                self.bases,
                self.namespace,
            )

            # Run postbuilders
            for postbuilder in self.postbuilders:
                postbuilder(cls)

            if hasattr(cls, "__class_post_build__"):
                cls.__class_post_build__()

            return cls

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs,
    ):
        return mcs.Builder(
            metaclass=mcs,
            name=name,
            bases=bases,
            namespace=namespace,
            args=kwargs,
        ).build()

    @property
    def __parent__(self) -> Optional[type]:
        """
        Returns the parent class of the current class, if it exists.
        This is useful for resolving the class hierarchy and finding
        the parent class of a given class.
        If the parent class cannot be found, a warning is issued.

        Returns:
            Optional[type]: The parent class of the current class, 
            or None if not found.

        """
        path = self.__qualname__.split('.')
        if len(path) == 1:
            return None

        parent = modules.get(self.__module__)

        if parent is None:
            warn(
                f"Could not resolve parent for class {self.__qualname__}: "
                f"Module {self.__module__} not found in sys.modules",
                UserWarning,
                2,
            )
            return None

        for part in path[:-1]:
            if part =='<locals>':
                warn(
                    f"Could not resolve parent for *local* class {self.__qualname__}",
                    UserWarning,
                    2,
                )

            parent = getattr(parent, part, None)
            if parent is None:
                warn(
                    f"Could not resolve parent for class {self.__qualname__}: ",
                    #f"{part} not found in {parent.__name__}",
                    UserWarning,
                    2,
                )
                return None
            
        if not isinstance(parent, type):
            warn(
                f"Could not resolve parent for class {self.__qualname__}: "
                f"{parent} is not a class",
                UserWarning,
                2,
            )
            return None

        return parent

@cache
def parent_of(cls: Type) -> Optional[type]:
    return getattr(cls, "__parent__", None)



def get_mro_protodata(cls_or_mro: type | Sequence[type], name: str):
    mro = cls_or_mro.__mro__ if isinstance(cls_or_mro, type) else cls_or_mro
    return {
        base: baseval
        for base in reversed(mro)
        if (basemeta := getattr(base, '__protodata__', None)) is not None
        and (baseval := basemeta.get(name, _MISSING)) is not _MISSING
    }




def _mro(cls):
    if cls is object:
        return [object]
    return [cls] + _mro_merge([_mro(base) for base in cls.__bases__])


def _mro_merge(mros):
    if not any(mros):  # all lists are empty
        return []  # base case
    for candidate, *_ in mros:
        if all(candidate not in tail for _, *tail in mros):
            return [candidate] + _mro_merge(
                [tail if head is candidate else [head, *tail] for head, *tail in mros]
            )
    else:
        raise TypeError("No legal mro")


def _mro_sorted(bases: Sequence[type]) -> list[type]:
    return _mro_merge([_mro(base) for base in bases])
