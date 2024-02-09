"""
This is a head lina
        This is a documentation line
    This is a entry
            Documentation for the entry
        body of the entri
    This is a second entry without doc
        The body for the second entry
    This is a third without doc and body
    This is a fourth entry
            Documentation for the fourth entry

    This is a fifth entry
        only body entry
                body documented here
            other entry
            

the first word in the head line is the keyword.
the keyword can be optional on several 

if a < b:

multiple blocks can be merged together


let alpha = match a
: Nat = x => "a is natural, with value {x}"!
: Real = x =>  "a is real, with value {x}"!


if : Real x = x

fn foo: (a: N, b: N) 
were N
: .. Natural => 
: .. Real =>

when x in 0..200:

    

elif a > 0:
    print("a is positive")
else:
    print("a is negative")


    

fn a_custom_function_name(
        The foo function is a 

    alpha: Natural = 0, 
            This is a documentation line for alpha
    beta: Real = 0.0,
            beta documentation line
    gamma: Real = 0.0,
) -> ReturnType:
        
        This is the documentation block for foo
        All the lines indented a the same level are part of the documentation
        block for foo
    
        
    This is the body of foo
    This is the seond entry in the body of foo

    the Parethesis (
        are ignored by the outline
        outblock
    )

    This is the body of foo


def foo(): {

}



"""


from __future__ import annotations


class Entry:
    head: list[str]
    doc: list[str]
    body: list[Entry]
