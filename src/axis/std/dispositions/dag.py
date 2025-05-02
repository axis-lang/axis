from __future__ import annotations
from typing import Iterable
from protobase import Record, frozendict, cached_property

# dict[K, set[V]] es una estructura recurrente. 

class DAG[T](Record, frozen=True):

    @classmethod
    def from_iter(cls, iterable: Iterable[tuple[T, T]]) -> DAG[T]:
        dag = {}
        for a, b in iterable:
            dag.setdefault(a, set()).add(b)
        return cls(_frozen(dag))

    dag: frozendict[T, frozenset[T]]

    def __contains__(self, item: T) -> bool:
        return item in self.dag

    def __getitem__(self, item: T) -> frozenset[T]:
        return self.dag[item]

    @cached_property
    def reversed(self) -> DAG[T]:
        """
        Reverse the DAG
        """
        dag = {}
        for k, v in self.dag.items():
            dag.setdefault(k, set())
            for i in v:
                dag.setdefault(i, set()).add(k)
        return self.__class__(_frozen(dag))

    @cached_property
    def degree(self) -> frozendict[T, int]:
        """
        Degree of each node in the DAG
        """
        return frozendict({k: len(v) for k, v in self.dag.items()})

    @cached_property
    def topology(self) -> list[set[T]]: # modificar resultado
        """
        Topological sort of the DAG
        """
        indegree = self.degree
        rev = self.reversed
        # Inicializa el primer nivel: nodos sin dependencias (grado 0)
        current_level = {node for node, deg in indegree.items() if deg == 0}
        levels = []
        
        # Mientras haya nodos sin dependencias, se procesan en niveles
        while current_level:
            # Se añade el conjunto actual a la lista de niveles
            levels.append(current_level)
            next_level = set()
            # "Elimina" cada nodo del nivel actual, actualizando el grado de entrada de sus dependientes
            for node in current_level:
                for dependent in rev.get(node, []):
                    indegree[dependent] -= 1
                    # Si el dependiente ya no tiene otras dependencias, se podrá procesar en el siguiente nivel
                    if indegree[dependent] == 0:
                        next_level.add(dependent)
            current_level = next_level

        # Si existen nodos que aún tienen grado de entrada positivo, significa que hay ciclos en el grafo.
        if any(deg > 0 for deg in indegree.values()):
            raise ValueError("El grafo contiene ciclos y no es un DAG válido.")
        
        return levels        



def _frozen[T](dag: dict[T, set[T]]) -> frozendict[T, frozenset[T]]:
    return frozendict({k: frozenset(v) for k, v in dag.items()})