from typing import Any, Callable, Generic, TYPE_CHECKING, TypeVar, cast


T = TypeVar("T")


if TYPE_CHECKING:
    class classproperty(Generic[T]):
        def __init__(self, fget: Callable[..., T], fset: Callable[..., None] | None = None): ...

        def setter(self, fset: Callable[..., None]) -> "classproperty[T]": ...

        def __get__(self, obj: object, klass: type | None = None) -> T: ...

        def __set__(self, obj: object, value: T) -> None: ...

else:
    class classproperty(Generic[T]):
        def __init__(self, fget: Callable[..., T], fset: Callable[..., None] | None = None):
            if isinstance(fget, (classmethod, staticmethod)):
                self._fget = fget
            else:
                self._fget = classmethod(fget)
            self._fset: Any = None
            if fset is not None:
                self.setter(fset)

        def setter(self, fset: Callable[..., None]) -> "classproperty[T]":
            if isinstance(fset, (classmethod, staticmethod)):
                self._fset = fset
            else:
                self._fset = classmethod(fset)
            return self

        def __get__(self, obj: object, klass: type | None = None) -> T:
            getter = cast(Callable[[], T], self._fget.__get__(obj, klass))
            return getter()

        def __set__(self, obj: object, value: T) -> None:
            if self._fset is None:
                raise AttributeError("can't set attribute")
            setter = cast(Callable[[T], None], self._fset.__get__(obj, type(obj)))
            setter(value)
