from protobase.__core import Object

class Graph[K,V](Object):
    type Edge = tuple[K, K]
    _directions: dict[K, dict[K, V]]
    _indirections: dict[K, dict[K, V]]

    def __init__(self):
        self._directions = {}
        self._indirections = {}

    
    def __getitem__(self, edge: Edge) -> V:
        return self._directions[key]


if __name__ == '__main__':
    g = Graph()
    g[1,2] = 3
    assert g[1,2] == 3
    assert g[2,1] == 3
    print("Graph passed")

    Graph[Node, Edge]

    