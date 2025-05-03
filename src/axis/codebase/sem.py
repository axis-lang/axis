"""
cada forma (morph) ast de una entidad contribuye a los aspectos semanticos
de la entidad. estos aspectos se tratan de la siguiente manera:

1. sobrecarga de la llamada a la entidad
2. sobrecarga de rasgo de la entidad
3. namespace plain flatten de la entidad

"""
from protobase import frozendict
from .ast import SyntacticLayer

from axis.dom import sem, ref


class SemanticLayer(SyntacticLayer, abstract=True):
    ''
    # def sem_scoping_of_mod(self, mod_ref: ref.Unit):
    #     # tansolo modifica la disposicion de los datos a group_recursive
    #     return sem.Scoping.for_item(self.ast_of_unit(mod_ref))

