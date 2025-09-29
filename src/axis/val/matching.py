from functools import singledispatchmethod
from protobase import Record

class Match(Record):
    ''
    #values: dict[]
    
    def __call__(self, a, b):
        ...

    @singledispatchmethod
    def match(self, a, b): ...

    # @classmethod
    # def impl(cls, type: )
        