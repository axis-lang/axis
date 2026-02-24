import unittest

from protobase.utils import compile_function, dict_filter, dict_split


class UtilsTest(unittest.TestCase):
    def test_dict_split(self) -> None:
        data = {"a": 1, "b": 2, "c": 3}
        falsy, truthy = dict_split(data, lambda v: v % 2 == 0)
        self.assertEqual(falsy, {"a": 1, "c": 3})
        self.assertEqual(truthy, {"b": 2})

    def test_dict_filter(self) -> None:
        data = {"a": 1, "b": 2}
        self.assertEqual(dict_filter(data, lambda v: v > 1), {"b": 2})

    def test_compile_function_success(self) -> None:
        fn = compile_function(
            "def add(x, y):",
            "    return x + y",
        )
        self.assertEqual(fn(1, 2), 3)
        self.assertIn("def add", fn.__source__)

    def test_compile_function_sets_attrs(self) -> None:
        fn = compile_function(
            "def foo():",
            "    return 1",
            custom=42,
        )
        self.assertEqual(fn.custom, 42)

    def test_compile_function_missing_name(self) -> None:
        with self.assertRaises(ValueError):
            compile_function("x = 1")

    def test_compile_function_syntax_error(self) -> None:
        with self.assertRaises(SyntaxError):
            compile_function("def broken(:", "    pass")
