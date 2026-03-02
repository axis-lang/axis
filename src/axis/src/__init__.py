"""
Muchas de las estructuras de axis.src están diseñadas conforme la especificación LSP:
https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#basicJsonStructures
Esto es para facilitar la integración con herramientas que ya implementan esta especificación, como editores de código, linters, etc.
"""

from pathlib import Path

from .diagnostic import (  # noqa: F401
    Diagnostic,
    DiagnosticException,
    Label,
    LabelStyle,
    Severity,
    error,
    info,
    warning,
)
from .source import Source, SourceBuffer
from .fs import FSWatcher, SourceDir, SourceFile

Span = Source.Span  # type: ignore[misc]
Line = Source.Line  # type: ignore[misc]
Position = Source.Position  # type: ignore[misc]

__all__ = [
    "Line",
    "Path",
    "Position",
    "Source",
    "SourceBuffer",
    "SourceDir",
    "SourceFile",
    "FSWatcher",
    "Span",
    "Diagnostic",
    "DiagnosticException",
    "Label",
    "LabelStyle",
    "Severity",
    "error",
    "info",
    "warning",
    "span_of",
    "tag_span_from",
]


def span_of(obj: object) -> Source.Span | None:
    return Source.Span.of(obj)


def tag_span_from(from_: object, *to) -> Source.Span | None:
    "aplica el source span de from_ a to"
    span = Source.Span.of(from_)
    if span is None:
        return None
    span.tag(*to)
    return span
