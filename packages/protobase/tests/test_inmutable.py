import unittest
from typing import Any, Literal, TypeVar, cast

from protobase.inmutable import check_inmutable, inmutable, is_inmutable, register_inmutable


class InmutableTest(unittest.TestCase):
    def test_register_inmutable(self) -> None:
        class Custom:
            pass

        self.assertFalse(is_inmutable(Custom))
        register_inmutable(Custom)
        self.assertTrue(is_inmutable(Custom))

    def test_inmutable_decorator(self) -> None:
        @inmutable
        class Tagged:
            pass

        self.assertTrue(is_inmutable(Tagged))

    def test_check_inmutable_union(self) -> None:
        check_inmutable(int | str)
        with self.assertRaises(TypeError):
            check_inmutable(int | list)

    def test_check_inmutable_typevar(self) -> None:
        T = TypeVar("T", int, str)
        check_inmutable(T)

        U = TypeVar("U", bound=list)
        with self.assertRaises(TypeError):
            check_inmutable(U)

    def test_check_inmutable_alias(self) -> None:
        Alias = tuple[int, str]
        check_inmutable(Alias)

    def test_check_inmutable_special_cases(self) -> None:
        check_inmutable("ForwardRef")
        check_inmutable(...)

    def test_check_inmutable_literal(self) -> None:
        check_inmutable(Literal["binding", 1, None, True])

    def test_check_inmutable_literal_rejects_mutable_value(self) -> None:
        literal_factory = Literal
        with self.assertRaises(TypeError):
            check_inmutable(cast(Any, literal_factory).__getitem__((object(),)))
