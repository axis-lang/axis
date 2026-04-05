from __future__ import annotations

from protobase import flux, frozendict
import protomorph as pm

from axis import sem

from .entity import ContributionSet, EntityView


class SpecCluster(ContributionSet):
    bucket: pm.MatchBucket
    templates_by_contribution: frozendict[EntityView.SpecContribution, tuple[pm.Constraint, ...]] = frozendict()

    @flux.property
    def status(self) -> sem.Status:
        return sem.Status()


__all__ = ["SpecCluster"]
