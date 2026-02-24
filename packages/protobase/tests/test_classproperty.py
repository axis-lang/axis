import unittest

from protobase.classproperty import classproperty


class ClassPropertyTest(unittest.TestCase):
    def test_getter(self) -> None:
        class Box:
            _value = 1

            @classproperty
            def value(cls) -> int:
                return cls._value

        self.assertEqual(Box.value, 1)
        self.assertEqual(Box().value, 1)

    def test_setter(self) -> None:
        class Box:
            _value = 1

            @classproperty
            def value(cls) -> int:
                return cls._value

            @value.setter
            def value(cls, v: int) -> None:
                cls._value = v

        box = Box()
        box.value = 3
        self.assertEqual(Box.value, 3)

    def test_setter_missing(self) -> None:
        class Box:
            @classproperty
            def value(cls) -> int:
                return 1

        with self.assertRaises(AttributeError):
            Box().value = 2
