from typing import Any, Mapping, Optional, Self, TYPE_CHECKING, cast
from protobase.inmutable import inmutable

if TYPE_CHECKING:
    class frozendict[K, V](dict[K, V]):
        __slots__ = "__hash_cache__"

        def __hash__(self) -> int: ...  # pyright: ignore[reportIncompatibleVariableOverride]

        def __repr__(self) -> str: ...

        def __reduce__(self) -> tuple[type, tuple[dict[K, V]]]: ...

        def __setitem__(self, k: K, v: V) -> None: ...

        def __or__(self, other: dict[Any, Any]) -> "frozendict[K, V]": ...

        def __ior__(self, other: object) -> "frozendict[K, V]": ...

        def __delitem__(self, k: K) -> None: ...

        def __delattr__(self, name: str) -> None: ...

        def __setattr__(self, name: str, value: object) -> None: ...

        def clear(self) -> None: ...

        def pop(self, k: K, d: object = ...) -> Any: ...

        def popitem(self) -> tuple[K, V]: ...

        def set(self, k: K, v: V) -> "frozendict[K, V]": ...

        def setdefault(self, k: K, v: object = None) -> Any: ...

        def delete(self, k: K, v: V) -> "frozendict[K, V]": ...

        def update(self, d: object = None, **kwargs: V) -> Any: ...

else:
    class frozendict[K, V](dict[K, V]): # IDEA: utilizar dict view
        __slots__ = "__hash_cache__"

        def __hash__(self):  # pyright: ignore[reportIncompatibleVariableOverride]
            try:
                return self.__hash_cache__
            except AttributeError:
                pass

            result = hash(tuple(self.items()))
            object.__setattr__(self, "__hash_cache__", result)
            return result

        def __repr__(self):
            return f"{self.__class__.__name__}({super().__repr__()})"

        def __reduce__(self):
            return (self.__class__, (dict(self),))

        def __setitem__(self, k: K, v: V):
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def __or__(self, other: dict[Any, Any]):  # type: ignore[override]
            return self.__class__(dict.__or__(self, other))

        def __ior__(self, other: object):  # type: ignore[override]
            return self.__class__(dict.__ior__(self, cast(dict, other)))

        def __delitem__(self, k: K):
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def __delattr__(self, name):
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def __setattr__(self, name, value):
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def clear(self):
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def pop(self, k: K, d: object = ...) -> Any:  # type: ignore[override]
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def popitem(self) -> tuple[K, V]:
            raise ValueError(f"{self.__class__.__name__} is immutable")

        def set(self, k: K, v: V) -> Self:
            data = dict(self)
            data[k] = v
            return self.__class__(data)

        def setdefault(self, k: K, v: object = None) -> Any:  # type: ignore[override]
            if k in self:
                return self
            data = dict(self)
            data[k] = cast(V, v)
            return self.__class__(data)

        def delete(self, k: K, v: V) -> Self:
            return self.__class__(item for item in self.items() if item[0] != k)

        def update(self, d: object = None, **kwargs: V) -> Any:  # type: ignore[override]
            data = dict(self)
            if d:
                data.update(cast(dict, d))
            if kwargs:
                data.update(kwargs)
            return self.__class__(data)

inmutable(frozendict)

if __name__ == "__main__":
    ...
