from __future__ import annotations

from typing import Optional, Protocol, Self
from xml.sax.handler import EntityResolver

from protobase import Record, frozendict, inmutable

from axis import syn, val, log

@inmutable
class ScopeKey(Protocol):
    name: str
    at: Optional[str]


class Scope[K: ScopeKey, V: syn.Node](Record, frozen=True):
    """
    Semantic scope representa un espacio de nombres jerarquico.

    """

    class Builder[K: ScopeKey, V](Record):
        name: Optional[str] = None
        parent: Optional[Scope] = None
        entries: dict[K, list[V]] = {}

        def add(self, key: K, value: V) -> Self:
            self.entries.setdefault(key, []).append(value)

        def build(self) -> Scope[K, V]:
            entries = {}
            for key, valueset in self.entries.items():
                if len(valueset) > 1:
                    log.error(f"Duplicate key {key} in scope").with_label(v.as_label for v in valueset).emit()
                    # TODO: add dummy entry
                else:
                    entries[key] = valueset[0]

            return Scope(
                name=self.name,
                parent=self.parent,
                entries=frozendict(entries),
            )

    name: Optional[str] = None
    parent: Optional[Scope] = None
    entries: frozendict[K, V]

    def lookup(self, name: str, at: Optional[str] = None) -> Optional[V]:

        if at is None or at == self.name:
            try:
                return self.entries[name]
            except KeyError:
                pass

        if self.parent is not None:
            return self.parent.lookup(name, at)

        return None
