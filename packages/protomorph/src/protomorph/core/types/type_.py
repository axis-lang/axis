from __future__ import annotations

from typing import Iterator as _Iterator

import protomorph.core as _pm
from protobase import frozendict as _frozendict

from protomorph.core.foundation import Builtin as _Builtin


type Schema = _pm.Tuple[*tuple[_pm.Type, ...]]

class Type[T](_Builtin, abstract=True):
    def metatype(self) -> Type:
        raise NotImplementedError(f"Metatype not implemented for {self!r}")

    def make(self, data: T):
        return _pm.make_value(self, data)

    @property
    def schema(self) -> Schema | None:
        return None

    @property
    def is_leaf(self) -> bool:
        return self.schema is None

    def __len__(self) -> int:
        schema = self.schema
        if schema is None:
            raise TypeError(
                f"Leaf type has no structural length: {type(self).__name__}"
            )
        return len(schema)

    def __iter__(self) -> _Iterator:
        schema = self.schema
        if schema is None:
            raise TypeError(
                f"Leaf type has no structural iteration: {type(self).__name__}"
            )
        for child in schema:
            yield child.content

    def __getitem__(self, key: int | slice) -> _pm.Val[Type] | _pm.Tuple:
        schema = self.schema
        if schema is None:
            raise TypeError(
                f"Leaf type has no structural indexing: {type(self).__name__}"
            )
        return schema[key]


def compatible(left: Type, right: Type) -> bool:
    if left is right:
        return True

    return bool(_pm.current_realm().compatible_structure(left, right))
