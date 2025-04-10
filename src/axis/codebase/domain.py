from .ast import ASTLayer

from axis.std.core import Id, Class


class DomainLayer(ASTLayer, abstract=True):
    """ 
    domain layer implementa metodos realtivos al dominio (data model)
    """

    def dom_index(self):
        ...

    def dom_class(self, entity_id: Id) -> Class:
        'Retorna Class de una entidad'
        pass

