from typing import cast

from protobase import Inmutable, flux


class Expr(Inmutable, abstract=True):
    @flux.property
    def eval(self) -> int:
        raise NotImplementedError

    @flux.property
    def size(self) -> int:
        raise NotImplementedError


class Lit(Expr):
    value: int

    @flux.property
    def eval(self) -> int:
        return self.value

    @flux.property
    def size(self) -> int:
        return 1


class Add(Expr):
    left: Expr
    right: Expr

    @flux.property
    def eval(self) -> int:
        left = cast(int, self.left.eval)
        right = cast(int, self.right.eval)
        return left + right

    @flux.property
    def size(self) -> int:
        left = cast(int, self.left.size)
        right = cast(int, self.right.size)
        return 1 + left + right


def main() -> None:
    expr = Add(Lit(1), Add(Lit(2), Lit(3)))

    print("eval:", expr.eval)
    print("size:", expr.size)
    print("eval (cached):", expr.eval)
    print("stats Add.eval:", Add.eval.stats())
    print("stats Lit.eval:", Lit.eval.stats())


if __name__ == "__main__":
    main()
