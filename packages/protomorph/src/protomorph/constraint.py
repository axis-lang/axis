from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import protomorph as pm


class Constraint(pm.Builtin):
    subject: pm.Val
    term: pm.Val
    target: pm.Val

    @property
    def template_goal_carrier(self) -> pm.Val:
        return pm.val(pm.Spec.of("std.facts.Conforms", self.subject.content, to=self.target.content))

    @property
    def goal_carrier(self) -> pm.Val:
        return self.template_goal_carrier

    @property
    def template_goal(self) -> pm.Spec:
        return cast(pm.Spec, self.template_goal_carrier.content)

    @property
    def goal(self) -> pm.Spec:
        return cast(pm.Spec, self.goal_carrier.content)

    # def subst(self, mapping: Mapping[pm.Val, pm.Val]) -> Constraint:
    #     return type(self)(
    #         subject=pm.walk_subst(self.subject, mapping),
    #         term=pm.walk_subst(self.term, mapping),
    #         target=pm.walk_subst(self.target, mapping),
    #     )

    # def subst_self(self, spec: pm.Val | pm.AnyData) -> Constraint:
    #     return type(self)(
    #         subject=pm.subst_self(self.subject, spec),
    #         term=pm.subst_self(self.term, spec),
    #         target=pm.subst_self(self.target, spec),
    #     )

    # def goal_for(self, spec: pm.Val | pm.AnyData) -> pm.Spec:
    #     return self.subst_self(spec).goal
