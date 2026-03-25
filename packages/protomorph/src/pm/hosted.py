from __future__ import annotations

from typing import Any, cast

from .abstract.contract import Item

import pm
from .foundation import Builtin
from .type_ import Type
from .carrier import Tuple


class Host(Builtin):
    """Base host for nominal hosted types."""

    def schema_for(self, spec: pm.Spec) -> pm.TupleLikeType | None:
        return None

    def val_is_leaf(self, meta: pm.Type, data: Any) -> bool:
        return True

    def val_children(
        self,
        meta: pm.Type,
        data: Any,
    ) -> tuple[pm.Carrier, ...]:
        return ()

    def val_reconstruct(
        self,
        meta: pm.Type,
        children: tuple[pm.Carrier, ...],
    ) -> Any:
        raise NotImplementedError


def current_host() -> pm.Host:
    return pm.HOST.get()
