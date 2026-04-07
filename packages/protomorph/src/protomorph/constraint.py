from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import protomorph as pm


class Constraint(pm.Builtin):
    subject: pm.Carrier
    term: pm.Carrier
    target: pm.Carrier

    @property
    def template_goal_carrier(self) -> pm.Carrier:
        return pm.wrap(pm.Spec.of("std.facts.Conforms", self.subject.fetch(), to=self.target.fetch()))

    @property
    def goal_carrier(self) -> pm.Carrier:
        return self.template_goal_carrier

    @property
    def template_goal(self) -> pm.Spec:
        return cast(pm.Spec, self.template_goal_carrier.fetch())

    @property
    def goal(self) -> pm.Spec:
        return cast(pm.Spec, self.goal_carrier.fetch())

    def subst(self, mapping: Mapping[pm.Carrier, pm.Carrier]) -> Constraint:
        return type(self)(
            subject=self.subject.subst(mapping),
            term=self.term.subst(mapping),
            target=self.target.subst(mapping),
        )

    def subst_self(self, spec: pm.Carrier | pm.Datum) -> Constraint:
        return type(self)(
            subject=self.subject.subst_self(spec),
            term=self.term.subst_self(spec),
            target=self.target.subst_self(spec),
        )

    def goal_for(self, spec: pm.Carrier | pm.Datum) -> pm.Spec:
        return self.subst_self(spec).goal
