from __future__ import annotations

import protomorph_ as pm

__all__ = ["Goal", "Clause"]


type Goal = pm.Spec


class Clause(pm.Builtin):
    ANCHOR = "std.logic.Clause"

    head: pm.Spec
    body: tuple[Goal, ...] = ()
