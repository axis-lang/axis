import unittest
from typing import cast

from protobase import flux


class FluxStressTest(unittest.TestCase):
    def test_large_chain(self) -> None:
        class Node:
            __slots__ = ("value", "next", "__weakref__")

            def __init__(self, value: int, next: "Node | None" = None) -> None:
                self.value = value
                self.next = next

            @flux.method
            def total(self) -> int:
                if self.next is None:
                    return self.value
                return self.value + self.next.total()

        length = 200
        head = None
        for i in range(length):
            head = Node(i, head)

        self.assertIsNotNone(head)
        head = cast(Node, head)
        expected = sum(range(length))
        self.assertEqual(head.total(), expected)
        self.assertEqual(head.total(), expected)
