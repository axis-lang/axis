from __future__ import annotations

from typing import NewType

from protobase import Consed

Id = NewType("Id", str)
Anchor = NewType("Anchor", str)

_RECONSTRUCT = object()


_ALL_BUILTINS: set[type["Builtin"]] = set()


class Builtin(Consed, abstract=True):
    def __repr__(self) -> str:
        from .display import repr_any
        return repr_any(self)

    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return

        _ALL_BUILTINS.add(cls)

        try:
            import protomorph.core as pm_core

            pm_core.NativeHost.all_builtins.invalidate_for(pm_core.NATIVE_HOST)
        except (AttributeError, ImportError):
            pass
