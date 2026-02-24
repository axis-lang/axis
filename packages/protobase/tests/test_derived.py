import unittest
from typing import Callable, cast

from protobase.derived import derived
from protobase.object import Object


class DerivedTest(unittest.TestCase):
    def test_derived_method_installs(self) -> None:
        def impl_hello(cls):
            def hello(self) -> str:
                return f"hello from {cls.__name__}"

            return hello

        class Greeter(Object):
            name: str

            @derived(impl_hello)
            def hello(self) -> str: ...

        greeter = Greeter("x")
        self.assertEqual(greeter.hello(), "hello from Greeter")
        self.assertTrue(callable(Greeter.hello))

    def test_derived_classmethod(self) -> None:
        def impl_name(cls):
            def name(inner_cls) -> str:
                return inner_cls.__name__

            return name

        class Named(Object):
            @derived(impl_name)
            @classmethod
            def name(cls) -> str: ...

        self.assertEqual(Named.name(), "Named")

    def test_derived_missing_impl(self) -> None:
        def impl_none(cls):
            return None

        class Missing(Object):
            @derived(cast(Callable[[type], Callable[..., object]], impl_none))
            def nope(self) -> None: ...

        missing = Missing()
        with self.assertRaises(NotImplementedError):
            _ = missing.nope()
