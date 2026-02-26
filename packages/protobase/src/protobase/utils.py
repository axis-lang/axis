# %%
import re
from typing import Any, Callable, Mapping, Protocol, cast


def dict_split[K, V](
    d: Mapping[K, V],
    fn: Callable[[V], bool],
) -> tuple[dict[K, V], dict[K, V]]:
    result = {}, {}
    for k, v in d.items():
        result[fn(v)][k] = v
    return result


def dict_filter[K, V](d: dict[K, V], fn: Callable[[V], bool]) -> dict[K, V]:
    return {k: v for k, v in d.items() if fn(v)}


FN_NAME_RE = re.compile(r"^def\s(\w+)")


class CompiledFunction(Protocol):
    __source__: str

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

    def __getattr__(self, name: str) -> Any: ...


def compile_function(
    *source,
    locals: dict[str, Any] | None = None,
    globals: dict[str, Any] | None = None,
    **kwargs,
) -> CompiledFunction:
    """
    Compile a function from source code.

    Args:
        name (str): The name of the function.
        source: The source code of the function.
        locals (dict[str, Any] | None, optional): Local variables to be used during execution. Defaults to None.
        globals (dict[str, Any] | None, optional): Global variables to be used during execution. Defaults to None.
        kwargs: Additional keyword arguments to be set as attributes of the compiled function.

    Returns:
        Callable: The compiled function.

    Example:
        >>> fn = compile_function(
        ...     "def foo(x: int, y: int) -> int:",
        ...     "    return x + y",
        ... )
        >>> fn(1, 2)
        3
        >>> fn.__source__
        def foo(x: int, y: int) -> int:\n    return x + y\n    \n    \n

    """
    if locals is None:
        locals = {}

    source = "\n".join(source)

    match = FN_NAME_RE.match(source)
    if match is None:
        raise ValueError("Cannot find function name in source code.")
    fn_name = match.group(1)

    try:
        exec(source, globals, locals)
    except SyntaxError as e:
        raise SyntaxError(f"{e.msg} in source code:\n{source}")

    fn = cast(CompiledFunction, locals[fn_name])
    fn.__source__ = source

    for nm, val in kwargs.items():
        setattr(fn, nm, val)

    return fn
