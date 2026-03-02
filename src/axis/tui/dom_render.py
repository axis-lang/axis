from __future__ import annotations

from typing import cast

from rich.text import Text

from axis.dom.core import Anchor, Ref, Spec


def format_ref(ref: Ref) -> str:
    anchor = ref.anchor
    parts: list[str] = []
    current = cast(Anchor.Data | None, anchor.data)
    stack: list[Anchor.Data] = []
    while current is not None:
        stack.append(current)
        current = current.parent
    for data in reversed(stack):
        parts.append(data.member)
    if isinstance(ref, Spec):
        suffix = "[]" if ref.spec is None else "[...]"
        if parts:
            parts[-1] = f"{parts[-1]}{suffix}"
    return ".".join(parts)


def render_ref(ref: Ref) -> Text:
    return Text(format_ref(ref))
