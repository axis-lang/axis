grammar Axis;
/*
implementemos una gramatica hibrida entre kotlin y rust para parsear el body de funciones

```axis
# terminals
val term0 = x; # by identifier
val term1 = 1; # by literal
val term2 = 'string'; # by string

# tuples
val unnamed_tuple = (1,2,3, ..)
val named_tuple: (a:Real,b: Real,c: Real) = unnamed_tuple
val shuffled_tuple: (c:Real, b:Real, a:Real) = (..named_tuple) # tuple spreading
val (a,b,p:z) = (1,2,z:3)

# airthmetics
val expr = 1 / { {1 + 2} * 3 + 4 * term1 } # brackets are used as parenthesis in other grammars

# functions
val func = f(1,2,keyword:3)

# indexing
val index = a[1,2,3]
val index = a[.., 2, _] # like python (_ as placeholder)

# composition
val v = beta Array[4,4] gammma(x:1, y:2) # la yuxtaposicion se evalua de derecha a izquierda,
val x = Real { a * b + c }

# statements as trailing lambdas
val v = if (a > b) {a} else {b}

```

*/

file: statement* EOF;

// Statements
statement
    : valStatement
    ;

valStatement
    : 'val' (pattern) (':' expression)? ('=' expression)? ';'?
    ;

pattern
    : identifier
    | tuplePattern
    ;

// Tuple pattern for destructuring
tuplePattern
    : '(' (tuplePatternElement (',' tuplePatternElement)*)? ')'
    ;

tuplePatternElement
    : identifier
    | identifier ':' identifier
    ;



// Expression hierarchy (precedence low to high)
expression
    : juxtapositionExpr
    ;

// Juxtaposition (right-to-left evaluation)
juxtapositionExpr
    : logicalExpr (logicalExpr)*
    ;

// Logical operators
logicalExpr
    : comparisonExpr ((AND | OR) comparisonExpr)*
    ;

// Comparison operators
comparisonExpr
    : addition ((EQ | NE | LT | LE | GT | GE) addition)*
    ;

// Additive operators
addition
    : product ((ADD | SUB) product)*
    ;

// Multiplicative operators
product
    : postfix ((MUL | DIV | MOD) postfix)*
    ;

// Postfix operations
postfix
    : primaryExpr                                               # Pass
    | postfix lambda                                             # TrailingCall
    | postfix tuple                                             # Call
    | postfix '[' (expression (',' expression)*)? ']'           # Indexing
    | postfix ('.' identifier)+                                 # MemberAccess
    ;

// Primary expressions
primaryExpr
    : identifier          // Variables
    | literal             // Numbers
    | tuple           // Tuples
    | lambda         // Bracket expressions
    //| ifExpr              // If expressions
    //| wildcard            // Wildcard
    //| spread              // Spreading
    //| range               // range
    ;

wildcard: '_';
spread: '..';
range: '..' expression;

// Tuple expressions
tuple
    : '(' (tupleElement (',' tupleElement)*)? ','? ')'
    ;

tupleElement
    : expression                            # UnnamedTupleElement
    | ID '=' expression                     # NamedTupleElement
    | '{' expression '}' '=' expression     # DynamicTupleElement
    | '..' expression                       # SpreadTupleElement
    ;

// Bracket expressions (used as parentheses in other languages or trailing lambdas)
lambda
    : '{' lambdaParams? '->' statement* expression? '}'    # LambdaSuite
    | '{' statement* expression? semicolon? '}'            # BasicSuite
    ;

semicolon: ';';

lambdaParams
    : lambdaParam (',' lambdaParam)* ','?
    ;

lambdaParam
    : identifier (':' expression)?
    ;

// Function arguments
argument
    : expression                    // Positional argument
    | identifier ':' expression     // Named argument
    ;




// If expressions
// ifExpr
//     : 'if' '(' expression ')' expression ('else' expression)?
//     ;


// Lexer Rules
identifier: ID;

literal
    : decimal
    | text
    ;

text: TEXT;
decimal: DECIMAL;

ID: [a-zA-Z_][a-zA-Z0-9_]*;
DECIMAL: [0-9]+ ('.' [0-9]+)?;
TEXT: '\'' ( ~'\'' | '\\' . )* '\'';
ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
MOD: '%';
EQ: '==';
NE: '!=';
LT: '<';
LE: '<=';
GT: '>';
GE: '>=';
AND: '&&';
OR: '||';
ARROW: '->';

WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;
