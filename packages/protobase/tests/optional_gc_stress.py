import gc
import unittest
import weakref

from protobase import flux


class GCStressTest(unittest.TestCase):
    def test_flux_cache_releases_objects(self) -> None:
        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def read(self) -> int:
                return self.value

        refs: list[weakref.ref] = []
        for i in range(200):
            obj = Box(i)
            obj.read()
            refs.append(weakref.ref(obj))
        obj = None
        gc.collect()
        self.assertTrue(all(ref() is None for ref in refs))
