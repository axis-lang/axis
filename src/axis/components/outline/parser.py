# %%
"""
Outline File System 

sirve como base de parseo del sistema de ficheros y la estructura general de los ficheros de un proyecto

outline define keyworkds para marcar la funcionalidad de los bloques de texto y los archivos

cada elemento que outline parsea es un bloque de texto que tiene un keyword y un contenido

los elementos de outlilne pueden estar anidados, 

outline permite la construccion incremental de un arbol de entidades

cada entidad en outline tiene un identificador unico como si de un sistema de ficheros se tratara



FUSE Path syntax:
/mod:lambda/fn:sin

los keywords:

postprocesado de bloques:
 forzar la identacion dentro de los bloques
 arbol de entidades

Directivas:
las directivas de outline permiten a outline parsear el arbol de entidades
una directiva puede estar presente en un bloque de texto o en un archivo o un directorio

una directiva establece como debe de preprocesarse y postprocesarse el contenido 
de una entidad.

El arbol de entidades actua como un EntityModel (DOM) sobre el que se pueden hacer consultas
y transformaciones que derivaran en otras representaciones de los datos (AST, IR, etc)

SourceEntity 
modelo de entidades fuente

"""


class Directive:
    as_directory: bool
    as_file: bool
    as_block: bool

    directory_keyword: str
    file_keyword: str
    block_keyword: str


from protobase import Obj, traits
from typing import Generator


class Location(Obj, *traits.Common):
    line: int
    column: int


class LocationRange(Obj, *traits.Common):
    start: Location
    end: Location


class Block(Obj, *traits.Common):
    keyword: str
    content: list[str]
    location_range: LocationRange


class OutlineParser:
    def __init__(
        self,
        keywords: list[str],
        head="mod",
    ):
        self.keywords = keywords
        self.head = head

    def parse_outline_blocks(self, text: str) -> Generator[Block, None, None]:
        """
        Generator function that returns a list of Blocks

        Args:
            text (str): Text to parse

        Returns:
            Generator[Block, None, None]: Generator of Blocks
        """

        lines = text.splitlines()

        block_keyword = self.head
        block_content = []
        block_start_location = Location(line=0, column=0)
        for n, line in enumerate(lines):
            si = line.find(" ")

            if si == -1:
                block_content.append(line)
                continue

            keyword = line[:si]

            if keyword in self.keywords:
                if block_content:
                    block_end_location = Location(line=n, column=len(line))
                    yield Block(
                        keyword=block_keyword,
                        content=block_content,
                        location_range=LocationRange(
                            start=block_start_location, end=block_end_location
                        ),
                    )
                block_keyword = keyword
                block_content = [line]
                block_start_location = Location(line=n, column=0)
            else:
                block_content.append(line)


parser = OutlineParser(["fn", "type", "use"])
example = """
use a

fn alpha...
        Esto es la funcion alpha
where
    a = 9

-> Alpha {
    a: int
    b: str
}   
        

fn beta

type My Type {
    
}

"""

list(parser.parse_outline_blocks(example))

# %%
