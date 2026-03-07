#%%
from typing import Any, ClassVar, Self, cast

from protobase.object import Object
from protobase.type import Type
from protobase.weak import WeakKeyIdDictionary

class Metadata[T=Any](Object, abstract=True):
    __slots__ = "__weakref__",
    __storage__: ClassVar[WeakKeyIdDictionary[object, object]]
    
    @staticmethod
    def __class_build__(bld: Type.Builder):  # Type.Proto

        abstract = bld.data('abstract')
        #inherited_abstract = all(bld.mro_data('abstract').values())

        inherited_hub = any(bld.mro_data("hub").values())
        hub = bld.args.pop("hub", inherited_hub is False and abstract is False)

        if inherited_hub and hub:
            exc = TypeError("Cannot inherit from a hub class and be a hub class")
            exc.add_note(
                "A hub class is a class that is not abstract and does not inherit from an abstract class"
            )
            raise exc

        bld.data(hub=hub)

        @bld.postbuild
        def post(cls):
            if hub:
                cls.__hub_class__ = cls
                cls.__storage__ = WeakKeyIdDictionary()

    @classmethod
    def of(cls, obj: T) -> Self | None:
        try: 
            return cls.__storage__.get(obj) # type: ignore
        except KeyError:
            pass
        return cls.__on_fault__(obj)
    
    @classmethod
    def __on_fault__(cls, obj: T) -> Self | None:
        return None

    def tag[V](self, obj: V) -> V:
        type(self).__storage__[obj] = self
        return obj

    # def tag(self, *objs: T) -> None:
    #     storage = type(self).__storage__
    #     for obj in objs:
    #         storage[obj] = self
