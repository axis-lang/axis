from protobase import Inmutable


class Leaf(Inmutable):
    value: int


class Pair(Inmutable):
    left: Leaf
    right: Leaf


def main() -> None:
    a = Leaf(1)
    b = Leaf(1)
    pair1 = Pair(a, a)
    pair2 = Pair(a, b)

    print("a == b:", a == b)
    print("a is b:", a is b)
    print("hash(a) == hash(b):", hash(a) == hash(b))
    print("pair1:", pair1)
    print("pair2:", pair2)
    print("pair1 == pair2:", pair1 == pair2)
    print("pair1.left is pair1.right:", pair1.left is pair1.right)
    print("pair2.left is pair2.right:", pair2.left is pair2.right)


if __name__ == "__main__":
    main()
