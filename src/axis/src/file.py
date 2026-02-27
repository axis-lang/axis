from __future__ import annotations

import re
from pathlib import Path
from textwrap import dedent

from protobase import Metadata, Inmutable, cached_property, flux

from .fs import FileSystem, VirtualFileSystem, default_fs


class File(Inmutable):
    fs: FileSystem
    path: Path

    @classmethod
    def from_buffer(cls, path: Path | str, buffer: str, *, fs: FileSystem | None = None) -> File:
        target = Path(path)
        fs = fs or default_fs()
        fs.apply_text(target, dedent(buffer))
        return cls(path=target, fs=fs)

    @classmethod
    def from_path(cls, path: Path | str, *, fs: FileSystem | None = None) -> File:
        """
        Creates a File object from a file path.
        """
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        fs = fs or default_fs()
        if not fs.exists(path):
            raise IsADirectoryError(f"Path {path} is not a file")
        return cls(path=path, fs=fs)

    @flux.property
    def content(self) -> str:
        return self.fs.read_text(self.path)

    @flux.property
    def lines(self) -> tuple[File.Line, ...]:
        src = self.content  # type: ignore[assignment]
        starts = [0] + [i for i, ch in enumerate(src, 1) if ch == "\n"]  # type: ignore[arg-type]

        return tuple(
            File.Line(file=self, start=starts[i], end=starts[i + 1] - 1, line_no=i + 1)
            for i in range(len(starts) - 1)
        )

    def __len__(self) -> int:
        return len(self.lines)  # type: ignore[arg-type]

    def __getitem__(self, line_no: int) -> File.Line:
        length = len(self.lines)  # type: ignore[arg-type]
        if line_no < -length or line_no >= length:
            raise IndexError(f"Line number {line_no} out of range (0-{length})")
        return self.lines[line_no]  # type: ignore[index]

    def __iter__(self):
        for line in self.lines:  # type: ignore[assignment]
            yield line

    def __str__(self) -> str:
        return f"{self.path}"

    def line_at_offset(self, offset: int) -> File.Line:
        """
        Returns the line at the given offset in the file content.
        """
        content = self.content  # type: ignore[assignment]
        size = len(content)  # type: ignore[arg-type]
        if offset < 0 or offset > size:
            raise IndexError(f"Offset {offset} out of range (0-{size})")

        lines = self.lines  # type: ignore[assignment]

        l = 0
        r = len(self.lines) - 1  # type: ignore[arg-type]
        while l <= r:
            c = (l + r) // 2
            line = lines[c]  # type: ignore[index]
            if line.start <= offset <= line.end:
                return line
            elif offset < line.start:
                r = c - 1
            else:
                l = c + 1

        raise ValueError(f"Offset {offset} not found in any line")

    def position_at_offset(self, offset: int) -> File.Position:
        """
        Returns the line and column at the given offset in the file content.
        """
        line = self.line_at_offset(offset)
        col = offset - line.start + 1
        return File.Position(line=line, col_no=col)

    class Span(Metadata, Inmutable, hub=True): # type: ignore
        file: "File"
        start: int
        end: int

        @classmethod
        def from_str(cls, content: str) -> File.Span:
            fs = VirtualFileSystem()
            return cls(File.from_buffer(Path("<unnamed>"), content, fs=fs), 0, len(content))

        def __len__(self) -> int:
            return self.end - self.start

        def __getitem__(self, index):
            if isinstance(index, slice):
                if index.start < 0 or index.stop > len(self):
                    raise IndexError(f"Slice {index} out of range (0-{len(self)})")
                if index.start > index.stop:
                    raise IndexError(f"Slice {index} invalid (start > stop)")

                return File.Span(
                    file=self.file,
                    start=self.start + index.start,
                    end=self.start + index.stop,
                )
            elif isinstance(index, int):
                if index < 0 or index >= len(self):
                    raise IndexError(f"Index {index} out of range (0-{len(self)})")
                return File.Position(self, index)
            else:
                raise TypeError(f"Invalid index type: {type(index)}")

        @cached_property
        def start_position(self) -> File.Position:
            return self.file.position_at_offset(self.start)

        @cached_property
        def end_position(self) -> File.Position:
            return self.file.position_at_offset(self.end)

        @property
        def start_line(self) -> File.Line:
            return self.start_position.line  # type: ignore[return-value]

        @property
        def end_line(self) -> File.Line:
            return self.start_position.line  # type: ignore[return-value]

        @property
        def is_multi_line(self) -> bool:
            return self.start_line.line_no != self.end_line.line_no

        @property
        def content(self) -> str:
            return self.file.content[self.start : self.end]  # type: ignore[index,operator]

        def match(self, pattern: re.Pattern | str, offset: int = 0, full: bool = False):
            if offset < 0 or offset > len(self):
                raise IndexError(f"Offset {offset} out of range (0-{len(self.content)})")

            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            regex: re.Pattern = pattern

            if full:
                return regex.fullmatch(self.file.content, self.start + offset, self.end)
            else:
                return regex.match(self.file.content, self.start + offset, self.end)

        def fullmatch(self, pattern: re.Pattern | str, offset: int = 0):
            return self.match(pattern, offset, full=True)

        def __str__(self):
            return self.content

    class Line(Span):
        line_no: int

        def __str__(self) -> str:
            return f"{self.file}:{self.line_no}"

        @property
        def identation(self):
            content = self.content
            return content[: len(self) - len(content.lstrip(" \t"))]

        def startswith(self, prefix: str) -> bool:
            return self.file.content.startswith(prefix, self.start, self.end)  # type: ignore[operator]

    class Position(Inmutable):
        line: "File.Span"
        col_no: int

        @property
        def offset(self) -> int:
            return self.line.start + self.col_no - 1


if __name__ == "__main__":
    file = File.from_buffer(
        Path("test.txt"),
        dedent(
            """
            This is a sample file
            with multiple lines.
            It is used for testing.
             Indentation test.
             Another indented line.
             Line with spaces at the end.    
             Line with tabs at the end.    
             Line with mixed whitespace at the end. \t
            """
        ),
    )

    print(len(file))

