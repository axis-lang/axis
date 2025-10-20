"""
Deberiamos poder construir el seedcore prescindiendo de array


Cohercionar a un array de N dimensiones aplanará N-1 dimensiones:

necesitamos verbos logicos para aplanar si es aplanable


Array[2] (1,0)

Array[_, _] ((1,0), (0,1))
se representa internamente como 
Array[2, 2] (1,0,0,1)

Array[..-1] # coherciona todas las dimensiones menos la ultima

"""