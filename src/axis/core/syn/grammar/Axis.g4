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
    : juxtaposition
    ;


// Juxtaposition (right-to-left evaluation)
juxtaposition
    : range (range)*
    ;


range: logical ('..' logical)?;


// Logical operators
logical
    : comparison (logicalOp comparison)*
    ;

logicalOp: '&&' | '||';

// Comparison operators
comparison
    : addition (comparisonOp addition)*
    ;

comparisonOp: '==' | '!=' | '<' | '<=' | '>' | '>=';

// Additive operators
addition
    : product (additiveOp product)*
    ;

additiveOp: '+' | '-';

// Multiplicative operators
product
    : prefix (productiveOp prefix)*
    ;

productiveOp: '*' | '/' | '%';

prefix
    : postfix                                                   # PrefixPass          
    ;

// Postfix operations
postfix
    : primary                                                   # PostfixPass
    | postfix lambda                                            # TrailingLambda
    | postfix tuple                                             # Call
    | postfix shape                                             # Index
    | postfix ('.' ID)+                                         # MemberAccess
    | postfix ('::' ID)+                                        # ScopeAccess
    ;

// Primary expressions
primary
    : sym
    | lit
    | tuple                 // Tuples
    | lambda                // Bracket expressions
    // | wildcard              // Wildcard
    // | spread
    // | ellipsis              // Ellipsis
    //| etc
    ;

sym: ID ('@' ID)?;

lit : DECIMAL
    | TEXT
    ;

// wildcard: '_';
// ellipsis: '..';
// spread: '..' expression;
// etc: '...' expression?;

// Tuple expressions
tuple
    : '(' (element (',' element)*)? ','? ')'
    ;

shape
    : '[' (element (',' element)*)? ','? ']'
    ;

element
    : expression                                        # ValueElement
    | ID (':' expression)? ('=' expression)?            # NamedElement
    | '..' expression?                                  # SpreadElement
    ;
//| suite (':' expression)? ('=' expression)?         # DynElement
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

// If expressions
// ifExpr
//     : 'if' '(' expression ')' expression ('else' expression)?
//     ;


// Lexer Rules
ID: [$]?[a-zA-Z_][a-zA-Z0-9_]*;
DECIMAL: [0-9]+ ('.' [0-9]+)?;
TEXT: '\'' ( ~'\'' | '\\' . )* '\'';
// ADD: '+';
// SUB: '-';
// MUL: '*';
// DIV: '/';
// MOD: '%';
// EQ: '==';
// NE: '!=';
// LT: '<';
// LE: '<=';
// GT: '>';
// GE: '>=';
// AND: '&&';
// OR: '||';
// COLON: ':';
// ASSIGN: '=';
// ARROW: '->';

// ELLIPSIS: '..';
// WILDCARD: '_';

WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;
