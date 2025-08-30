#%%
"""
map reduce eample

def Axis(
    length: Option Natural = None
)

def Collection[
  ..axis: Tuple Axis
]

einsum = map_reduce.with(map=mul, reduce=sum)

"""
from protobase import Object, Record

class Collection(Record, frozen=True):
    axis: dict[str, int]


def map_reduce(*inputs: Collection, map, reduce) -> Collection:
    ...

    
