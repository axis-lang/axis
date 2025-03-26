from typing import Any, Dict
from weakref import WeakKeyDictionary
from protobase.traits import Weak


class MetadataContext:
    _metadata: WeakKeyDictionary[Weak, Dict[type, Any]]

    def __init__(self):
        self._metadata = WeakKeyDictionary()

    def get[T](self, obj, type: type[T]) -> T | None:
        if obj_md := self._metadata.get(obj):
            return obj_md.get(type, None)

    def set[T](self, obj, metadata: T):
        self._metadata[obj] = metadata

    def remove(self, obj):
        del self._metadata[obj]


_current_metadata_context = MetadataContext()


def get_metadata(obj: Any, type: type[T], /, default) -> T | None:
    return _current_metadata_context.get(obj, type)
