from decimal import Decimal
from typing import Union
from .index import *
from .tuple_ import *

type Natural = int
type Integer = int
type Text = str
type Float = float
type Boolean = bool

type All = Union[
    None,
    Boolean,
    Integer,
    Natural,
    Decimal,
    float,
    str,
    bytes,
    tuple,
    Index,
    Tuple,
    # frozenset,
    # frozendict,
    # Pattern,
    # Path,
    # datetime,
    # date,
    # timedelta,
]
