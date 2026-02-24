import unittest
from typing import Callable, cast

from protobase.type import Type, parent_of


class ModuleTop(metaclass=Type):
    pass


class ModuleOuter(metaclass=Type):
    class Inner(metaclass=Type):
        pass


class TypeBuildTest(unittest.TestCase):
    def test_builder_order(self) -> None:
        calls: list[str] = []

        class Base(metaclass=Type):
            @staticmethod
            def __class_build__(bld: Type.Builder) -> None:
                calls.append(f"base:{bld.name}")

        class Child(Base):
            @staticmethod
            def __class_build__(bld: Type.Builder) -> None:
                calls.append(f"child:{bld.name}")

        filtered = [item for item in calls if item.endswith(":Child")]
        self.assertEqual(filtered, ["base:Child", "child:Child"])

    def test_prebuild_postbuild(self) -> None:
        class Built(metaclass=Type):
            @staticmethod
            def __class_build__(bld: Type.Builder) -> None:
                @bld.prebuild
                def pre() -> None:
                    bld.namespace["prebuilt"] = True

                def post(cls: type) -> None:
                    cls.postbuilt = True

                bld.postbuild(cast(Callable[[Type.Builder], None], post))

        self.assertTrue(getattr(Built, "prebuilt"))
        self.assertTrue(getattr(Built, "postbuilt"))

    def test_unused_class_args(self) -> None:
        with self.assertRaises(ValueError):

            class Bad(metaclass=Type, unused=True):
                pass

    def test_parent_of_top_level(self) -> None:
        self.assertIsNone(parent_of(ModuleTop))

    def test_parent_of_nested(self) -> None:
        self.assertIs(ModuleOuter.Inner.__parent__, ModuleOuter)
