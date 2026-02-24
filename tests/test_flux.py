import gc
import unittest
import weakref

from protobase import flux


class FluxMethodTest(unittest.TestCase):
    def test_cache_hits_for_same_args(self):
        calls = {"add": 0}

        class Counter:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def add(self, delta: int) -> int:
                calls["add"] += 1
                return self.value + delta

        counter = Counter(3)
        self.assertEqual(counter.add(2), 5)
        self.assertEqual(counter.add(2), 5)
        self.assertEqual(calls["add"], 1)
        self.assertEqual(counter.add(3), 6)
        self.assertEqual(calls["add"], 2)

    def test_invalidate_key(self):
        calls = {"add": 0}

        class Counter:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def add(self, delta: int) -> int:
                calls["add"] += 1
                return self.value + delta

        counter = Counter(1)
        self.assertEqual(counter.add(4), 5)
        self.assertEqual(counter.add(4), 5)
        self.assertEqual(calls["add"], 1)
        Counter.add.invalidate(counter, 4)
        self.assertEqual(counter.add(4), 5)
        self.assertEqual(calls["add"], 2)

    def test_invalidate_for(self):
        calls = {"add": 0}

        class Counter:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def add(self, delta: int) -> int:
                calls["add"] += 1
                return self.value + delta

        counter = Counter(10)
        self.assertEqual(counter.add(1), 11)
        self.assertEqual(counter.add(2), 12)
        self.assertEqual(calls["add"], 2)
        Counter.add.invalidate_for(counter)
        self.assertEqual(counter.add(1), 11)
        self.assertEqual(counter.add(2), 12)
        self.assertEqual(calls["add"], 4)


class FluxPropertyTest(unittest.TestCase):
    def test_property_cache(self):
        calls = {"value": 0}

        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.property
            def doubled(self) -> int:
                calls["value"] += 1
                return self.value * 2

        box = Box(7)
        self.assertEqual(box.doubled, 14)
        self.assertEqual(box.doubled, 14)
        self.assertEqual(calls["value"], 1)
        Box.doubled.invalidate(box)
        self.assertEqual(box.doubled, 14)
        self.assertEqual(calls["value"], 2)


class FluxDependencyTest(unittest.TestCase):
    def test_dependency_invalidation(self):
        calls = {"base": 0, "derived": 0}

        class Node:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def base(self) -> int:
                calls["base"] += 1
                return self.value

            @flux.method
            def derived(self) -> int:
                calls["derived"] += 1
                return self.base() + 1

        node = Node(5)
        self.assertEqual(node.derived(), 6)
        self.assertEqual(node.derived(), 6)
        self.assertEqual(calls["base"], 1)
        self.assertEqual(calls["derived"], 1)
        Node.base.invalidate(node)
        self.assertEqual(node.derived(), 6)
        self.assertEqual(calls["base"], 2)
        self.assertEqual(calls["derived"], 2)


class FluxCycleTest(unittest.TestCase):
    def test_cycle_detection(self):
        class Loop:
            __slots__ = ("__weakref__",)

            @flux.method
            def left(self) -> int:
                return self.right()

            @flux.method
            def right(self) -> int:
                return self.left()

        loop = Loop()
        with self.assertRaises(flux.CycleError) as ctx:
            loop.left()
        self.assertIn("flux cycle detected", str(ctx.exception))


class FluxFunctionTest(unittest.TestCase):
    def test_global_function_cache(self):
        calls = {"add": 0}

        @flux.method
        def add(a: int, b: int) -> int:
            calls["add"] += 1
            return a + b

        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(calls["add"], 1)
        add.invalidate(None, 2, 3)
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(calls["add"], 2)


class FluxWeakrefTest(unittest.TestCase):
    def test_slots_require_weakref(self):
        with self.assertRaises(TypeError):

            class BadSlots:
                __slots__ = ("value",)

                @flux.method
                def compute(self) -> int:
                    return 1

    def test_cache_does_not_keep_object_alive(self):
        class Ephemeral:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def read(self) -> int:
                return self.value

        obj = Ephemeral(9)
        self.assertEqual(obj.read(), 9)
        ref = weakref.ref(obj)
        self.assertIsNotNone(ref())
        obj = None
        gc.collect()
        self.assertIsNone(ref())
