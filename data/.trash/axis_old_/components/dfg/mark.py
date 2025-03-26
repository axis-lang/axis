class MarkRule:
    """
    Regla de marcado

    Se utiliza para marcar nodos en un grafo de flujo de datos
    donde los nodos que cumplan con la estructura de la regla
    seran (carpturados) para realizar una transformacion.


    """

    wild: Leaf  # nodo utilizado como final de la regla (wildcard)

    root: Node  # nodo raiz de la regla
