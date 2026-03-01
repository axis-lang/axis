from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent
from typing import cast, overload

from protobase import Metadata, Inmutable, cached_property, flux

__all__ = ["Source", "SourceBuffer"]


class Source(Inmutable, abstract=True):
    path: Path

    @property
    def content(self) -> str:
        raise NotImplementedError

    @flux.property
    def lines(self) -> tuple["Source.Line", ...]:
        src = self.content
        starts = [0] + [i for i, ch in enumerate(src, 1) if ch == "\n"]

        return tuple(
            Source.Line(source=self, start=starts[i], end=starts[i + 1] - 1, line_no=i + 1)
            for i in range(len(starts) - 1)
        )

    def __len__(self) -> int:
        return len(self.lines)

    def __getitem__(self, line_no: int) -> "Source.Line":
        length = len(self.lines)
        if line_no < -length or line_no >= length:
            raise IndexError(f"Line number {line_no} out of range (0-{length})")
        return self.lines[line_no]

    def __iter__(self):
        for line in self.lines:
            yield line

    def __str__(self) -> str:
        return f"{self.path}"

    def line_at_offset(self, offset: int) -> "Source.Line":
        """
        Returns the line at the given offset in the source content.
        """
        content = self.content
        size = len(content)
        if offset < 0 or offset > size:
            raise IndexError(f"Offset {offset} out of range (0-{size})")

        lines = self.lines

        l = 0
        r = len(lines) - 1
        while l <= r:
            c = (l + r) // 2
            line = lines[c]
            if line.start <= offset <= line.end:
                return line
            if offset < line.start:
                r = c - 1
            else:
                l = c + 1

        raise ValueError(f"Offset {offset} not found in any line")

    def position_at_offset(self, offset: int) -> "Source.Position":
        """
        Returns the line and column at the given offset in the source content.
        """
        line = self.line_at_offset(offset)
        col = offset - line.start + 1
        return Source.Position(line=line, col_no=col)

    class Span(Metadata, Inmutable, hub=True):  # type: ignore
        source: "Source"
        start: int
        end: int

        @classmethod
        def from_str(cls, content: str) -> "Source.Span":
            return cls(SourceBuffer.from_str(content), 0, len(content))

        def __len__(self) -> int:
            return self.end - self.start

        @overload
        def __getitem__(self, index: slice) -> "Source.Span": ...
        @overload
        def __getitem__(self, index: int) -> "Source.Position": ...

        def __getitem__(self, index: slice | int) -> "Source.Span | Source.Position":
            if isinstance(index, slice):
                if index.start < 0 or index.stop > len(self):
                    raise IndexError(f"Slice {index} out of range (0-{len(self)})")
                if index.start > index.stop:
                    raise IndexError(f"Slice {index} invalid (start > stop)")

                return Source.Span(
                    source=self.source,
                    start=self.start + index.start,
                    end=self.start + index.stop,
                )
            if isinstance(index, int):
                if index < 0 or index >= len(self):
                    raise IndexError(f"Index {index} out of range (0-{len(self)})")
                return Source.Position(self, index)
            raise TypeError(f"Invalid index type: {type(index)}")

        @cached_property
        def start_position(self) -> "Source.Position":
            return self.source.position_at_offset(self.start)

        @cached_property
        def end_position(self) -> "Source.Position":
            return self.source.position_at_offset(self.end)

        @property
        def start_line(self) -> "Source.Line":
            return cast(Source.Line, self.start_position.line)

        @property
        def end_line(self) -> "Source.Line":
            return cast(Source.Line, self.start_position.line)

        @property
        def is_multi_line(self) -> bool:
            return self.start_line.line_no != self.end_line.line_no

        @property
        def content(self) -> str:
            return self.source.content[self.start : self.end]

        def match(self, pattern: re.Pattern | str, offset: int = 0, full: bool = False):
            if offset < 0 or offset > len(self):
                raise IndexError(f"Offset {offset} out of range (0-{len(self.content)})")

            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            regex: re.Pattern = pattern

            if full:
                return regex.fullmatch(self.source.content, self.start + offset, self.end)
            return regex.match(self.source.content, self.start + offset, self.end)

        def fullmatch(self, pattern: re.Pattern | str, offset: int = 0):
            return self.match(pattern, offset, full=True)

        def __str__(self):
            return self.content

    class Line(Span):
        line_no: int

        def __str__(self) -> str:
            return f"{self.source}:{self.line_no}"

        @property
        def identation(self):
            content = self.content
            return content[: len(self) - len(content.lstrip(" \t"))]

        def startswith(self, prefix: str) -> bool:
            return self.source.content.startswith(prefix, self.start, self.end)

    class Position(Inmutable):
        line: "Source.Span"
        col_no: int

        @property
        def offset(self) -> int:
            return self.line.start + self.col_no - 1


class SourceBuffer(Source):
    token: int

    def __init__(self, path: Path | str, text: str) -> None:
        object.__setattr__(self, "path", Path(path))
        object.__setattr__(self, "token", id(self))
        self.buffer = dedent(text)

    @classmethod
    def from_str(cls, content: str, path: Path | str = "<unnamed>") -> "SourceBuffer":
        return cls(path=path, text=content)

    @flux.input
    def buffer(self) -> str:
        return ""

    @flux.property
    def _content(self) -> str:
        return self.buffer

    @property  # type: ignore[override]
    def content(self) -> str:
        return self._content
