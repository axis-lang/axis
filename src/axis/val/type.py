"""
Valores (expresiones) del algebra de tipos.

cuando los valores actuan como tipos algebraicos, se evaluan de la siguiente manera.

una referencia a una entidad engloba a cualquier construccion posible de esa entidad.

un indice a una entidad Entity[..] selecciona total o parcialmente las construcciones de la entidad 
en las que los valores genericos quedan atados:

    Entity[bitlength: 0..32] # atado a dominio
    Entity[bitlength=32] # atado a valor
    Entity[bitlength:0..32=BL] # atado a dominio y asignado a variable

una aplicacion a una entidad indica un tipo de construccion especifico de la entidad,
    Entity(value: str) # la propiedad value esta atada a str
    Entity(name='foo') # la propiedad name esta asignada a 'foo'
    Entity(name: Rex('[a-zA-Z_][a-zA-Z0-9_]*')) # la propiedad name esta atada a una expresion regular

"""