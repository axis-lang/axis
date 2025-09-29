from functools import singledispatchmethod
from protobase import Record

class Unification(Record):
    ''
    #values: dict[]
    
    def __call__(self, a, b):
        ...

    @singledispatchmethod
    def unify(self, a, b): ...

    # @classmethod
    # def impl(cls, type: )
        