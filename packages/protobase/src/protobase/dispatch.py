#%%
from functools import update_wrapper
from logging import warning
from typing import Any, Callable, Dict, get_type_hints, Literal, get_origin, get_args
import inspect
from warnings import warn

def valuedispatch(func):
    """
    Single-dispatch generic function decorator that dispatches based on the value
    of the first argument.
    
    This provides functionality similar to functools.singledispatch but uses
    the value of the first argument instead of its type.
    
    Example usage:
    
    @valuedispatch
    def process_command(command, *args):
        return f"Unknown command: {command}"
        
    @process_command.register("help")
    def _help_command(command, *args):
        return "Available commands: help, version, exit"
        
    @process_command.register("version")
    def _version_command(command, *args):
        return "Version 1.0"
    """
    registry = {}
    
    def dispatch(value):
        """Return the function implementation for the given value."""
        return registry.get(value, func)
    
    def register(value, func=None):
        """Register a new implementation for the given value."""
        if func is None:
            return lambda f: register(value, f)
        
        registry[value] = func
        update_wrapper(func, dispatch_wrapper)
        return func
    
    def dispatch_wrapper(*args, **kw):
        if not args:
            return func(*args, **kw)
        return dispatch(args[0])(*args, **kw)
    
    dispatch_wrapper.register = register
    update_wrapper(dispatch_wrapper, func)
    return dispatch_wrapper

def takefirst(x, *_):
    return next(iter(x), *_)


def litdispatch(func):
    """
    Single-dispatch generic function decorator that dispatches based on the value
    of the first argument, which must match a typing.Literal annotation in registered functions.
    
    Example usage:
    
    @litdispatch
    def say_hi(name: str):
        return f"Hello {name}!"
        
    @say_hi.register
    def say_hi_alice(name: Literal['Alice']):
        return f"Welcome to wonderland, Alice!"
    """
    registry = {}
    
    # Get the original function's signature
    signature = inspect.signature(func)
    params = list(signature.parameters.keys())
    
    if not params:
        raise ValueError("Function must have at least one parameter")
        
    first_param = params[0]
    
    def dispatch(value):
        """Return the function implementation that matches the literal value."""
        return registry.get(value, func)
    
    def register(impl):
        """Register a new implementation with a Literal type annotation for the first parameter."""
        impl_hints = get_type_hints(impl)
        
        # if first_param not in impl_hints:
        #     raise ValueError(f"Registered function must have parameter '{first_param}'")
            
        param_name, param_type = takefirst(impl_hints.items())
        if param_name != first_param:
            warning(
                f"Registered function parameter '{param_name}' does not match the first parameter '{first_param}'"
            )

        origin = get_origin(param_type)
        
        if origin is not Literal:
            raise ValueError(f"Parameter '{first_param}' must be annotated with Literal type")
            
        literal_values = get_args(param_type)
        for value in literal_values:
            registry[value] = impl
        
        update_wrapper(impl, dispatch_wrapper)
        return impl
    
    def dispatch_wrapper(*args, **kw):
        if not args:
            return func(*args, **kw)
        return dispatch(args[0])(*args, **kw)
    
    dispatch_wrapper.register = register
    update_wrapper(dispatch_wrapper, func)
    return dispatch_wrapper


# Example usage - replace the commented example

if __name__ == '__main__':
    @litdispatch
    def say_hi(name: str):
        return f"Hello {name}!"

    @say_hi.register
    def say_hi_alice(name: Literal['Alice']):
        return f"Welcome to wonderland, Alice!"

    print(say_hi("Bob"))      # Output: Hello Bob!
    print(say_hi("Alice"))    # Output: Welcome to wonderland, Alice!
