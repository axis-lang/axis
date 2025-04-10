grammar Axis;
/*

```axis
# terminals
val term0 = x; # by identifier
val term1 = 1; # by literal
val term2 = 'string'; # by string

# tuples
val unnamed_tuple = (1,2,3)
val named_tuple: (a:Real,b: Real,c: Real) = unnamed_tuple
val shuffled_tuple: (c:Real, b:Real, a:Real) = (..named_tuple) # tuple spreading
val mixed_tuple = (1,2,z:3)

# airthmetics
val expr = 1 / { {1 + 2} * 3 + 4 * term1 }

# functions
val func = f(1,2,keyword:3)

# indexing
val index = a[1,2,3]

# composition
val v = beta Array[4,4] gammma(x:1, y:2)

```

*/

program
    : statement*
    ;

// Statements
statement
    : valDeclaration
    | expressionStatement
    ;

valDeclaration
    : 'val' IDENTIFIER (':' expression)? ('=' expression)? ';'?
    ;

expressionStatement
    : expression ';'?
    ;

// Expressions
expression
    : compositionExpression
    | assignmentExpression
    ;

assignmentExpression
    : conditionalExpression ('=' expression)?
    ;

// Composición por yuxtaposición (evaluada de derecha a izquierda)
compositionExpression
    : functionExpression (('(..)') functionExpression)*
    ;

functionExpression
    : primaryExpression functionCallSuffix? trailingLambda?
    | conditionalExpression
    ;

conditionalExpression
    : orExpression
    | ifExpression
    ;

ifExpression
    : 'if' '(' expression ')' blockExpression ('else' (ifExpression | blockExpression))?
    ;

orExpression
    : andExpression ('||' andExpression)*
    ;

andExpression
    : equalityExpression ('&&' equalityExpression)*
    ;

equalityExpression
    : comparisonExpression (('==' | '!=') comparisonExpression)*
    ;

comparisonExpression
    : additiveExpression (('<' | '>' | '<=' | '>=') additiveExpression)*
    ;

additiveExpression
    : multiplicativeExpression (('+' | '-') multiplicativeExpression)*
    ;

multiplicativeExpression
    : unaryExpression (('*' | '/' | '%') unaryExpression)*
    ;

unaryExpression
    : ('+' | '-' | '!') unaryExpression
    | primaryExpression
    ;

primaryExpression
    : literal
    | IDENTIFIER
    | tupleExpression
    | blockExpression
    | '(' expression ')'
    ;

blockExpression
    : '{' statement* (expression)? '}'
    ;

literal
    : INTEGER_LITERAL
    | FLOAT_LITERAL
    | STRING_LITERAL
    | BOOLEAN_LITERAL
    ;

tupleExpression
    : '(' tupleElements? ')'
    ;

tupleElements
    : tupleElement (',' tupleElement)* ','?
    ;

tupleElement
    : (IDENTIFIER ':')? expression
    | '..' expression  // Tuple spreading
    ;

functionCallSuffix
    : '(' functionArguments? ')'
    ;

functionArguments
    : functionArgument (',' functionArgument)* ','?
    ;

functionArgument
    : (IDENTIFIER ':')? expression
    ;

trailingLambda
    : '{' lambdaParameters? ('->' (statement* expression? | expression))? '}'
    ;

lambdaParameters
    : lambdaParameter (',' lambdaParameter)*
    ;

lambdaParameter
    : IDENTIFIER (':' expression)?
    ;

// Lexer Rules
IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

INTEGER_LITERAL
    : [0-9]+
    ;

FLOAT_LITERAL
    : [0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?
    | '.' [0-9]+ ([eE] [+-]? [0-9]+)?
    | [0-9]+ [eE] [+-]? [0-9]+
    ;

STRING_LITERAL
    : '\'' ( ~['\\\r\n] | EscapeSequence )* '\''
    | '"' ( ~["\\\r\n] | EscapeSequence )* '"'
    ;

BOOLEAN_LITERAL
    : 'true'
    | 'false'
    ;

fragment EscapeSequence
    : '\\' [btnfr"'\\]
    | '\\' ([0-3]? [0-7])? [0-7]
    | '\\' 'u' HexDigit HexDigit HexDigit HexDigit
    ;

fragment HexDigit
    : [0-9a-fA-F]
    ;

// Skip whitespace and comments
WHITESPACE
    : [ \t\r\n]+ -> skip
    ;

LINE_COMMENT
    : '#' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;