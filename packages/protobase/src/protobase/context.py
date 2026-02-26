# %%
from functools import wraps
from typing import Any, Callable, ClassVar, Concatenate, Optional, ParamSpec, Self, TypeVar, cast
from weakref import WeakKeyDictionary
from protobase.object import Object
from contextvars import ContextVar, Token
from protobase.classproperty import classproperty

class Context(Object, abstract=True):
    __contextvar__: ClassVar[ContextVar[Optional["Context"]]]

    def __init_subclass__(cls, context_base: bool = False, **kwargs): 
        super().__init_subclass__(**kwargs)
        if context_base:
            cls.__contextvar__ = ContextVar(
                f"{cls.__module__}:{cls.__qualname__}",
                default=None,
            )

    def __enter__(self):
        assert not hasattr(self, "__contexttoken__"), "Context already entered"
        stack = _CONTEXT_STACK.setdefault(self, [])
        stack.append(self.__contextvar__.set(self))

    def __exit__(self, exc_type, exc_value, traceback):
        stack = _CONTEXT_STACK.get(self)
        if not stack:
            return
        token = stack.pop()
        self.__contextvar__.reset(token)
        if not stack:
            _CONTEXT_STACK.pop(self, None)

    @classproperty
    def context(cls) -> Optional[Self]:
        return cast(Optional[Self], cls.__contextvar__.get(None))

    @property
    def is_current_context(self) -> bool:
        return type(self).context == self
    
    @property
    def is_context_activated(self) -> bool:
        return bool(_CONTEXT_STACK.get(self))

# PER THREAD
_CONTEXT_STACK: WeakKeyDictionary[
    Context,
    list[Token[Optional[Context]]],
] = WeakKeyDictionary()


P = ParamSpec("P")
R = TypeVar("R")
C = TypeVar("C", bound="Context")


def contextmethod(fn: Callable[Concatenate[C, P], R]) -> Callable[Concatenate[C, P], R]:
    @wraps(fn)
    def wrapper(self: C, *args: P.args, **kwargs: P.kwargs) -> R:
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

    ctx = MyContext()
    with ctx:
        assert ctx.is_context_activated
        assert MyContext.context == ctx
        c = MyContext.context

    assert not ctx.is_context_activated
    # assert not MyContext.current()
