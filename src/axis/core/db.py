from protobase import Record

from axis import val


class GlobalIndex(Record):
    ""
    # by tupleBlund -> Indice
    

    #arity_mapping: dict[int, ]


class Database(Record):

    global_indices: dict[val.GlobalPath, GlobalIndex]

