from typing import Any, Callable, Optional


class classproperty[T]:
    fget : Callable[..., T]
    fset : Optional[Callable[[Any, T], None]]

    def __init__(self, fget: Callable[..., T], fset=None):
        if not isinstance(fget, (classmethod, staticmethod)):
            fget = classmethod(fget)
        self.fget = fget
        if fset is not None:
            self.setter(fset)

    def setter(self, fset):
        if not isinstance(fset, (classmethod, staticmethod)):
            fset = classmethod(fset)
        self.fset = fset
        return self

    def __get__(self, obj, klass=None) -> T:
        #if klass is None:
            #klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

