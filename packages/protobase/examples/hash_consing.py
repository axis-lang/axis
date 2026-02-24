from protobase import Consed


class Symbol(Consed):
    name: str


class Pair(Consed):
    left: Symbol
    right: Symbol


def main() -> None:
    s1 = Symbol("x")
    s2 = Symbol("x")
    s3 = Symbol("y")

    print("s1 is s2:", s1 is s2)
    print("s1 == s2:", s1 == s2)
    print("s1 is s3:", s1 is s3)

    p1 = Pair(s1, s3)
    p2 = Pair(Symbol("x"), Symbol("y"))

    print("p1 is p2:", p1 is p2)
    print("p1:", p1)
    print("p2:", p2)


if __name__ == "__main__":
    main()
