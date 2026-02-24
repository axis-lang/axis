import unittest
from typing import Literal

from protobase.dispatch import litdispatch, valuedispatch


class ValueDispatchTest(unittest.TestCase):
    def test_dispatch_by_value(self) -> None:
        @valuedispatch
        def process(command: str) -> str:
            return "default"

        @process.register("start")
        def _start(command: str) -> str:
            return "start"

        self.assertEqual(process("start"), "start")
        self.assertEqual(process("stop"), "default")

    def test_dispatch_no_args(self) -> None:
        calls = {"count": 0}

        @valuedispatch
        def ping() -> str:
            calls["count"] += 1
            return "pong"

        self.assertEqual(ping(), "pong")
        self.assertEqual(calls["count"], 1)


class LitDispatchTest(unittest.TestCase):
    def test_dispatch_literal(self) -> None:
        @litdispatch
        def greet(name: str) -> str:
            return f"hi {name}"

        @greet.register
        def greet_alice(name: Literal["Alice"]) -> str:
            return "welcome"

        self.assertEqual(greet("Alice"), "welcome")
        self.assertEqual(greet("Bob"), "hi Bob")

    def test_register_requires_literal(self) -> None:
        @litdispatch
        def base(name: str) -> str:
            return "base"

        with self.assertRaises(ValueError):
            @base.register
            def bad(name: int) -> str:
                return "bad"

    def test_function_requires_parameter(self) -> None:
        with self.assertRaises(ValueError):

            @litdispatch
            def no_args() -> str:
                return "x"
