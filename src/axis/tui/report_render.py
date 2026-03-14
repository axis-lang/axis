from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderResult, RenderableType
from rich.style import Style
from rich.text import Text

from axis import log, src


@dataclass(frozen=True)
class ReportCharacters:
    hbar: str
    vbar: str
    vbar_break: str
    ltop: str
    lbot: str
    rarrow: str
    underline: str
    uarrow: str
    error: str
    warning: str
    info: str

    @staticmethod
    def ascii() -> "ReportCharacters":
        return ReportCharacters(
            hbar="-",
            vbar="|",
            vbar_break=":",
            ltop=",",
            lbot="`",
            rarrow=">",
            underline="^",
            uarrow="^",
            error="x",
            warning="!",
            info="i",
        )

    @staticmethod
    def unicode() -> "ReportCharacters":
        return ReportCharacters(
            hbar="\u2500",
            vbar="\u2502",
            vbar_break="\u00b7",
            ltop="\u256d",
            lbot="\u2570",
            rarrow="\u25b6",
            underline="\u2500",
            uarrow="\u25b2",
            error="\u00d7",
            warning="\u26a0",
            info="\u2139",
        )


@dataclass(frozen=True)
class ReportStyles:
    error: Style
    warning: Style
    info: Style
    header: Style
    code: Style
    line_number: Style
    gutter: Style
    note: Style
    suggestion: Style
    label_styles: dict[log.Report.LabelStyle, Style]
    highlights: tuple[Style, ...]

    @staticmethod
    def color() -> "ReportStyles":
        return ReportStyles(
            error=Style(color="red", bold=True),
            warning=Style(color="yellow", bold=True),
            info=Style(color="cyan", bold=True),
            header=Style(bold=True),
            code=Style(dim=True),
            line_number=Style(dim=True),
            gutter=Style(dim=True),
            note=Style(italic=True),
            suggestion=Style(underline=True),
            label_styles={
                log.Report.LabelStyle.PRIMARY: Style(color="red", bold=True),
                log.Report.LabelStyle.SECONDARY: Style(color="blue"),
            },
            highlights=(
                Style(color="magenta", bold=True),
                Style(color="yellow", bold=True),
                Style(color="green", bold=True),
            ),
        )

    @staticmethod
    def mono() -> "ReportStyles":
        base = Style()
        return ReportStyles(
            error=base,
            warning=base,
            info=base,
            header=base,
            code=base,
            line_number=base,
            gutter=base,
            note=base,
            suggestion=base,
            label_styles={
                log.Report.LabelStyle.PRIMARY: base,
                log.Report.LabelStyle.SECONDARY: base,
            },
            highlights=(base,),
        )


@dataclass(frozen=True)
class ReportTheme:
    characters: ReportCharacters
    styles: ReportStyles

    @staticmethod
    def ascii(color: bool = True) -> "ReportTheme":
        styles = ReportStyles.color() if color else ReportStyles.mono()
        return ReportTheme(characters=ReportCharacters.ascii(), styles=styles)

    @staticmethod
    def unicode(color: bool = True) -> "ReportTheme":
        styles = ReportStyles.color() if color else ReportStyles.mono()
        return ReportTheme(characters=ReportCharacters.unicode(), styles=styles)

    @staticmethod
    def mono() -> "ReportTheme":
        return ReportTheme(characters=ReportCharacters.ascii(), styles=ReportStyles.mono())


@dataclass(frozen=True)
class ReportRenderOptions:
    context_before: int = 1
    context_after: int = 1
    tab_width: int = 4
    show_notes: bool = True
    show_suggestion: bool = True
    show_source_header: bool = True
    show_primary_span_start: bool = True
    show_gutter: bool = True


@dataclass(frozen=True)
class LabelInfo:
    label: log.Report.Label
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    style: Style
    priority: int


class ReportRenderer:
    def __init__(
        self,
        theme: ReportTheme,
        options: ReportRenderOptions | None = None,
    ) -> None:
        self.theme = theme
        self.options = options or ReportRenderOptions()

    @classmethod
    def for_console(
        cls,
        console: Console,
        options: ReportRenderOptions | None = None,
        theme: ReportTheme | None = None,
    ) -> "ReportRenderer":
        return cls(theme or _default_theme(console), options)

    def render(self, report: log.Report) -> list[RenderableType]:
        renderables: list[RenderableType] = []

        header = self._render_header(report)
        if header is not None:
            renderables.append(header)

        grouped = self._group_labels(report.labels)
        for source, labels in grouped.items():
            renderables.extend(self._render_source_block(source, labels))

        if self.options.show_notes:
            for note in report.notes:
                renderables.append(Text(f"note: {note}", style=self.theme.styles.note))
        if self.options.show_suggestion and report.suggestion:
            renderables.append(
                Text(
                    f"help: {report.suggestion}",
                    style=self.theme.styles.suggestion,
                )
            )

        return renderables

    def _render_header(self, report: log.Report) -> Text | None:
        severity = report.severity
        severity_style = self._severity_style(severity)
        icon = self._severity_icon(severity)
        label = Text()
        label.append(f"{icon} ", style=severity_style)
        label.append(severity.name.lower(), style=severity_style)
        if report.code:
            label.append(f"[{report.code}]", style=self.theme.styles.code)
        label.append(f": {report.message}", style=self.theme.styles.header)
        return label

    def _group_labels(
        self, labels: Iterable[log.Report.Label]
    ) -> dict[src.Source, list[log.Report.Label]]:
        grouped: dict[src.Source, list[log.Report.Label]] = {}
        for label in labels:
            if label.source is None:
                continue
            grouped.setdefault(label.source, []).append(label)
        return grouped

    def _render_source_block(
        self, source: src.Source, labels: list[log.Report.Label]
    ) -> list[RenderableType]:
        renderables: list[RenderableType] = []
        infos = self._label_infos(source, labels)
        if not infos:
            return renderables

        ranges = self._merge_ranges(
            [
                (
                    max(1, info.start_line - self.options.context_before),
                    min(len(source), info.end_line + self.options.context_after),
                )
                for info in infos
            ]
        )

        for start_line, end_line in ranges:
            block_labels = [
                info
                for info in infos
                if info.start_line <= end_line and info.end_line >= start_line
            ]
            renderables.extend(
                self._render_context(source, block_labels, start_line, end_line)
            )

        return renderables

    def _render_context(
        self,
        source: src.Source,
        labels: list[LabelInfo],
        start_line: int,
        end_line: int,
    ) -> list[RenderableType]:
        renderables: list[RenderableType] = []
        linum_width = len(str(end_line))
        header_label = self._primary_label(labels)
        if self.options.show_source_header:
            header = Text(" " * (linum_width + 2), style=self.theme.styles.gutter)
            header.append(self.theme.characters.ltop, style=self.theme.styles.gutter)
            header.append(self.theme.characters.hbar, style=self.theme.styles.gutter)
            header.append(" ")
            header.append(self._source_header_text(source, header_label))
            renderables.append(header)

        for line_no in range(start_line, end_line + 1):
            line = source[line_no - 1]
            gutter = self._gutter_char(labels, line_no)
            prefix = self._line_prefix(line_no, linum_width, gutter)
            line_text = self._expand_tabs(line.content, self.options.tab_width)
            line_text_render = self._render_line_text(
                line_text, line.content, line_no, labels
            )
            prefix.append_text(line_text_render)
            renderables.append(prefix)

            pointer_lines = self._render_pointers(
                line_no, linum_width, gutter, line.content, labels
            )
            renderables.extend(pointer_lines)

        if self.options.show_source_header:
            footer = Text(" " * (linum_width + 2), style=self.theme.styles.gutter)
            footer.append(self.theme.characters.lbot, style=self.theme.styles.gutter)
            footer.append(
                self.theme.characters.hbar * 3, style=self.theme.styles.gutter
            )
            renderables.append(footer)

        return renderables

    def _label_infos(
        self, source: src.Source, labels: list[log.Report.Label]
    ) -> list[LabelInfo]:
        infos: list[LabelInfo] = []
        highlight_styles = self.theme.styles.highlights
        for index, label in enumerate(labels):
            if label.span is None:
                continue
            start_pos = source.position_at_offset(label.span.start)
            end_pos = source.position_at_offset(label.span.end)
            start_col = start_pos.col_no
            end_col = end_pos.col_no - 1
            if start_pos.line.line_no == end_pos.line.line_no and end_col < start_col:
                end_col = start_col

            label_style = label.style
            if label_style is not None:
                style = self.theme.styles.label_styles.get(label_style, Style())
            else:
                style = highlight_styles[index % len(highlight_styles)]

            priority = 0
            if label_style == log.Report.LabelStyle.PRIMARY:
                priority = 2
            elif label_style == log.Report.LabelStyle.SECONDARY:
                priority = 1

            infos.append(
                LabelInfo(
                    label=label,
                    start_line=start_pos.line.line_no,
                    end_line=end_pos.line.line_no,
                    start_col=start_col,
                    end_col=end_col,
                    style=style,
                    priority=priority,
                )
            )
        return infos

    def _render_line_text(
        self,
        expanded_text: str,
        raw_text: str,
        line_no: int,
        labels: list[LabelInfo],
    ) -> Text:
        if not expanded_text:
            return Text()

        line_len = len(expanded_text)
        style_map: list[tuple[int, Style | None]] = [(-1, None)] * line_len
        for info in labels:
            segment = self._segment_for_line(info, line_no, raw_text, expanded_text)
            if segment is None:
                continue
            start_idx, end_idx = segment
            for idx in range(start_idx, end_idx):
                if info.priority > style_map[idx][0]:
                    style_map[idx] = (info.priority, info.style)

        text = Text()
        run_start = 0
        current_style = style_map[0][1]
        for idx in range(1, line_len):
            style_at = style_map[idx][1]
            if style_at != current_style:
                text.append(expanded_text[run_start:idx], current_style)
                run_start = idx
                current_style = style_at
        text.append(expanded_text[run_start:line_len], current_style)
        return text

    def _render_pointers(
        self,
        line_no: int,
        linum_width: int,
        gutter: str,
        raw_text: str,
        labels: list[LabelInfo],
    ) -> list[RenderableType]:
        renderables: list[RenderableType] = []
        expanded_text = self._expand_tabs(raw_text, self.options.tab_width)
        for info in labels:
            if info.label.message is None:
                continue
            if line_no < info.start_line or line_no > info.end_line:
                continue
            if info.start_line != info.end_line and line_no != info.end_line:
                continue

            segment = self._segment_for_line(info, line_no, raw_text, expanded_text)
            if segment is None:
                continue
            start_idx, end_idx = segment
            start_col = start_idx + 1
            end_col = end_idx
            length = max(1, end_col - start_col + 1)

            pointer = Text()
            pointer.append(" " * (start_col - 1))
            if info.start_line != info.end_line:
                pointer.append(
                    self.theme.characters.lbot
                    + self.theme.characters.hbar * max(length - 1, 0),
                    style=info.style,
                )
            else:
                pointer.append(
                    self.theme.characters.underline * length,
                    style=info.style,
                )
            pointer.append(f" {info.label.message}", style=info.style)

            prefix = self._pointer_prefix(linum_width, gutter)
            prefix.append_text(pointer)
            renderables.append(prefix)

        return renderables

    def _segment_for_line(
        self,
        info: LabelInfo,
        line_no: int,
        raw_text: str,
        expanded_text: str,
    ) -> tuple[int, int] | None:
        if line_no < info.start_line or line_no > info.end_line:
            return None

        if (
            info.start_line != info.end_line
            and line_no == info.end_line
            and info.end_col <= 0
        ):
            return None

        if not expanded_text:
            return None

        if line_no == info.start_line:
            raw_start = info.start_col
        else:
            raw_start = 1

        if line_no == info.end_line:
            raw_end = info.end_col
        else:
            raw_end = len(raw_text)

        raw_start = max(1, min(raw_start, len(raw_text) + 1))
        raw_end = max(0, min(raw_end, len(raw_text)))
        if raw_end < raw_start:
            raw_end = raw_start

        start_col = _visual_col(raw_text, raw_start, self.options.tab_width)
        end_col = _visual_col(raw_text, raw_end, self.options.tab_width)

        start_idx = start_col - 1
        end_idx = max(start_col, end_col)
        end_idx = min(end_idx, len(expanded_text))
        if end_idx <= start_idx:
            end_idx = min(start_idx + 1, len(expanded_text))
        return start_idx, end_idx

    def _line_prefix(self, line_no: int, linum_width: int, gutter: str) -> Text:
        text = Text()
        text.append(" ", style=self.theme.styles.line_number)
        text.append(
            f"{line_no:>{linum_width}}", style=self.theme.styles.line_number
        )
        text.append(f" {self.theme.characters.vbar} ", style=self.theme.styles.gutter)
        if self.options.show_gutter:
            text.append(f"{gutter} ", style=self.theme.styles.gutter)
        return text

    def _pointer_prefix(self, linum_width: int, gutter: str) -> Text:
        text = Text()
        text.append(" " * (linum_width + 1), style=self.theme.styles.line_number)
        text.append(
            f" {self.theme.characters.vbar_break} ", style=self.theme.styles.gutter
        )
        if self.options.show_gutter:
            text.append(f"{gutter} ", style=self.theme.styles.gutter)
        return text

    def _gutter_char(self, labels: list[LabelInfo], line_no: int) -> str:
        if not self.options.show_gutter:
            return ""
        for info in labels:
            if info.start_line < line_no <= info.end_line:
                return self.theme.characters.vbar
            if info.start_line <= line_no < info.end_line:
                return self.theme.characters.vbar
        return " "

    def _severity_style(self, severity: log.Report.Severity) -> Style:
        match severity:
            case log.Report.Severity.ERROR:
                return self.theme.styles.error
            case log.Report.Severity.WARNING:
                return self.theme.styles.warning
            case log.Report.Severity.INFO:
                return self.theme.styles.info
        return self.theme.styles.header

    def _severity_icon(self, severity: log.Report.Severity) -> str:
        match severity:
            case log.Report.Severity.ERROR:
                return self.theme.characters.error
            case log.Report.Severity.WARNING:
                return self.theme.characters.warning
            case log.Report.Severity.INFO:
                return self.theme.characters.info
        return "!"

    def _source_header_text(self, source: src.Source, primary: LabelInfo | None) -> str:
        if primary is None:
            return str(source)
        if self.options.show_primary_span_start:
            return f"{source}:{primary.start_line}:{primary.start_col}"
        return str(source)

    def _primary_label(self, labels: list[LabelInfo]) -> LabelInfo | None:
        if not labels:
            return None
        for info in labels:
            if info.priority == 2:
                return info
        return labels[0]

    def _merge_ranges(self, ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
        if not ranges:
            return []
        ranges.sort()
        merged: list[tuple[int, int]] = [ranges[0]]
        for start, end in ranges[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end + 1:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        return merged

    def _expand_tabs(self, text: str, tab_width: int) -> str:
        if "\t" not in text:
            return text
        result: list[str] = []
        column = 1
        for ch in text:
            if ch == "\t":
                spaces = tab_width - ((column - 1) % tab_width)
                result.append(" " * spaces)
                column += spaces
            else:
                result.append(ch)
                column += 1
        return "".join(result)


def _visual_col(text: str, raw_col: int, tab_width: int) -> int:
    raw_col = max(1, min(raw_col, len(text) + 1))
    column = 1
    for ch in text[: raw_col - 1]:
        if ch == "\t":
            column += tab_width - ((column - 1) % tab_width)
        else:
            column += 1
    return column


def _default_theme(console: Console) -> ReportTheme:
    no_color = os.environ.get("NO_COLOR") not in (None, "", "0")
    if not console.is_terminal:
        return ReportTheme.ascii(color=False)
    if no_color or console.color_system is None:
        return ReportTheme.unicode(color=False)
    return ReportTheme.unicode(color=True)


def render_report(
    report: log.Report, console: Console, options: ConsoleOptions
) -> RenderResult:
    renderer = ReportRenderer.for_console(console)
    for renderable in renderer.render(report):
        yield renderable
