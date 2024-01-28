import unittest
from pure import Pure, PureMeta


class TestPure(unittest.TestCase):
    class MyPure(Pure):
        x: int
        y: int

    def setUp(self):
        self.pure1 = self.MyPure(1, 2)
        self.pure2 = self.MyPure(1, 2)
        self.pure3 = self.MyPure(3, 4)

    def test_pure_equality(self):
        self.assertEqual(self.pure1, self.pure2)
        self.assertNotEqual(self.pure1, self.pure3)

    def test_pure_identity(self):
        self.assertIs(self.pure1, self.pure2)
        self.assertIsNot(self.pure1, self.pure3)

    def test_pure_hash(self):
        self.assertEqual(hash(self.pure1), hash(self.pure2))
        self.assertNotEqual(hash(self.pure1), hash(self.pure3))

    def test_pure_immutable(self):
        with self.assertRaises(AttributeError):
            self.pure1.x = 5

    def test_metapure(self):
        self.assertIsInstance(self.MyPure, PureMeta)

    def test_metapure_instances(self):
        self.assertIn(self.pure1, self.MyPure.__instances__)
        self.assertIn(self.pure2, self.MyPure.__instances__)
        self.assertIn(self.pure3, self.MyPure.__instances__)


if __name__ == "__main__":
    unittest.main()
