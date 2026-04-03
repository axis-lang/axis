import gc
import unittest
import weakref
from typing import Callable, cast

from protobase import Inmutable, flux


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
        cast(flux.Query, Counter.add).invalidate(counter, 4)
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
        cast(flux.Query, Counter.add).invalidate_for(counter)
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
        cast(flux.Query, Box.doubled).invalidate(box)
        self.assertEqual(box.doubled, 14)
        self.assertEqual(calls["value"], 2)


class FluxInputTest(unittest.TestCase):
    def test_input_set_and_invalidate(self):
        calls = {"doubled": 0}

        class Config:
            __slots__ = ("__weakref__",)

            @flux.input
            def value(self) -> int:
                raise NotImplementedError

            @flux.property
            def doubled(self) -> int:
                calls["doubled"] += 1
                return cast(int, self.value) * 2

        cfg = Config()
        cfg.value = 2
        self.assertEqual(cfg.value, 2)
        self.assertEqual(cfg.doubled, 4)
        self.assertEqual(cfg.doubled, 4)
        self.assertEqual(calls["doubled"], 1)

        cfg.value = 3
        self.assertEqual(cfg.doubled, 6)
        self.assertEqual(calls["doubled"], 2)

        Config.value.invalidate(cfg)
        self.assertEqual(cfg.doubled, 6)
        self.assertEqual(calls["doubled"], 3)

    def test_input_set_on_inmutable(self):
        class Token(Inmutable):
            name: str

            @flux.input
            def version(self) -> int:
                raise NotImplementedError

        token = Token("alpha")
        Token.version.set(token, 1)
        self.assertEqual(token.version, 1)


class FluxContextVarTest(unittest.TestCase):
    def test_contextvar_read_is_tracked(self):
        calls = {"value": 0}
        current = flux.contextvar("test.current", default=2)

        @flux.functions
        def doubled() -> int:
            calls["value"] += 1
            return cast(int, current.get()) * 2

        self.assertEqual(doubled(), 4)
        self.assertEqual(doubled(), 4)
        self.assertEqual(calls["value"], 1)

        token = current.set(3)
        try:
            self.assertEqual(doubled(), 6)
            self.assertEqual(calls["value"], 2)
        finally:
            current.reset(token)

        self.assertEqual(doubled(), 4)
        self.assertEqual(calls["value"], 3)

    def test_contextvar_set_inside_query_raises(self):
        current = flux.contextvar("test.reentrant", default=1)

        @flux.functions
        def bad() -> int:
            current.set(2)
            return 0

        with self.assertRaises(RuntimeError):
            bad()


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
        cast(flux.Query, Node.base).invalidate(node)
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

        @flux.functions
        def add(a: int, b: int) -> int:
            calls["add"] += 1
            return a + b

        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(calls["add"], 1)
        add.invalidate(None, 2, 3)
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(calls["add"], 2)


class FluxUnsupportedReturnTest(unittest.TestCase):
    def test_property_generator_function_raises(self):
        class Box:
            __slots__ = ("__weakref__",)

            @flux.property
            def values(self):
                yield 1

        box = Box()
        with self.assertRaises(TypeError):
            _ = box.values

    def test_property_generator_object_raises(self):
        class Box:
            __slots__ = ("__weakref__",)

            @flux.property
            def values(self):
                return (value for value in range(3))

        box = Box()
        with self.assertRaises(TypeError):
            _ = box.values

    def test_property_async_function_raises(self):
        class Box:
            __slots__ = ("__weakref__",)

            @flux.property
            async def value(self) -> int:
                return 1

        box = Box()
        with self.assertRaises(TypeError):
            _ = box.value

    def test_function_coroutine_object_raises(self):
        @flux.functions
        def compute() -> object:
            async def inner() -> int:
                return 1

            return cast(object, inner())

        with self.assertRaises(TypeError):
            compute()


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


class FluxKwargsTest(unittest.TestCase):
    def test_kwargs_order_cache(self):
        calls = {"sum": 0}

        class Counter:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def add(self, *, a: int, b: int) -> int:
                calls["sum"] += 1
                return self.value + a + b

        counter = Counter(1)
        self.assertEqual(counter.add(a=1, b=2), 4)
        self.assertEqual(counter.add(b=2, a=1), 4)
        self.assertEqual(calls["sum"], 1)


class FluxEmitCollectTest(unittest.TestCase):
    def test_emit_and_collect(self):
        class Node:
            __slots__ = ("value", "child", "__weakref__")

            def __init__(self, value: int, child: "Node | None" = None) -> None:
                self.value = value
                self.child = child

            @flux.method
            def visit(self) -> int:
                flux.emit(self.value)
                if self.child is not None:
                    return self.child.visit()
                return self.value

        leaf = Node(1)
        root = Node(2, child=leaf)
        _ = root.visit()

        collected = cast(flux.Query, Node.visit).collect(obj=root)
        self.assertEqual(collected, frozenset({1, 2}))

        direct = cast(flux.Query, Node.visit).collect(obj=root, transitive=False)
        self.assertEqual(direct, frozenset({2}))

    def test_emit_outside_query_raises(self):
        flux._runtime._current_key.set(None)
        flux._runtime._current_emits.set(None)
        with self.assertRaises(RuntimeError):
            flux.emit("x")

    def test_collect_requires_query(self):
        with self.assertRaises(TypeError):
            flux.collect(cast(flux.Query, object()))


class FluxMiscTest(unittest.TestCase):
    def test_unhashable_args_raise(self):
        @flux.functions
        def total(values: list[int]) -> int:
            return sum(values)

        with self.assertRaises(TypeError):
            total([1, 2, 3])

    def test_collect_all(self):
        class Box:
            __slots__ = ("value", "__weakref__")

            def __init__(self, value: int) -> None:
                self.value = value

            @flux.method
            def emit_value(self) -> int:
                flux.emit(self.value)
                return self.value

        first = Box(1)
        second = Box(2)
        first.emit_value()
        second.emit_value()
        collected = flux.collect_all(cast(flux.Query, Box.emit_value))
        self.assertEqual(collected, frozenset({1, 2}))


class FluxIterTest(unittest.TestCase):
    def test_iter_linear(self):
        class Node:
            __slots__ = ("value", "next")

            def __init__(self, value: int, next: "Node | None" = None) -> None:
                self.value = value
                self.next = next

        head = Node(1, Node(2, Node(3)))
        def next_node(node: "Node") -> "Node | None":
            return node.next

        next_fn = cast(Callable[[object], object | None], next_node)
        values = [cast(Node, node).value for node in flux.iter(head, next=next_fn)]
        self.assertEqual(values, [1, 2, 3])

    def test_iter_children(self):
        class Node:
            __slots__ = ("value", "children")

            def __init__(self, value: int, children: list["Node"] | None = None) -> None:
                self.value = value
                self.children = children or []

        shared = Node(3)
        root = Node(1, [Node(2, [shared]), shared])
        def child_nodes(node: "Node") -> list["Node"]:
            return node.children

        children_fn = cast(Callable[[object], object], child_nodes)
        values = [cast(Node, node).value for node in flux.iter(root, children=children_fn)]
        self.assertEqual(set(values), {1, 2, 3})
