from __future__ import annotations

from protobase import Consed as _Consed, flux as _flux
import protomorph


ALL_BUILTINS: set[type["Builtin"]] = set()

class Builtin(_Consed, abstract=True):
    def __repr__(self) -> str:
        from ..display import repr_any

        return repr_any(self)

    def __init_subclass__(cls, abstract: bool = False, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if abstract:
            return

        ALL_BUILTINS.add(cls)

        try:
            import protomorph as pm_core  # type: ignore[import-not-found]

            pm_core.NativeRealm.all_builtins.invalidate_for(pm_core.NATIVE_REALM)
        except (AttributeError, ImportError):
            pass
