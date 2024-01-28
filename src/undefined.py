from typing import Callable, Literal


class UndefinedType:
    """
    Represents an undefined value.
    """

    def __new__(cls):
        try:
            return Undefined
        except NameError:
            return super().__new__(cls)

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> Literal["Undefined"]:
        return "Undefined"

    def __init_subclass__(cls) -> None:
        raise TypeError("Type Undefined cannot be subclassed")


Undefined = UndefinedType()


def optional[
    T
](
    value: T | Undefined,
    /,
    default_: T | Undefined = Undefined,
    factory: Callable[[], T] | Undefined = Undefined,
) -> T:
    """
    Returns the value if it is not Undefined. If the value is Undefined,
    it checks if a factory function is provided. If so, it calls the factory
    function and returns its result. If no factory function is provided,
    it returns the default value.

    Args:
        value (T | Undefined): The value to be checked.
        default_ (T | Undefined, optional): The default value to be returned
            if the value is Undefined. Defaults to Undefined.
        factory (Callable[[], T] | Undefined, optional): The factory function
            to be called if the value is Undefined. Defaults to Undefined.

    Returns:
        T: The value, default value, or the result of the factory function.

    Raises:
        AssertionError: If neither default value nor factory function is provided.
    """
    assert (
        default_ is not Undefined or factory is not Undefined
    ), "Must provide either default or factory"
    if value is Undefined:
        if factory is not Undefined:
            return factory()
        elif default_ is not Undefined:
            return default_
