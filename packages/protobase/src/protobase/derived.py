# %%
from types import MethodType
from typing import Callable, Concatenate, Optional, cast

from .type import Type

class derived[**P](Type.StickyMember):

    def __init__(
        self,
        implementor: Callable[Concatenate[type, P], Callable],
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.implementor = implementor
        self.args = args
        self.kwargs = kwargs

    def __call__(self, proto: Callable):
        self.proto = proto
        return self

    def __set_name__(self, owner, name):

        assert (
            hasattr(self, "owner") is False and hasattr(self, "name") is False
        ), "Cannot reassign the implementation function."

        self.owner: Optional[type] = owner
        self.name = name

    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj) if obj is not None else self.owner
        if objtype is None:
            raise TypeError("derived descriptor requires an owner type")

        target_type = cast(type, objtype)
        fn = self.implementor(target_type, *self.args, **self.kwargs)

        if fn is None:
            raise NotImplementedError(
                f"Cannot find an implementation for '{self.proto.__qualname__}'."
            )
        
        # update_wrapper(fn, self.proto, ('__name__', '__module__', '__doc__'), ())
        fn.__name__ = self.proto.__name__
        fn.__module__ = self.proto.__module__
        fn.__doc__ = self.proto.__doc__


        if isinstance(self.proto, classmethod):
            fn = classmethod(fn)
            #fn.__set_name__(self.owner, self.name)

        setattr(objtype, self.name, fn)
        #print(f"Derived {self.name} from {self.proto.__qualname__} to {objtype.__name__}")

        return getattr(objtype if obj is None else obj, self.name)

        # if obj is None:
        #     return fn
        # return MethodType(fn, obj)
