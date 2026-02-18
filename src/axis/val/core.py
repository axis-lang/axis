from __future__ import annotations
from protobase import Record
from axis import dom


class Node(Record, frozen=True, abstract=True):
    "Value NODE implementa unificacion y otras operaciones de alto nivel"


class Value(Node, frozen=True, abstract=True):
    """
    Un valor representa un dato que podria ser dinamico o estatico, 
    cualquier cosa que pueda resultar de evaluar una expresion.
    """

    def __get_meta__(self) -> Value:
        raise NotImplementedError()

    def __get_member__(self, name: str) -> Value:
        raise NotImplementedError()

class Const(Value, frozen=True, consed=True, abstract=True):
    """
    Un valor constante representa un dato inmutable y conocido en tiempo de compilacion.
    """
    # dynamic meta & data?

    ...

class Var(Value, frozen=True, consed=True, abstract=True):
    """
    Una variable representa un dato que puede cambiar en tiempo de ejecucion. 
    o ser determinada en tiempo de compilacion.

    en tiempo de compilacion no se conoce su valor exacto, pero si su bound (dominio).
    informacion: location(stack, heap, pointer), allocation, aliasing 
    (relacion con otra variable), mutabilidad, etc.

    tambien los generics son variables! existen variables que pueden transformarse en constants?!
    """
###

class DynConst(Const, frozen=True, consed=True, abstract=True):
    """
    Una estancia constante tipo creado en tiempo de ejecucion.
    """

class BuiltinConst(Const, frozen=True, consed=True, abstract=True):
    """
    Una estancia constante tipo interno del sistema. 
    """

    def __get_member__(self, name: str) -> Value:
        ...


class Ref(BuiltinConst, frozen=True, consed=True, abstract=True):
    """
    Referencia a una entidad conocida en tiempo de compilacion.
    """

class Bound(Node, frozen=True, consed=True, abstract=True):
    """
    constraint de una variable, puede ser un tipo variable.
    """

class Type(BuiltinConst, frozen=True, consed=True):
    """
    def Type[..Qualifiers, Scheme]
    takes:
        val Qualifiers: (..: Qualifier)
        val Scheme: Scheme
    """

    class Scheme(Node, frozen=True, abstract=True):
        ...

    class PolymorphicScheme(Scheme, frozen=True, consed=True):
        ...

    class NominalScheme(Scheme, frozen=True, consed=True):
        ...

    qualifiers: dom.Tuple[str, dom.Meta]
    scheme: Scheme  # tipo de destino estructural o nominal
    # Meta provider


class TypeScheme(Node, frozen=True, consed=True):
    '''
    clase abstracta para tipos: struct class union, literal
    '''


class Struct(TypeScheme, frozen=True, consed=True):
    fields: dom.Tuple[str, Bound]
