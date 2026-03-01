from axis.dom.core import Ref


type Val[M: Val | None = Val, D: Data] = tuple[M, D]

type Data = str | int | bool | tuple[Data, ...]
type TupleData = tuple[Data, ...]

Empty = ()


def val(meta: Val | None, data: Data) -> Val:
    return (meta, data)



# Ref stuff

type RefMeta = tuple[RefMeta | None, Tuple]
type RefData = tuple[RefData | None, str, TupleData]

def ref_root(nm: str) -> Val[RefType, RefData]:
    meta = val(None, (None, Empty))
    return val(meta, (None, nm, Empty))
