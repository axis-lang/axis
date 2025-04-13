from .syn import SyntacticLayer

from axis.std import Id, sem


class SemanticLayer(SyntacticLayer, abstract=True):
    """ 
    Semantic layer for the codebase. This layer is responsible for
    creating the semantic graph from the syntactic layer. 
    """

    @property
    def sem_graph(self):
        for unit in self.fs_units:
            unit_ast = self.ast_of_unit(unit)

            # construye de forma recursiva el arbol de nodos semanticos de la unidad
            # comenzando con el nodo raiz, la unidad misma.

            # todas las unidades y sus nodos son agregaddos al arbol de unidades
           
            # esta funcion debe ser refactorizada pensando en la computacion incremental

        return sem.Graph()
