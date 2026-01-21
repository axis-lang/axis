from typing import Mapping, Optional, Self
from protobase.inmutable import inmutable

@inmutable
class frozendict[K, V](dict[K, V]): # IDEA: utilizar dict view
    

    __slots__ = "__hash_cache__"

    def __hash__(self):
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

    def __or__(self, other: Mapping[K, V]):
        return self.__class__(dict.__or__(self, other))

    def __ior__(self, other: Mapping[K, V]):
        return self.__class__(dict.__ior__(self, other))

    def __delitem__(self, k: K):
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def __delattr__(self, name):
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def __setattr__(self, name, value):
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def clear(self):
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def pop(self, k: K, d: V | None = None) -> V:
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def popitem(self) -> tuple[K, V]:
        raise ValueError(f"{self.__class__.__name__} is immutable")

    def set(self, k: K, v: V) -> Self:
        return self.__class__(self, **{k: v})

    def setdefault(self, k: K, v: V) -> Self:
        if k in self:
            return self
        return self.__class__(self, **{k: v})

    def delete(self, k: K, v: V) -> Self:
        return self.__class__(item for item in self.items() if item[0] != k)

    def update(self, d: Optional[dict[K, V]] = None, **kwargs):
        if d is None:
            d = {}
        return self.__class__(self, **d, **kwargs)


if __name__ == "__main__":
    ...
