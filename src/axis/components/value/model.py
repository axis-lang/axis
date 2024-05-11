from protobase import Object, traits


# Value, Variable y Constant son siempre traits?


class Value(Object, traits.Basic):
    ...
    # shape
    # tuple
    # type
    # domain for constant = self


class Constant(Value): ...


class Variable(Value): ...


class Type(Constant): ...


class Domain(Constant): ...
