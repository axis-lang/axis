from protobase import Record

from axis import dom


class GlobalIndex(Record):
    ""
    # by tupleBlund -> Indice
    

    #arity_mapping: dict[int, ]


class Database(Record):

    global_indices: dict[dom.Ref, GlobalIndex]
