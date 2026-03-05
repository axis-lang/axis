from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.style import Style
from rich.text import Text

from axis import src
from axis.log.report import Report


@dataclass(frozen=True)
class ReportTheme:
    severity_styles: dict[Report.Severity, Style] = field(
        default_factory=lambda: {
            Report.Severity.ERROR: Style(color="red", bold=True),
            Report.Severity.WARNING: Style(color="yellow", bold=True),
            Report.Severity.INFO: Style(color="cyan", bold=True),
        }
    )
    label_styles: dict[Report.LabelStyle, Style] = field(
        default_factory=lambda: {
            Report.LabelStyle.PRIMARY: Style(color="white", bgcolor="red"),
            Report.LabelStyle.SECONDARY: Style(color="white", bgcolor="blue"),
        }
    )
    header_style: Style = Style(bold=True)
    note_style: Style = Style(italic=True)
    suggestion_style: Style = Style(underline=True)


@dataclass(frozen=True)
class ReportRenderOptions:
    context_before: int = 1
    context_after: int = 1
    show_notes: bool = True
    show_suggestion: bool = True
    show_source_header: bool = True


class ReportRenderer:
    def __init__(
        self,
        theme: ReportTheme | None = None,
        options: ReportRenderOptions | None = None,
    ) -> None:
        self.theme = theme or ReportTheme()
        self.options = options or ReportRenderOptions()

    def render(self, report: Report) -> list[RenderableType]:
        renderables: list[RenderableType] = []

        header = self._render_header(report)
        if header is not None:
            renderables.append(header)

        for source, labels in self._group_labels(report.labels).items():
            renderables.extend(self._render_source_block(source, labels))

        if self.options.show_notes:
            for note in report.notes:
                renderables.append(Text(f"note: {note}", style=self.theme.note_style))
        if self.options.show_suggestion and report.suggestion:
            renderables.append(
                Text(
                    f"suggestion: {report.suggestion}",
                    style=self.theme.suggestion_style,
                )
            )

        return renderables

    def _render_header(self, report: Report) -> Text | None:
        code = f"[{report.code}]" if report.code else ""
        label = Text(
            f"{report.severity.name.lower()}{code}: {report.message}",
            style=self.theme.severity_styles.get(report.severity, self.theme.header_style),
        )
        return label

    def _group_labels(
        self, labels: Iterable[Report.Label]
    ) -> dict[src.Source, list[Report.Label]]:
        grouped: dict[src.Source, list[Report.Label]] = {}
        for label in labels:
            if label.source is None:
                continue
            grouped.setdefault(label.source, []).append(label)
        return grouped

    def _render_source_block(
        self, source: src.Source, labels: list[Report.Label]
    ) -> list[RenderableType]:
        renderables: list[RenderableType] = []
        if not labels:
            return renderables

        if self._should_show_header(source):
            renderables.append(Text(str(source), style=self.theme.header_style))

        line_ranges: dict[int, list[Report.Label]] = {}
        for label in labels:
            if label.span is None:
                continue
            start_pos = source.position_at_offset(label.span.start)
            end_pos = source.position_at_offset(label.span.end)
            start_line = start_pos.line.line_no
            end_line = end_pos.line.line_no
            for ln in range(start_line, end_line + 1):
                line_ranges.setdefault(ln, []).append(label)

        all_lines = sorted(line_ranges.keys())
        if not all_lines:
            return renderables

        start_ctx = max(all_lines[0] - self.options.context_before, 1)
        end_ctx = min(all_lines[-1] + self.options.context_after, len(source))

        for ln in range(start_ctx, end_ctx + 1):
            line = source[ln - 1]
            line_content = line.content
            gutter = f" {'>' if ln in all_lines else ' '} {ln} | "
            text = Text(gutter)
            if ln in line_ranges:
                segments: list[tuple[int, int, Report.Label]] = []
                for label in line_ranges[ln]:
                    if label.span is None:
                        continue
                    start_pos = source.position_at_offset(label.span.start)
                    end_pos = source.position_at_offset(label.span.end)
                    s_ln = start_pos.line.line_no
                    e_ln = end_pos.line.line_no
                    if s_ln == ln:
                        start = start_pos.col_no - 1
                    else:
                        start = 0
                    if e_ln == ln:
                        end = end_pos.col_no - 1
                    else:
                        end = len(line_content)
                    segments.append((start, end, label))
                segments.sort(key=lambda x: x[0])
                last = 0
                for start, end, label in segments:
                    if start > last:
                        text.append(line_content[last:start])
                    label_style = label.style
                    style = (
                        self.theme.label_styles.get(label_style, Style())
                        if label_style is not None
                        else Style()
                    )
                    text.append(line_content[start:end], style)
                    last = end
                if last < len(line_content):
                    text.append(line_content[last:])
            else:
                text.append(line_content)
            renderables.append(text)

        for label in labels:
            if label.span is None:
                continue
            start_pos = source.position_at_offset(label.span.start)
            end_pos = source.position_at_offset(label.span.end)
            start_line = start_pos.line.line_no
            end_line = end_pos.line.line_no
            if label.message:
                if start_line == end_line:
                    s_col = start_pos.col_no - 1
                    e_col = end_pos.col_no - 1
                    gutter = " " * len(f"   {start_line} | ")
                    pointer = " " * s_col + "^" * max(e_col - s_col, 1)
                    label_style = label.style
                    style = (
                        self.theme.label_styles.get(label_style, Style())
                        if label_style is not None
                        else Style()
                    )
                    renderables.append(
                        Text(
                            f"{gutter}{pointer} {label.message}",
                            style=style,
                        )
                    )
                else:
                    renderables.append(
                        Text(
                            f"   -> {label.message}",
                            style=self.theme.label_styles.get(
                                label.style or Report.LabelStyle.PRIMARY,
                                Style(),
                            ),
                        )
                    )

        return renderables

    def _should_show_header(self, source: src.Source) -> bool:
        if not self.options.show_source_header:
            return False
        return not isinstance(source, src.SourceBuffer)


def render_report(
    report: Report, console: Console, options: ConsoleOptions
) -> RenderResult:
    renderer = ReportRenderer()
    for renderable in renderer.render(report):
        yield renderable
