import unittest

from protobase.metadata import Metadata

class MetadataTest(unittest.TestCase):
    def test_tag_and_of(self) -> None:
        class Target:
            __slots__ = ("__weakref__",)

        class Tag(Metadata[Target]):
            label: str

        obj = Target()
        tag = Tag("alpha")
        tag.tag(obj)
        self.assertIs(Tag.of(obj), tag)

    def test_missing_returns_none(self) -> None:
        class Target:
            __slots__ = ("__weakref__",)

        class Tag(Metadata[Target]):
            label: str

        obj = Target()
        self.assertIsNone(Tag.of(obj))

    def test_hub_inheritance_error(self) -> None:
        class Target:
            __slots__ = ("__weakref__",)

        class Tag(Metadata[Target]):
            label: str

        with self.assertRaises(TypeError):

            class Bad(Tag, hub=True):
                pass
