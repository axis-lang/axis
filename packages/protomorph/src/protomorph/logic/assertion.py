from __future__ import annotations

from protobase import _, frozendict, slot_cached_property

import protomorph as pm

from .. import Builtin


type Goal = pm.Val


class Premise(Builtin):
    goal: Goal = _
    path: pm.Path = ()
    affirmative: bool = True

    @slot_cached_property
    def term(self) -> pm.Morph:
        return pm.Morph.from_val(self.goal, ctx=self)


class Assertion(Builtin):

    fact: Goal = _
    premises: frozenset[Premise] = frozenset()

    @property
    def is_fact(self) -> bool:
        return not self.premises

    @slot_cached_property
    def term(self) -> pm.Morph:
        return pm.Morph.from_val(self.fact, ctx=self)

    @slot_cached_property
    def frame_slots(self) -> frozendict[
        pm.Val[pm.Pattern.Slot[Assertion | Premise]],
        pm.Val,
    ]:
        return frozendict({
            slot: binding
            for canonical in (self.term, *(premise.term for premise in self.premises))
            for slot, binding in canonical.bindings.items()
            if binding.is_var
        })

    @slot_cached_property
    def frame_bindings(self) -> frozendict[
        pm.Val,
        frozenset[pm.Val[pm.Pattern.Slot[Assertion | Premise]]],
    ]:
        all_slots_by_binding: dict[
            pm.Val,
            set[pm.Val[pm.Pattern.Slot[Assertion | Premise]]],
        ] = {}

        for slot, binding in self.frame_slots.items():
            all_slots_by_binding.setdefault(binding, set()).add(slot)

        return frozendict(
            (binding, frozenset(slots))
            for binding, slots in all_slots_by_binding.items()
        )
    
