"""
Taxonomia de las entidades

Las entidades son los nodos semanticos que representan el contexto
de un AST. El contexto puede recibir parametros

Las entidades en funcion de sus parametros de contexto (where):
    - no recibir parametros de contexto (generando un contexto de primer orden)
    - recibir parametros de contexto (generando contextos derivados)
    - recibir varias disposiciones de parametros de contexto (sobrecargando los conetxtos derivados)

    | where | takes | returns | nombre segun el tipo de contexto interno
    --------------------------------------------------------------------
    | no    | no    | no      | namespace (mod)
    | no    | yes   | no      | dataclass (def)
    | no    | no    | yes     | injector or getter (fn)
    | no    | yes   | yes     | function (fn)
    | yes   | no    | no      | parameterized namespace or trait (trait/interface/unit)
    | yes   | yes   | no      | parameterized dataclass (def)
    | yes   | no    | yes     | parameterized injector (default injector)
    | yes   | yes   | yes     | generic function


Step 1: collect ast nodes for entity scoping:
    - namespace (first order)
    - unit (second order)
    - getter
    - overload
    
Step 2: merge ast nodes into a single entity.
    projects the information from higer order entity scopes to lower order scopes.
    Solo los nodos namespace y unit

Step 3: generate the entity


fn self.drop(..)
takes:
    val self: Self
    val sin: Number


"""

from __future__ import annotations
from functools import singledispatch
from typing import Optional, Self
from protobase import Record, frozendict
from axis import syn, Id, ref

class EntityMixin(Record, frozen=True):
    ...


class Morph(Record, frozen=True):
    ast: syn.Item

    class WithWhere:
        ast: syn.Item

    class OptionalWhere:
        ast: syn.Item

    class WithTakes:
        ast: syn.Item

    class WithReturns:
        ast: syn.Item

    class OptionalReturns:
        ast: syn.Item


class Namespace(Morph):
    """
    entity1.entity2 -> namespace lookup
    """

    class CapabilityMixin(EntityMixin):
        namespace: frozendict[str, EntityScoping]

        def get(self, name: str):
            return self.namespace.entries.get(name)

    entries: frozendict[str, Scoping]


class Trait(Morph.WithWhere, Morph):
    """
    Entity[Number]
    """

    class CapabilityMixin(EntityMixin):
        traits: tuple[Trait, ...]

        def __getitem__(self):
            ...

    hiperparams: tuple[syn.Val]


class Getter(Morph.OptionalWhere, Morph.WithReturns, Morph):
    """
    var alpha = Entity
    """
    class CapabilityMixin(EntityMixin):
        traits: tuple[Trait, ...]




class Overload(
    Morph.WithTakes, 
    Morph.OptionalWhere, 
    Morph.OptionalReturns,
    Morph
):
    """
    Entity(a = 1, b = 2)

    si una sobrecarga tiene return su construccion completa dara
    un Entity. Si no tiene return, su construccion completa
    dara un objeto.

    La construccion Partial[entity](1, 2) arrojará una 
    construccion parcial de Entity cuando la construccion
    se complete si el overload tiene return el resultado

    el scope interno de las funciones (returns) es generado
    posteriormente por el compilador, al procesar el suite.

    las funciones sin suite son expected. Futuros codebases
        pueden aportar su implementacion.

    La sobrecarga tambien se utiliza para implementar enums (rust). 

    def Opt
    takes Some(n)
        val name: T
    returns T
    where
        val T: Type

    takes None
    returns Result::Error

    el polimorfismo ocurre entre la composicion del argumento 
    y la ejecucion de la funcion (curante el currying)

    Ejecutar un option sera hacer unwrap. 
    acceder al valor resultado MUTA el valor curried.
    el drop del curried puede optar entre descartar
    la ejecucion o ejecutar y dropear el resultado.
    en el caso de option se descarta, en el caso de result
    se ejecuta (lanzando la excepcion en caso de error)

    apply y drop seran ejecutados de forma transparente (e inteligente)

    """

    class CapabilityMixin(EntityMixin):
        overloads: tuple[Trait, ...]

    parameters: tuple[syn.Val]

"""
Las capabilities de las entidades son abstracciones que deben
ser pautadas con implementaciones concretas para
abordar un buen comportamiento del lenguaje.
"""

type Namespace = frozendict[str, EntityScoping]

class EntityScoping(
    Namespace.CapabilityMixin, 
    Trait.CapabilityMixin, 
    Getter.CapabilityMixin,
    Overload.CapabilityMixin,
    EntityMixin
):
    """
    Representa una entidad semantica.
    """
    namespace: Namespace
    
