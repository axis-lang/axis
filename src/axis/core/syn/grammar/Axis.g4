grammar Axis;

unitItem: 'unit' expression EOF;
modItem: 'mod' expression EOF;
defItem: 'def' expression EOF;
valItem: 'val' expression (':' expression)? ('=' expression)? ';'? EOF;
useItem: 'use' expression EOF;
takesBlock: 'takes' ID? ':' EOF;
whereBlock: 'where' ':' EOF;
returnsBlock: 'returns' expression EOF;
suiteBlock: 'suite' statement* EOF;

suite: statement*;

// Statements
statement
    : valStatement
    | expression
    ;

valStatement
    : 'val' (pattern) (':' expression)? ('=' expression)? ';'?
    ;

pattern
    : ID
    | tuplePattern
    ;

// Tuple pattern for destructuring
tuplePattern
    : '(' (tuplePatternElement (',' tuplePatternElement)*)? ')'
    ;

tuplePatternElement
    : ID
    | ID ':' ID
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

logicalOp: '&&' | '||';

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
    | postfix lambda                                            # TrailingLambda
    | postfix tuple                                             # Call
    | postfix shape                                             # Index
    | postfix ('.' ID)+                                         # MemberAccess
    | postfix ('::' ID)+                                        # ScopeAccess
    ;

// Primary expressions
primaryExpr
    : identifier
    | literal               // Numbers
    | tuple                 // Tuples
    | lambda                // Bracket expressions
    | spread
    | wildcard              // Wildcard
    | ellipsis              // Ellipsis
    ;

identifier: ID; // sym

literal // lit
    : DECIMAL
    | TEXT
    ;

wildcard: '_';
ellipsis: '..';
spread: '..' expression;

// Tuple expressions


tuple
    : '(' (tupleElement (',' tupleElement)*)? ','? ')'
    ;
shape
    : '[' (tupleElement (',' tupleElement)*)? ','? ']'
    ;


tupleElement
    : expression                                    # TupleElementSingle
    | expression '=' expression                     # TupleElementAssignation
    | expression ':' expression                     # TupleElementBounded
    | expression ':' expression '=' expression      # TupleElementBoundedAssignation
    ;

// ..: ..T = ..alpha
// _: _ = _


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
    : ID (':' expression)?
    ;

// Function arguments
argument
    : expression                    // Positional argument
    | ID ':' expression     // Named argument
    ;




// If expressions
// ifExpr
//     : 'if' '(' expression ')' expression ('else' expression)?
//     ;


// Lexer Rules
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
COLON: ':';
ASSIGN: '=';
ARROW: '->';

ELLIPSIS: '..';
WILDCARD: '_';

WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;
