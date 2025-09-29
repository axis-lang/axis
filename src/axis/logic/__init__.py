'''
val zero: Numeric = 0
val additive_identity: Numeric = 0
val multiplicative_identity: Numeric = 1

def Optional T
where:
    val T: Type
takes Some:
    val x: T
takes None
returns T

use Optional(..)
val None: Optional[T] = Optional[T].None
val Some: Fn[T] Optional T = Optional[T].Some

def Range T
where T:
    val T: Numeric
takes:
    val start: T = zero
    val stop: T
    val step: T = additive_identity
returns T




def List[..]
where: 
    val length: Optional Natural = None



def Array[..shape]:
where: 
    val shape: List[length=dims] Natural
    val dims: Optional Natural

'''