# %%
from functools import wraps
from typing import Callable, ClassVar, Optional, Self
from weakref import WeakKeyDictionary
from protobase.core import Object
from contextvars import ContextVar, Token
from protobase.core.classproperty import classproperty

class Context(Object, abstract=True):
    __contextvar__: ClassVar[ContextVar]

    def __init_subclass__(cls, context_base: bool = False, **kwargs): 
        super().__init_subclass__(**kwargs)
        print(context_base)
        if context_base:
            cls.__contextvar__ = ContextVar(f"{cls.__module__}:{cls.__qualname__}")

    def __enter__(self):
        assert not hasattr(self, "__contexttoken__"), "Context already entered"
        print('enter', self.__contextvar__)
        _CONTEXT_STACK.setdefault(self, []).append(self.__contextvar__.set(self))

    def __exit__(self, exc_type, exc_value, traceback):
        token = _CONTEXT_STACK.get(self, []).pop()
        self.__contextvar__.reset(token)

    @classproperty
    def context(cls) -> Optional[Self]:
        print('ctx', cls, cls.__contextvar__)
        return cls.__contextvar__.get(None)

    @property
    def is_current_context(self) -> bool:
        return type(self).context == self
    
    @property
    def is_context_activated(self) -> bool:
        return len(_CONTEXT_STACK.get(self, [])) > 0

# PER THREAD
_CONTEXT_STACK = WeakKeyDictionary[Context, list[Token]]


def contextmethod[*A, R](fn: Callable[[*A], R]) :
    @wraps(fn)
    def wrapper(self: Context, *args: *A, **kwargs):
        if self.is_current_context:
            return fn(self, *args, **kwargs)
        with self:
            return fn(self, *args, **kwargs)

    return wrapper



# Pass throught inmutability of __contexttoken__ slot
#_set_context_token = Context.__contexttoken__.__set__
#_del_context_token = Context.__contexttoken__.__delete__

if __name__ == "__main__":

    class MyContext(Context):
        a: int = 9
        pass

    with MyContext() as ctx:
        assert ctx.is_active
        assert MyContext.context == ctx
        c = MyContext.context

    assert not ctx.is_active
    # assert not MyContext.current()
    print("Context passed")
