"""
Muchas de las estructuras de axis.src están diseñadas conforme la especificación LSP: 
https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#basicJsonStructures
Esto es para facilitar la integración con herramientas que ya implementan esta especificación, como editores de código, linters, etc.
"""
from .file import *
#from .outline import *
from .span import *
from .dir import *
from .fs import *
