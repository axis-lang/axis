from __future__ import annotations

import protomorph as pm

from axis import log


class Status(pm.Builtin):
    reports: tuple[log.Report, ...] = ()
    children: tuple["Status", ...] = ()

    @property
    def all_reports(self) -> tuple[log.Report, ...]:
        reports = list(self.reports)
        for child in self.children:
            reports.extend(child.all_reports)
        return tuple(reports)

    @property
    def is_ok(self) -> bool:
        return not any(report.severity is log.Report.Severity.ERROR for report in self.all_reports)

    def throw(self) -> None:
        for report in self.all_reports:
            if report.severity is log.Report.Severity.ERROR:
                report.throw()


__all__ = ["Status"]
