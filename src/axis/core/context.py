# %%
from typing import ClassVar, Optional, Self
from protobase import Record
from contextvars import ContextVar
from protobase import classproperty

class Context(Record):
    __slots__ = '__contexttoken__',
    __contextvar__: ClassVar[ContextVar[Self]] = ContextVar(f"{__name__}.{__qualname__}")
    #__contexttoken__: Optional[Token[Self]] = None

    # def __init_subclass__(cls, hub: bool = False, **kwargs): 
    #     super().__init_subclass__(**kwargs)
    #     if not hub:
    #         return
    #     # hub context, shared among subclasses
    #     cls.__contextvar__ = ContextVar(f"{cls.__module__}.{cls.__qualname__}")

    def __enter__(self):
        assert not hasattr(self, "__contexttoken__"), "Context already entered"
        self.__contexttoken__ = self.__contextvar__.set(self)

    def __exit__(self, exc_type, exc_value, traceback):
        assert hasattr(self, "__contexttoken__"), "Context not entered"
        self.__contextvar__.reset(self.__contexttoken__)
        del self.__contexttoken__

    @classproperty
    @classmethod
    def current(cls) -> Optional[Self]:
        self = cls.__contextvar__.get(None)
        if not isinstance(self, cls):
            return None
        return self

    @property
    def is_current_context(self) -> bool:
        return type(self).current is self

