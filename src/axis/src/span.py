from __future__ import annotations
from typing import overload
from protobase import Metadata, Record, cached_property
from .file import File, Line, Position


class Span(Metadata, Record, frozen=True):
    file: File
    start: int
    end: int

    @classmethod
    def from_str(cls, content: str):
        return cls(File.from_buffer("<unnamed>", content), 0, len(content))

    def __len__(self) -> int:
        return self.end - self.start

    @overload
    def __getitem__(self, index: int) -> Position: ...

    @overload
    def __getitem__(self, index: slice) -> Span: ...

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index.start < 0 or index.stop > len(self):
                raise IndexError(f"Slice {index} out of range (0-{len(self)})")
            if index.start > index.stop:
                raise IndexError(f"Slice {index} invalid (start > stop)")

            return Span(
                file=self.file,
                start=self.start + index.start,
                end=self.start + index.stop,
            )
        elif isinstance(index, int):
            if index < 0 or index >= len(self):
                raise IndexError(f"Index {index} out of range (0-{len(self)})")
            return Position(self, index)
        else:
            raise TypeError(f"Invalid index type: {type(index)}")

    @cached_property
    def start_position(self) -> Position:
        return self.file.position_at_offset(self.start)

    @cached_property
    def end_position(self) -> Position:
        return self.file.position_at_offset(self.end)

    @property
    def start_line(self) -> Line:
        return self.start_position.line

    @property
    def end_line(self) -> Line:
        return self.start_position.line

    @property
    def is_multi_line(self) -> bool:
        return self.start_line.line_no != self.end_line.line_no

    @property
    def content(self) -> str:
        return self.file.content[self.start : self.end]

    def __str__(self):
        return self.content


def span_of(obj: object) -> Span | None:
    return Span.of(obj)


def tag_span_from(from_: object, *to) -> Span | None:
    "aplica el source span de from_ a to"
    span = Span.of(from_)
    if span is None:
        return None
    span.tag(*to)
