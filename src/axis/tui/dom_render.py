from __future__ import annotations

from rich.text import Text

from axis.dom.core import Ref


def format_ref(ref: Ref) -> str:
    parts: list[str] = []
    current = ref.data
    stack: list[Ref.Data] = []
    while current is not None:
        stack.append(current)
        current = current.parent
    for data in reversed(stack):
        segment = data.member
        if data.spec:
            segment = f"{segment}[...]"
        parts.append(segment)
    return ".".join(parts)


def render_ref(ref: Ref) -> Text:
    return Text(format_ref(ref))
