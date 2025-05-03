#%%
from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional

from protobase import Record, mutate
from rich import print
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from axis.dom import src


class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    INFO = auto()

class LabelStyle(Enum):
    PRIMARY = auto()
    SECONDARY = auto()

_SEVERITY_STYLE = {
    Severity.ERROR: Style(color="red", bold=True),
    Severity.WARNING: Style(color="yellow", bold=True),
    Severity.INFO: Style(color="blue", bold=True),
}

_LABEL_STYLE = {
    LabelStyle.PRIMARY: Style(color="white", bgcolor="red"),
    LabelStyle.SECONDARY: Style(color="white", bgcolor="blue"),
}


class Label(Record, frozen=True):
    span: src.Span
    message: str
    style: LabelStyle = LabelStyle.PRIMARY

    @property
    def file(self):
        return self.span.file

class Diagnostic(Record, frozen=True):
    severity: Severity
    message: str
    code: Optional[str] = None
    labels: tuple[Label] = ()
    notes: tuple[str] = ()
    suggestion: Optional[str] = None

    def label(
        self,
        span: src.Span,
        message: str = "",
        style: LabelStyle = LabelStyle.PRIMARY,
    ) -> Label:

        if not isinstance(span, src.Span):
            span = src.Span.of(span)

        if span is None:
            return self

        return mutate(self, labels=self.labels + (Label(span=span, message=message, style=style),))


    def note(self, message: str) -> Diagnostic:
        return mutate(self, notes=self.notes + (message,))

    def suggest(self, message: str) -> Diagnostic:
        return mutate(self, suggestion=message)
    
    def show(self) -> None:
        print(self)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        header = Text(f"{self.severity.name.lower()}[{self.code}]: {self.message}\n")
        header.stylize(_SEVERITY_STYLE[self.severity])
        yield header

        labels_by_file: Dict[Path, List[Label]] = {}
        for lbl in self.labels:
            labels_by_file.setdefault(lbl.file.path, []).append(lbl)

        for file_path, lbls in labels_by_file.items():
            file = lbls[0].file
            file_header = Text(f"{file_path}", style="bold")
            yield file_header
            spans = lbls
            # compute context lines
            line_ranges: Dict[int, List[Label]] = {}
            for lbl in spans:
                start_pos = file.position_at_offset(lbl.span.start)
                end_pos = file.position_at_offset(lbl.span.end)
                start_line = start_pos.line.line_no
                end_line = end_pos.line.line_no
                for ln in range(start_line, end_line + 1):
                    line_ranges.setdefault(ln, []).append(lbl)
            all_lines = sorted(line_ranges.keys())
            start_ctx = max(all_lines[0] - 1, 1)
            end_ctx = min(all_lines[-1] + 1, len(file))

            for ln in range(start_ctx, end_ctx + 1):
                line = file[ln-1]
                source = line.content
                gutter = f" {'>' if ln in all_lines else ' '} {ln} | "
                text = Text(gutter)
                if ln in line_ranges:
                    # highlight background for each label segment
                    idx = 0
                    segments: List[tuple[int,int,Label]] = []
                    for lbl in line_ranges[ln]:
                        start_pos = file.position_at_offset(lbl.span.start)
                        end_pos = file.position_at_offset(lbl.span.end)
                        s_ln = start_pos.line.line_no
                        e_ln = end_pos.line.line_no
                        if s_ln == ln:
                            start = start_pos.col_no - 1
                        else:
                            start = 0
                        if e_ln == ln:
                            end = end_pos.col_no - 1
                        else:
                            end = len(source)
                        segments.append((start, end, lbl))
                    segments.sort(key=lambda x: x[0])
                    last = 0
                    for start, end, lbl in segments:
                        # append plain
                        if start > last:
                            text.append(source[last:start])
                        # append highlighted
                        text.append(source[start:end], _LABEL_STYLE[lbl.style])
                        last = end
                    # remainder
                    if last < len(source):
                        text.append(source[last:])
                else:
                    text.append(source)
                yield text

            # annotations below multiline spans for messages
            for lbl in spans:
                start_pos = file.position_at_offset(lbl.span.start)
                end_pos = file.position_at_offset(lbl.span.end)
                start_line = start_pos.line.line_no
                end_line = end_pos.line.line_no
                
                # Display message for the label
                if lbl.message:
                    if start_line == end_line:
                        # For single-line spans, show the message below the line
                        s_col = start_pos.col_no - 1
                        e_col = end_pos.col_no - 1
                        gutter = " " * len(f"   {start_line} | ")
                        pointer = " " * s_col + "^" * (e_col - s_col)
                        msg = Text(f"{gutter}{pointer} {lbl.message}\n", style=_LABEL_STYLE[lbl.style])
                        yield msg
                    else:
                        # For multiline spans, show the message after the span
                        msg = Text(f"   → {lbl.message}\n", style=_LABEL_STYLE[lbl.style])
                        yield msg

        for note in self.notes:
            nt = Text(f"note: {note}\n", style="italic")
            yield nt
        if self.suggestion:
            sg = Text(f"suggestion: {self.suggestion}\n", style="underline")
            yield sg




def error(message: str):
    return Diagnostic(severity=Severity.ERROR, message=message)

def warning(message: str):
    return Diagnostic(severity=Severity.WARNING, message=message)

def info(message: str):
    return Diagnostic(severity=Severity.INFO, message=message)

# ===== Example / Test =====
if __name__ == "__main__":
    console = Console()
    content = (
        "pub fn process(data: &[i32]) -> i32 {\n"
        "    // sum the values\n"
        "    let sum = data.iter().sum();\n"
        "    // multiply if sum is positive\n"
        "    if sum > 0 {\n"
        "        let prod = data.iter()\n"
        "            .map(|v| v * sum)\n"
        "            .fold(1, |acc, x| acc * x);\n"
        "        prod\n"
        "    } else {\n"
        "        0\n"
        "    }\n"
        "}\n"
    )
    f2 = src.File(Path("example2.rs"), content)
    start_fold = content.find(".map(|v| v * sum)\n")
    end_fold = start_fold + 10
    span = src.Span(file=f2, start=start_fold, end=end_fold)
    lbl_fold = Label(span, "use checked_mul here", LabelStyle.PRIMARY)
    diag2 = Diagnostic(
        severity=Severity.WARNING,
        code="W200",
        message="Potential overflow",
        labels=[lbl_fold],
        notes=["Operations on large data slices may overflow."],
        suggestion="Switch to checked operations as needed."
    )
    console.print(diag2)

# %%
