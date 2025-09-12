#%%
from __future__ import annotations
from functools import cached_property, wraps, update_wrapper
from typing import Any, Callable, ClassVar
from protobase import Object, Record, Context
from contextvars import ContextVar


"""
el sistema tiene dos contadores globales de revision, commit y stash..
las inferencias anteriores a la revision commit son descartadas (liberando memoria)
las inferencias entre commit y stash son guardadas en un log de cambios (para undo)

el sistema tiene inputs e input sources.. los input sources son funciones puras que retornan
conjuntos de inputs (tuplas o frozensets) y son rastreadas por el sistema.
todo el sistema responde a esos input sources, recomputando las inferencias que dependen de ellos.

un input puede ser: agregado, actualizado o eliminado.

los inputs pueden actuar en cascada, por ejemplo, inputs pueden ser referencias a archivos (sus paths)
y otro input source una funcion que lee esos archivos y retorna su contenido como input.
el contenido puede ser actualizado.

"""

class FluxCycle(Exception):
    pass


class FluxQuery(Record, Context, frozen=True, hub=True):
    "Query Object"

    func: Callable
    args: tuple[Any, ...]
    kwargs_tuple: tuple[tuple[str, Any], ...]

    @property
    def kwargs(self):
        return dict(self.kwargs_tuple)

    @classmethod
    def from_tracked_call(cls, tracked_fn, args, kwargs):
        return cls(tracked_fn, args, tuple(sorted(kwargs.items())))

    def __enter__(self):
        if self.is_context_activated:
            raise FluxCycle("Cycle detected")

        return super().__enter__() # activate self context
    
    def __call__(self):
        graph = FluxGraph.context
        outer_query = type(self).context
        print(self)

        if entry := graph.entries.get(self, None):
            pass
        else:
            with self:
                entry = FluxGraph.Entry(value=self.func(*self.args, **self.kwargs))
                graph.entries[self] = entry

        if outer_query:
            entry.dependants.add(outer_query)
        return entry.value



class FluxGraph(Context, hub=True):
    "Tracks the flux of a environment (DB)"

    class Entry(Object):
        value: Any
        dependants: set[FluxQuery] = set()


    __hash__ = object.__hash__
    __eq__ = object.__eq__

    entries: dict[FluxQuery, Entry] = {}

    def propagate_invalidation(self, *keys: FluxQuery):
        invalidations = list(keys)
        for invalidation in invalidations:
            if entry := self.entries.pop(invalidation, None):
                invalidations.extend(entry.dependants)
                    
        return invalidations


class FluxTracked[*P, R](Record, frozen=True):
    __slots__ = ("__doc__",)

    fn: Callable[[*P], R]

    def __call__(self, *args, **kwargs):
        return FluxQuery.from_tracked_call(self.fn, args, kwargs)()

    # access to the accumulator..

def tracked(*args, **kwargs):
    def tracked_decorator(fn):
        # @wraps(fn)
        # def wrapper(*args, **kwargs):
        #     return FluxQuery.from_tracked_call(fn, args, kwargs)()
        # return wrapper
        return FluxTracked(fn)
    return tracked_decorator



if __name__ == "__main__":

    @tracked()
    def tracked_sum(a, b):
        return a + b
    

    graph = FluxGraph()

    with graph:
        res = tracked_sum(1, 2)

    print(res)
    