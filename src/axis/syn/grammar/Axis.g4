grammar Axis;


unitItem: 'unit' expr EOF;
modItem: 'mod' expr EOF;
defItem: 'def' expr EOF;
valItem: 'val' expr (':' expr)? ('=' expr)? EOF;


tupleBlockValElement: 'val' expr (':' expr)? ('=' expr)? EOF;
tupleBlockVarElement: 'var' expr (':' expr)? ('=' expr)? EOF;
tupleBlockLetElement: 'let' expr (':' expr)? ('=' expr)? EOF;
tupleBlockDynElement: 'dyn' expr (':' expr)? ('=' expr)? EOF;
tupleBlockMutElement: 'mut' expr (':' expr)? ('=' expr)? EOF;

useBlock: 'use' expr EOF;
defWhereBlock: 'where' ':' EOF;
defTakesBlock: 'takes' expr? ':' EOF;
defReturnsBlock: 'returns' expr EOF;
suiteBlock: 'suite' statement* EOF;

suite: statement*;

// Statements
statement
    : valStatement
    | expr
    ;

valStatement
    : 'val' (pattern) (':' expr)? ('=' expr)?
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



// expr hierarchy (precedence low to high)
expr
    : compoundExpr
    ;


// Juxtaposition (right-to-left evaluation)
compoundExpr
    : castExpr (castExpr)*
    ;


castExpr: rangeExpr (castOp castExpr)?;
castOp: '->' | '=>';


rangeExpr: logicExpr (rangeOp logicExpr)?;
rangeOp: '..=' | '..<'; // el operador ellipsis ... indica rango infinito y se utiliza como elemento solitario a = ... tambien es mas generico

// Logical operators
logicExpr
    : comparisonExpr (logicOp comparisonExpr)*
    ;

logicOp: '&&' | '||';

// Comparison operators
comparisonExpr
    : additiveExpr (comparisonOp additiveExpr)*
    ;

comparisonOp: '==' | '!=' | '<' | '<=' | '>' | '>=';

// Additive operators
additiveExpr
    : productiveExpr (additiveOp productiveExpr)*
    ;

additiveOp: '+' | '-';

// Multiplicative operators
productiveExpr
    : prefixExpr (productiveOp prefixExpr)*
    ;

productiveOp: '*' | '/' | '%' | '·';

prefixExpr
    : postfixExpr                                                   # PrefixPass          
    | etcOp prefixExpr                                              # EtcExpr
    | signOp prefixExpr                                             # SignExpr
    ;

signOp: '+' | '-' | '~' | '!'; //
etcOp: '..';

prefixOp: '+' | '-' | '!' | '~' | '..'; // etcPattern

// Postfix operations
postfixExpr
    : primaryExpr                                                   # PostfixPass
    | postfixExpr lambda                                            # TrailExpr
    | postfixExpr tupleExpr                                         # ApplyExpr
    | postfixExpr shapeExpr                                         # IndexExpr
    | postfixExpr ('.' ID)+                                         # MemberExpr
    | postfixExpr ('::' ID)+                                        # ScopeExpr
    ;

// Primary exprs
primaryExpr
    : wildcardExpr
    | ellipsisExpr
    //| etcExpr // unary operator
    | symExpr
    | litExpr
    | tupleExpr
    | lambda
    ;

ellipsisExpr: '...';

wildcardExpr: '_'; // placePattern

//etcExpr: '..' expr?; // etcPattern

symExpr: ID ('@' ID)?;

litExpr : DECIMAL
    | TEXT
    ;

// wildcard: '_';
// ellipsis: '..';
// spread: '..' expr;
// etc: '...' expr?;

// Tuple exprs
tupleExpr
    : '(' (tupleElement (',' tupleElement)*)? ','? ')'
    ;

shapeExpr
    : '[' (tupleElement (',' tupleElement)*)? ','? ']'
    ;

tupleElement
    : tuplePositionalElement
    | tupleNominalElement
    //| tupleSpreadElement
    ;

tuplePositionalElement
    : expr;

tupleNominalElement
    : expr ':' expr
    | expr '=' expr
    | expr ':' expr '=' expr
    ;

tupleSpreadElement
    : '..' expr?
    ;

//| suite (':' expr)? ('=' expr)?         # DynElement
// ..: ..T = ..alpha
// _: _ = _


// Bracket exprs (used as parentheses in other languages or trailing lambdas)
lambda
    : '{' lambdaParams? '->' statement* expr? '}'    # LambdaSuite
    | '{' statement* expr? semicolon? '}'            # BasicSuite
    ;

semicolon: ';';

lambdaParams
    : lambdaParam (',' lambdaParam)* ','?
    ;

lambdaParam
    : ID (':' expr)?
    ;

// If exprs
// ifExpr
//     : 'if' '(' expr ')' expr ('else' expr)?
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
