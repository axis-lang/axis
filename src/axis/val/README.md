# inferencia estructual

# Generalizacion (isomorfismos)

```axis
(
    a=(x=1,y=0,z=0)
    b=(0,1,0)
    c=(0,0,1)
) : Array[3,3] Natural

val v = (
    t=(0,1,2,3)
    p: Array[_] (x:_, y:_) =(
        (0,0)
        (1,2)
        (2,4)
        (3,8)
    )
)

reshape(v) { x,y,i,p -> y[i].{p} = x.{p}[i]; y }


: Array[4] (t: Natural, p: (x:Natural, y:Natural)) # reshape

```

# method dispatching and pattern matching (mro aplicada a sobrecargas)

la resolucion de metodos se efectua a lo largo de un tuple, elemento a elemento
en la profundidaz de su jerarquia de especializacion (del mas especifico al mas generico)

# currying

def op(a,b,c)

mysum = (a,b).sum

c.mysum




sum(a) -> (a).sum


bound
    monomorphic
        type: T
        dominio
            abierto: todo el dominio
            un solo valor: T -> v
            un conjunto de valores: T -> (..:T)
            un rango de valores (para clases ordenadas): T -> (min: T, max: T)
    polymorphic
        types: T1 | T2
        domain: 
            open
            valores discretos {T1: {v1, v2}, T2: {v3, v4} }
            

T1.{K}: T2[K]

(..; name = 6; ..)





