from derive import Hash
from trust import Trust


import unittest


class TestTrust(unittest.TestCase):
    class MyType(Trust, Hash):
        ...

    def test_instance(self):
        print("HEY")


if __name__ == "__main__":
    unittest.main()
