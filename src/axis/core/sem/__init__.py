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


from .scoping import *
#from .abstract import *
#from .entities import *