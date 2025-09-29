# %%

from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent

from protobase import  Record, cached_property



class File(Record, frozen=True):
    #dir: Dir
    path: Path
    buffer: str | None = None

    @classmethod
    def from_buffer(cls, path: Path|str, buffer: str) -> File:
        return cls(path=Path(path), buffer=dedent(buffer))

    @classmethod
    def from_path(cls, path: Path|str) -> File:
        """
        Creates a File object from a file path.
        """
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        if not path.is_file():
            raise IsADirectoryError(f"Path {path} is not a file")
        return cls(path=path)

    @cached_property
    def content(self) -> str:
        if self.buffer is not None:
            return self.buffer
        return self.path.read_text(encoding="utf-8")

    @cached_property
    def lines(self) -> tuple[Line, ...]:
        src = self.content
        starts = [0] + [i + 1 for i, ch in enumerate(src) if ch == "\n"]

        return tuple(
            Line(file=self, start=starts[i], end=starts[i + 1] - 1, line_no=i + 1)
            for i in range(len(starts) - 1)
        )

    def __len__(self) -> int:
        return len(self.lines)

    def __getitem__(self, line_no: int) -> Line:
        length = len(self.lines)
        if line_no < -length or line_no >= length:
            raise IndexError(f"Line number {line_no} out of range (0-{length})")
        return self.lines[line_no]

    def __iter__(self):
        for line in self.lines:
            yield line

    def __str__(self) -> str:
        return f"{self.path}"

    def line_at_offset(self, offset: int) -> Line:
        """
        Returns the line at the given offset in the file content.
        """
        if offset < 0 or offset > len(self.content):
            raise IndexError(f"Offset {offset} out of range (0-{len(self.content)})")

        lines = self.lines

        l = 0
        r = len(self.lines) - 1
        while l <= r:
            c = (l + r) // 2
            line = lines[c]
            if line.start <= offset <= line.end:
                return line
            elif offset < line.start:
                r = c - 1
            else:
                l = c + 1

        raise ValueError(f"Offset {offset} not found in any line")

    def position_at_offset(self, offset: int) -> Position:
        """
        Returns the line and column at the given offset in the file content.
        """
        line = self.line_at_offset(offset)
        col = offset - line.start + 1
        return Position(line=line, col_no=col)

class Line(Record, frozen=True):
    file: File
    start: int
    end: int
    line_no: int

    def __str__(self) -> str:
        return f"{self.file}:{self.line_no}"

    def __len__(self) -> int:
        return self.end - self.start

    def __getitem__(self, index: int) -> str:
        if index < 0 or index >= len(self):
            raise IndexError(f"Index {index} out of range (0-{len(self)})")
        return Position(self, index)

    @property
    def content(self) -> str:
        return self.file.content[self.start : self.end]

    @property
    def identation(self):
        content = self.content
        return content[: len(self) - len(content.lstrip(" \t"))]

    def startswith(self, prefix: str) -> bool:
        return self.file.content.startswith(prefix, self.start, self.end)

    def match(self, pattern: re.Pattern | str, offset: int = 0, full: bool = False):
        """
        Matches the line content with the given pattern.
        """
        if offset < 0 or offset > len(self):
            raise IndexError(f"Offset {offset} out of range (0-{len(self.content)})")

        if isinstance(pattern, str):
            pattern = compile(pattern)

        if full:
            return pattern.fullmatch(self.file.content, self.start + offset, self.end)
        else:
            return pattern.match(self.file.content, self.start + offset, self.end)

    def fullmatch(self, pattern: re.Pattern | str, offset: int = 0):
        self.match(pattern, offset, full=True)


class Position(Record, frozen=True):
    line: Line
    col_no: int

    @property
    def offset(self) -> int:
        return self.line.start + self.col_no - 1


if __name__ == "__main__":
    from re import compile


    file = File(
        Path("test.txt"),
        dedent(
            """
            This is a sample file

            With
              
            """
        ),
    )

    print(len(file))
