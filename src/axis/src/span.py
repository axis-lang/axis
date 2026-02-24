from __future__ import annotations

from .file import File

__all__ = [
    "Span",
    "Line",
    "Position",
    "span_of",
    "tag_span_from",
]

Span = File.Span  # type: ignore[misc]
Line = File.Line  # type: ignore[misc]
Position = File.Position  # type: ignore[misc]


def span_of(obj: object) -> Span | None:
    return Span.of(obj)


def tag_span_from(from_: object, *to) -> Span | None:
    "aplica el source span de from_ a to"
    span = Span.of(from_)
    if span is None:
        return None
    span.tag(*to)
    return span
