#%%
from collections import defaultdict
from typing import Dict, Iterable, Set, List, Tuple, TypeVar, Optional, Any, DefaultDict, Hashable

# Definir tipo genérico para nodos
T = TypeVar('T', bound=Hashable)
# Tipo para representar un grafo: diccionario donde las claves son nodos y valores son conjuntos de dependencias
DAG = Dict[T, Set[T]]
# Tipo para pesos de nodos
Weights = Dict[T, float]


def dag[T: Hashable](gen: Iterable[tuple[T, T]]):
    '''
    build a dag from iterable of relations x → y
    '''
    dag = {}
    for a, b in gen:
        dag.setdefault(a, set()).add(b)
    return dag

def rev[T: Hashable](dag: DAG[T]):
    rev = {}
    for a, b in dag.items():
        rev.setdefault(a, set())
        for c in b:
            rev.setdefault(c, set()).add(a)
    return rev

def degree[T: Hashable](dag: DAG[T]):
    return { k: len(v) for k, v in dag.items() }

def reverse_dag(graph: DAG[T]) -> DAG[T]:
    """
    Invierte las direcciones de todas las aristas de un grafo dirigido.
    
    Parámetros:
        graph (DAG): Grafo representado como un diccionario donde cada nodo tiene un conjunto de dependencias.
        
    Retorna:
        DAG: El grafo invertido donde todas las dependencias se revierten.
    """
    # Inicializar el grafo invertido
    reversed_graph: DAG[T] = {}
    
    # Recolectar todos los nodos primero
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
    
    # Inicializar el grafo invertido con conjuntos vacíos
    for node in all_nodes:
        reversed_graph[node] = set()
    
    # Invertir las dependencias
    for node, deps in graph.items():
        for dep in deps:
            reversed_graph[dep].add(node)
    
    return reversed_graph

def calculate_indegrees(graph: DAG[T]) -> Dict[T, int]:
    """
    Calcula los grados de entrada para todos los nodos del grafo.
    
    Parámetros:
        graph (DAG): Grafo representado como un diccionario.
        
    Retorna:
        Dict[T, int]: Diccionario donde cada clave es un nodo y su valor es su grado de entrada.
    """
    indegree: DefaultDict[T, int] = defaultdict(int)
    
    # Recolectar todos los nodos primero
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
    
    # Inicializar todos los nodos con grado 0
    for node in all_nodes:
        indegree[node] = 0
    
    # Construir el grafo inverso para calcular los grados de entrada correctamente
    for node, deps in graph.items():
        for dep in deps:
            # Si 'node' depende de 'dep', entonces hay una arista desde 'dep' hacia 'node'
            # Por lo tanto, incrementamos el grado de entrada de 'node'
            indegree[node] += 1
    
    return indegree

def topologic(graph: DAG[T]) -> List[Set[T]]:
    """
    Realiza un ordenamiento topológico en niveles de un grafo dirigido acíclico (DAG).
    
    Parámetros:
        graph (dict): Diccionario donde cada clave es un nodo y su valor
                      es un conjunto (o lista) de nodos de los cuales depende.
    
    Retorna:
        List[set]: Lista de conjuntos, donde cada conjunto contiene nodos que 
                   pueden procesarse en paralelo (sin dependencias entre sí).
                   
    Lanza:
        ValueError: Si el grafo contiene ciclos.
    """
    
    # Usar la función auxiliar para calcular los grados de entrada
    indegree = calculate_indegrees(graph)
    
    # Diccionario inverso: a cada nodo, se le asocia el conjunto de nodos que dependen de él.
    rev: DefaultDict[T, Set[T]] = defaultdict(set)
    
    # Construye el grafo inverso.
    for node, deps in graph.items():
        for dep in deps:
            rev[dep].add(node)
    
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

def has_cycle(graph: DAG[T]) -> bool:
    """
    Detecta si un grafo dirigido contiene ciclos.
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario de nodos y sus dependencias.
        
    Retorna:
        bool: True si el grafo contiene ciclos, False en caso contrario.
    """
    try:
        topologic(graph)
        return False
    except ValueError:
        return True

def find_sources(graph: DAG[T]) -> Set[T]:
    """
    Encuentra todos los nodos fuente (sin dependencias) del grafo.
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        
    Retorna:
        set: Conjunto de nodos fuente.
    """
    indegree = calculate_indegrees(graph)
            
    # Los nodos fuente tienen grado de entrada 0
    return {node for node, degree in indegree.items() if degree == 0}

def find_sinks(graph: DAG[T]) -> Set[T]:
    """
    Encuentra todos los nodos sumidero (de los que nadie depende) del grafo.
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        
    Retorna:
        set: Conjunto de nodos sumidero.
    """
    # Construye un conjunto de todos los nodos
    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)
        
    # Identifica qué nodos tienen dependientes
    has_dependents = set()
    for node, deps in graph.items():
        for dep in deps:
            has_dependents.add(dep)
            
    # Los sumideros son los nodos sin dependientes
    sinks = all_nodes - has_dependents
    return sinks

def find_ancestors(graph: DAG[T], target_node: T) -> Set[T]:
    """
    Encuentra todos los ancestros de un nodo específico (nodos de los que depende).
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        target_node: El nodo del cual se buscan los ancestros.
        
    Retorna:
        set: Conjunto de todos los ancestros del nodo objetivo.
    """
    ancestors: Set[T] = set()
    
    def dfs(node: T) -> None:
        # Busca entre las dependencias directas del nodo
        for dep in graph.get(node, set()):
            if dep not in ancestors:
                ancestors.add(dep)
                dfs(dep)
    
    # Comenzar búsqueda desde el nodo objetivo
    dfs(target_node)
    return ancestors

def find_descendants(graph: DAG[T], start_node: T) -> Set[T]:
    """
    Encuentra todos los descendientes de un nodo específico.
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        start_node: El nodo del cual se buscan los descendientes.
        
    Retorna:
        set: Conjunto de todos los descendientes del nodo de inicio.
    """
    # Construir el grafo inverso para facilitar la búsqueda
    rev: DefaultDict[T, Set[T]] = defaultdict(set)
    for node, deps in graph.items():
        for dep in deps:
            rev[dep].add(node)
            
    descendants: Set[T] = set()
    
    def dfs(node: T) -> None:
        for dependent in rev.get(node, set()):
            if dependent not in descendants:
                descendants.add(dependent)
                dfs(dependent)
                
    dfs(start_node)
    return descendants

def find_critical_path(graph: DAG[T], weights: Optional[Weights[T]] = None) -> Tuple[List[T], float]:
    """
    Encuentra el camino crítico en un DAG (el camino más largo).
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        weights (dict, opcional): Diccionario con pesos para cada nodo.
        
    Retorna:
        tuple: (camino, longitud) donde camino es una lista de nodos
               y longitud es la suma de los pesos del camino.
    """
    if weights is None:
        weights = {node: 1 for node in graph.keys()}
        for deps in graph.values():
            for dep in deps:
                if dep not in weights:
                    weights[dep] = 1
    
    # Ordenamiento topológico
    levels = topologic(graph)
    
    # Distancias más largas a cada nodo y predecesores
    distances: Dict[T, float] = {}
    predecessors: Dict[T, Optional[T]] = {}
    
    # Inicializa con nodos fuente
    all_nodes = set()
    for level in levels:
        all_nodes.update(level)
    
    for node in all_nodes:
        distances[node] = 0
        predecessors[node] = None
    
    # Construye el grafo inverso
    rev: DefaultDict[T, Set[T]] = defaultdict(set)
    for node, deps in graph.items():
        for dep in deps:
            rev[dep].add(node)
    
    # Para cada nivel en orden
    for level in levels:
        for node in level:
            weight = weights.get(node, 0)
            for dependent in rev.get(node, set()):
                new_dist = distances[node] + weight
                if new_dist > distances.get(dependent, 0):
                    distances[dependent] = new_dist
                    predecessors[dependent] = node
    
    # Encuentra el nodo con la distancia máxima
    max_dist = -1
    max_node = None
    for node, dist in distances.items():
        if dist > max_dist:
            max_dist = dist
            max_node = node
    
    # Reconstruye el camino
    path = []
    current = max_node
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    return list(reversed(path)), max_dist

def transitive_closure(graph: DAG[T]) -> Dict[T, Set[T]]:
    """
    Calcula el cierre transitivo del grafo (todos los nodos alcanzables desde cada nodo).
    
    Parámetros:
        graph (dict): Grafo representado como un diccionario.
        
    Retorna:
        dict: Diccionario donde cada clave es un nodo y su valor es el conjunto
              de todos los nodos alcanzables desde él.
    """
    closure: Dict[T, Set[T]] = {}
    
    for node in graph:
        # Para cada nodo, realiza un DFS para encontrar todos los nodos alcanzables
        visited: Set[T] = set()
        
        def dfs(current: T) -> None:
            for dep in graph.get(current, set()):
                if dep not in visited:
                    visited.add(dep)
                    dfs(dep)
        
        dfs(node)
        closure[node] = visited
    
    return closure

# Ejemplo de uso:
if __name__ == "__main__":
    # Definición de un DAG de ejemplo.
    # Cada nodo tiene un conjunto de dependencias.
    grafo: DAG[str] = {
        'A': set(),          # 'A' no depende de nada
        'B': {'A'},
        'C': {'A'},
        'D': {'B', 'C', 'A'},
        'E': {'C'},
        'F': {'D', 'E', 'A'}
    }
    
    try:
        niveles = topologic(grafo)
        print("Ordenamiento topológico en niveles:")
        for idx, nivel in enumerate(niveles, start=1):
            print(f"Nivel {idx}: {nivel}")
            
        print("\nFuentes:", find_sources(grafo))
        print("Sumideros:", find_sinks(grafo))
        print("¿Tiene ciclos?:", has_cycle(grafo))
        
        # Añadamos un ciclo para probar
        grafo_con_ciclo = grafo.copy()
        grafo_con_ciclo['A'] = {'F'}
        print("¿El grafo modificado tiene ciclos?:", has_cycle(grafo_con_ciclo))
        
        # Probar algunas otras funciones
        print("\nAncestros de 'F':", find_ancestors(grafo, 'F'))
        print("Descendientes de 'A':", find_descendants(grafo, 'A'))
        
        # Camino crítico con pesos uniformes
        path, length = find_critical_path(grafo)
        print(f"\nCamino crítico: {path}, Longitud: {length}")
        
        # Cierre transitivo parcial
        print("\nCierre transitivo:", transitive_closure(grafo))
        
        # Grafo invertido
        grafo_invertido = reverse_dag(grafo)
        print("\nGrafo invertido:", grafo_invertido)
        
    except ValueError as e:
        print(e)
