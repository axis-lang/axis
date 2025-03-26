# %%
from __future__ import annotations
from itertools import takewhile
from protobase.__core import Object, Consed, attrs_of, AttrInfo
from protobase.collections import Tuple, Map, Set
from typing import Annotated, Any, Optional, Iterable, Callable

type Symbol = str

class Class(Consed):
    class Member(Consed):
        name: Symbol
        type: Type

    name: typing.Optional[Symbol]  # un id es una operacion y un origen
    members: Tuple[Symbol, Type]

    @property
    def is_uniform(self):
        return all(m.type == self.members[0].type for m in self.members)

    @classmethod
    def from_class(cls, klass: type[Object]):
        return cls(
            name=klass.__name__,
            members=Tuple(
                (name, Type.from_attr(info)) for name, info in attrs_of(klass).items()
            ),
        )

class Fn(Consed):
    ' P -> R '
    param: Type
    returns: Type



class Type(Consed):
    type Morph = Set[Class, Fn]

    qualifiers: Tuple[Symbol, Qualifier]
    morph: Morph

    @classmethod
    def from_attr(cls, info: AttrInfo):
        return cls(qualifiers=Tuple(), morph=frozenset())

    @property
    def is_polymorphic(self):
        return len(self.morph) > 1
    @property
    def is_monomorphic(self):
        return len(self.morph) == 1
    @property
    def is_amorphic(self): # modela unknown o any
        return len(self.morph) == 0




class Qualifier: ...

class Clousure(Qualifier):
    'Actua como clousure de un valor '
    ' Clousure(once | mut) P -> R '

class RefQualifier(Qualifier):
    '[] T'

class ArrayQualifier(Qualifier):
    '[:,:,6,...] '

class MapQualifier(Qualifier):
    '[T] U'

class TupleQualifier(Qualifier):
    '[T?] U'

class SetQualifier(Qualifier):
    '[] T'


if __name__ == "__main__":

    # -> Ret

    # common prefix: dado un tuple outer de tuples inners
    # extrae el prefijo comun de todos los elementos comunes de inner
    # devolviendo: un tuple prefijo (qualifiers), un tuple outer (class)
    # de tuples inners (types)
    def common_prefix[T](s: Iterable[Iterable[T]]) -> Iterable[T]:
        return (e[0] for e in takewhile(lambda x: all(c == x[0] for c in x), zip(*s)))

    import typing

    typing.get_args(Map[str, str])
    Map.__type_params__

    class C[X: int, Y: int]: ...

    # class Byte(Object):
    #    bitfield: Annotated[int, Type.parse("[8] Bit")]
