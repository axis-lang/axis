"""
POC for key containers

FEatures:
 - random key access
 - random index access
 - linear scan
 - hash collisions handling
 - index_of()

La division entre hashmaps y keyspaces puede incurrir en una interesante 
generalizacion entre hashmaps y arrays (tensores) dado que convierte al 
la parte de valor de un Map en una lista.

El keyspace seria analogo al concepto de Shape en los tensores
Esto puede tener propiedades interesantes:
 - Array como union entre tensores y mapas

Shape puede contener un keyspace!!

extent = list[int | KeySpace]

"""

# %%

from decimal import Decimal
from typing import Annotated, Iterator, Optional, Self, Sequence
from protobase import Obj, traits

type AnyInmutable = None | bool | int | float | str | bytes | Decimal | frozenset | traits.Inmutable


class OrderedSet[T: AnyInmutable](Obj):
    _key_index: dict[T, int]
    _items: list[T]

    def __init__(self, items: Sequence[T]):
        self._key_index = {key: index for index, key in enumerate(items)}
        self._items = list(items)

    def __contains__(self, key: T) -> bool:
        return key in self._key_index

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __hash__(self):
        return hash(self._items)

    def __eq__(self, other):
        if not isinstance(other, OrderedSet):
            return NotImplemented
        return self._items == other._items

    def __ne__(self, other):
        if not isinstance(other, OrderedSet):
            return NotImplemented
        return self._items != other._items

    def __repr__(self):
        return f"{type(self).__qualname__}({self._items})"

    def add(self, key: T):
        if key not in self._key_index:
            self._key_index[key] = len(self._items)
            self._items.append(key)


class Map[K: AnyInmutable, V](Obj):
    """
    Map is the datatype behind de Tuple and mapping objects in axis.
    """

    _keyspace: OrderedSet[K]
    _values: list[V]

    def __init__(self, init=None):
        self._keyspace = OrderedSet()
        self._values = []

    def __len__(self):
        return len(self._values)

    def __iter__(self) -> Iterator[K]:
        return iter(self._keyspace._items)

    def __getitem__(self, key: K) -> V:
        index = self._keyspace._key_index[key]
        return self._values[index]

    def __setitem__(self, key: K, value: V):
        try:
            index = self._keyspace._key_index[key]
            self._values[index] = value
        except KeyError:
            self._keyspace.add(key)
            self._values.append(value)

    def items(self) -> Iterator[tuple[K, V]]:
        return zip(self._keyspace._items, self._values)


"""

class OrderedSet[T: AnyInmutable](Obj, traits.Init):

    _load_threshold = 0.5

    class Entry(Obj, traits.Repr, traits.Init):
        # is_present: bool
        in_collision: bool = False
        index: int

    _hash_table: list[Optional[Entry]]
    _hash_collisions: list[list[int]]
    _items: list[T]

    @classmethod
    def new(cls, capacity=0):
        return cls(_hash_table=[None] * capacity, _hash_collisions=[], _items=[])

    @property
    def capacity(self):
        return len(self._hash_table)

    @property
    def hash_collision_count(self):
        return sum(len(colliders) for colliders in self._hash_collisions)

    def entry(self, key: T) -> Optional[Entry]:
        return self._hash_table[hash(key) % self.capacity]

    def __contains__(self, key: T) -> bool:
        return self.entry(key) is not None

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def add(self, new_item: T):
        self._check_capacity()

        h = hash((new_item,)) % self.capacity
        entry = self._hash_table[h]

        if entry is None:
            self._hash_table[h] = self.Entry(index=len(self._items))
            self._items.append(new_item)
            return

        if not entry.in_collision:
            if self._items[entry.index] == new_item:
                return  # elemento ya presente

            entry.in_collision = True  # ocurre una colision
            colliders = [entry.index, len(self._items)]
            entry.index = len(self._hash_collisions)
            self._hash_collisions.append(colliders)
            self._items.append(new_item)

        else:
            colliders = self._hash_collisions[entry.index]
            for index in colliders:
                if self._items[index] == new_item:
                    return  # elemento ya presente (en colision)

            colliders.append(len(self._items))
            self._items.append(new_item)

    def _check_capacity(self):
        if len(self._hash_table) == 0:
            self.capacity = 8
        elif len(self._items) / len(self._hash_table) >= self._load_threshold:
            self.capacity *= 2

    @capacity.setter
    def capacity(self, new_capacity: int):
        print(f"NC Load: {len(self)}, capacity: {self.capacity}, new {new_capacity}")
        if new_capacity < len(self._items):
            raise ValueError(
                "New capacity must be greater than the current number of items. "
                f"Current number of items: {len(self._items)}. "
                f"Proposed new capacity: {new_capacity}"
            )
        self._hash_table = [None] * new_capacity
        self._hash_collisions = []
        self._items, items = [], self._items

        for item in items:
            self.add(item)

    def index_of(self, key: T) -> Optional[int]:
        entry = self.entry(key)
        if entry is None:
            return None

        if not entry.in_collision:
            return entry.index

        colliders = self._hash_collisions[entry.index]
        for index in colliders:
            if self._items[index] == key:
                return index

        return None

    def __repr__(self):
        items = map(repr, self._items)
        return f"{type(self).__qualname__}({', '.join(items)})"

    def collisions(self):
        for colliders in self._hash_collisions:
            yield [self._items[index] for index in colliders]


if __name__ == "__main__":
    import random

    print("...")
    oset = OrderedSet.new()
    for x in range(1000):
        for y in range(1000):

            oset.add((x, y))

    # %%
    print(f"Collisions {oset.hash_collision_count / len(oset)*100:.1f}%")
    for colliders in enumerate(oset.collisions()):
        print(colliders)
        if colliders[0] > 100:
            break

# %%
"""
