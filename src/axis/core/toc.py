"""
Base de datos jerarquica:

class DBEntry[K: Sequence[S], V, S]:
    key: K
    children: dict[S, Self] = {}
    items: set[V] = set()

class Entity(DBEntry[Ref]): 
    ...

db = Entity.Database()
db[ref..]
"""
# %%
from typing import Iterable, Self
from protobase import Record, frozendict
from axis.core import val, syn

"""
Obedece a un preanalisis que tansolo debe ocuparse de:
desde este path se definen los items N (nombres) con las referencias R..
"""

class ContentTable(Record):
    """
    La tabla de contenido (aka toc) sirve de indice es una estructura de entradas arboreas
    """

    class Entry(Record):
        ref: val.Ref
        children: dict['val.Ref.Step', Self] = {}
        items: set[syn.Item] = set()


    _root: Entry = Entry(ref=val.Ref.root)
    _by_ref: dict[val.Ref, Entry] = {}  # fast lookup by ref

    @property
    def root(self):
        return self._root.items


    def __getitem__(self, ref: val.Ref) -> set[syn.Item]:
        return self._by_ref[ref].items

    def __setitem__(self, key: val.Ref, item: syn.Item) -> None:
        assert len(key.steps) > 0, "cannot set root"

        entry = self._root

        for level, step in enumerate(key.steps):
            if step not in entry.children:
                parent = key.parent_at(level)
                child = self.Entry(ref=parent)
                entry.children[step] = child
                self._by_ref[parent] = child

            entry = entry.children[step]

        entry.items.add(item)

    @classmethod
    def from_entries(cls, entries: Iterable[tuple[val.Ref, syn.Item]]) -> Self:
        self = cls()        
        for ref, item in entries:
            self[ref] = item
        return self
