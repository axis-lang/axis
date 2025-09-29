from __future__ import annotations
from typing import Union
from protobase import Record, frozendict, cached_property
from decimal import Decimal

type Natural = int
type Integer = int
type Text = str
type Float = float
type Boolean = bool

class SparseIndex[K: All = All](Record, frozen=True, consed=True):
    """
    Implementa `SparseIndex I`
    """

    entries: tuple[K | None, ...]

    def __post_init__(self):
        # error if not unique non-null keys
        non_null_keys = [k for k in self.entries if k is not None]
        if len(non_null_keys) != len(set(non_null_keys)):
            # print the repeated keys
            seen = set()
            duplicates = set()
            for k in non_null_keys:
                if k in seen:
                    duplicates.add(k)
                else:
                    seen.add(k)
            raise ValueError(f"Duplicate keys in SparseIndex: {duplicates}")

    @cached_property
    def offsets(self) -> frozendict[K, int]:
        return frozendict({k: i for i, k in enumerate(self.entries) if k is not None})

    # def __getitem__(self, key: K) -> int | None:
    #     return self.offsets.get(key, None)

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
    SparseIndex,
    # frozenset,
    # frozendict,
    # Pattern,
    # Path,
    # datetime,
    # date,
    # timedelta,
]
