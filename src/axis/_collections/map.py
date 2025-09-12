from protobase import Record, frozendict, inmutable

@inmutable
class Map[K, V](Record, consed=True):
    _map: frozendict[K, V]

    def __init__(self, map: dict[K, V]):
        super().__init__(frozendict(map))

    def __rich_repr__(self):
        for entry in self.entries:
            yield entry

    def __len__(self):
        return len(self._map)

    def __getitem__(self, item: K) -> V:
        return self._map[item]

    def __setitem__(self, key, val):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item assignment"
        )

    def __delitem__(self, key):
        raise TypeError(
            f"'{self.__class__.__name__}' object doesn't support item deletion"
        )

    def __iter__(self):
        return iter(self.values)
    
    @property
    def values(self):
        return self._map.values()

    @property
    def keys(self):
        return self._map.keys()

    @property
    def entries(self):
        return self._map.items()
