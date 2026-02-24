import unittest
from contextvars import ContextVar
from typing import Callable, cast
from weakref import WeakKeyDictionary

import protobase.context as context_module
from protobase.context import Context, contextmethod


class ContextTest(unittest.TestCase):
    def test_context_activation(self) -> None:
        class MyContext(Context):
            value: int = 1

            @contextmethod
            def ping(self) -> bool:
                return self.is_current_context

        MyContext.__contextvar__ = ContextVar("test_context:MyContext")
        context_module._CONTEXT_STACK = WeakKeyDictionary()
        ctx = MyContext()
        self.assertFalse(ctx.is_context_activated)
        with ctx as current:
            self.assertIsNone(current)
            self.assertTrue(ctx.is_context_activated)
            self.assertTrue(ctx.is_current_context)
            self.assertIs(MyContext.context, ctx)
        self.assertFalse(ctx.is_context_activated)
        self.assertIsNone(MyContext.context)

        self.assertTrue(cast(Callable[[], bool], ctx.ping)())
        self.assertFalse(ctx.is_context_activated)

    def test_nested_context(self) -> None:
        class MyContext(Context):
            value: int = 1

        MyContext.__contextvar__ = ContextVar("test_context:MyContextNested")
        context_module._CONTEXT_STACK = WeakKeyDictionary()
        ctx = MyContext()
        with ctx:
            self.assertTrue(ctx.is_context_activated)
            with ctx:
                self.assertTrue(ctx.is_context_activated)
            self.assertTrue(ctx.is_context_activated)
        self.assertFalse(ctx.is_context_activated)
