# %%
from typing import Iterable, Self
from protobase import Record


class ContentTable[K: Iterable[K], V](Record):

    class Entry[K: Iterable[K], V](Record):
        # ref: K
        children: dict[K, Self] = {}
        items: set[V] = set()

    _root: Entry[K, V] = Entry()
    _by_ref: dict[K, Entry[K, V]] = {}

    @property
    def root(self):
        return self._root.items

    def __getitem__(self, ref: K) -> set[V]:
        return self._by_ref[ref].items

    def __setitem__(self, key: K, item: V) -> None:
        entry = self._root

        for parent in key:
            if parent not in entry.children:
                child = self.Entry()
                entry.children[parent] = child
                self._by_ref[parent] = child

            entry = entry.children[parent]

        entry.items.add(item)

    def children(self, ref: K) -> Iterable[K]:
        return self._by_ref[ref].children.keys()

    @classmethod
    def from_entries(cls, entries: Iterable[tuple[K, V]]) -> Self:
        self = cls()
        for ref, item in entries:
            self[ref] = item
        return self
