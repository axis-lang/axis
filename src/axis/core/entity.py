"""
las entidades son el 'sistema de archivos' de axis
cada entidad es un nodo logico y estructural

mientras que los items son nodos fisicos 
y sus referencias hacen relacion al codigo.

las entidades son los nodos logicos y sus referencias
se relacionan con los tipos y valores de axis.

las entidades son la base para el sistema de tipado
fuerte de axis. 



"""
from typing import Self
from protobase import Record, Object

class Entity(Record, frozen=True):
    '''
    '''

    class Builder(Object):
        '''
        Builder for Entity.
        '''
        def build(self):
            ...

    def member(self, name: str) -> Self:
        '''
        Get a member by name.
        '''

    

    def __getitem__(self, shape):
        '''
        '''
        
    def __call__(self, *args, **kwargs):
        '''
        '''

