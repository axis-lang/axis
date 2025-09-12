#%%
from collections import defaultdict

def topologic(graph):
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
    
    # Inicializa el diccionario de grados de entrada (indegree)
    indegree = {}
    # Diccionario inverso: a cada nodo, se le asocia el conjunto de nodos que dependen de él.
    rev = defaultdict(set)
    
    # Inicializa los grados de entrada para todos los nodos y construye el grafo inverso.
    for node, deps in graph.items():
        # Aseguramos que el nodo esté en el diccionario (si no, se inicializa con 0)
        if node not in indegree:
            indegree[node] = 0
        # Procesamos cada dependencia del nodo
        for dep in deps:
            # Aseguramos que la dependencia también esté en el diccionario
            if dep not in indegree:
                indegree[dep] = 0
            # Como 'node' depende de 'dep', se incrementa el grado de entrada de 'node'
            indegree[node] += 1
            # Registramos que 'node' depende de 'dep'
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

# Ejemplo de uso:
if __name__ == "__main__":
    # Definición de un DAG de ejemplo.
    # Cada nodo tiene un conjunto de dependencias.
    grafo = {
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
    except ValueError as e:
        print(e)
