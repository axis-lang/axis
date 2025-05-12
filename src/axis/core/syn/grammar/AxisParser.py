# Generated from src/axis/parsing/grammar/Axis.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,42,383,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,2,33,
        7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,1,0,1,0,1,
        0,1,0,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,3,3,95,8,3,
        1,3,1,3,3,3,99,8,3,1,3,3,3,102,8,3,1,3,1,3,1,4,1,4,1,4,1,4,1,5,1,
        5,3,5,112,8,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,7,1,7,1,7,1,7,1,8,1,
        8,5,8,127,8,8,10,8,12,8,130,9,8,1,8,1,8,1,9,5,9,135,8,9,10,9,12,
        9,138,9,9,1,10,1,10,3,10,142,8,10,1,11,1,11,1,11,1,11,3,11,148,8,
        11,1,11,1,11,3,11,152,8,11,1,11,3,11,155,8,11,1,12,1,12,3,12,159,
        8,12,1,13,1,13,1,13,1,13,5,13,165,8,13,10,13,12,13,168,9,13,3,13,
        170,8,13,1,13,1,13,1,14,1,14,1,14,1,14,1,14,3,14,179,8,14,1,15,1,
        15,1,16,1,16,5,16,185,8,16,10,16,12,16,188,9,16,1,17,1,17,1,17,5,
        17,193,8,17,10,17,12,17,196,9,17,1,18,1,18,1,19,1,19,1,19,5,19,203,
        8,19,10,19,12,19,206,9,19,1,20,1,20,1,20,5,20,211,8,20,10,20,12,
        20,214,9,20,1,21,1,21,1,21,5,21,219,8,21,10,21,12,21,222,9,21,1,
        22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,4,22,236,
        8,22,11,22,12,22,237,1,22,1,22,1,22,4,22,243,8,22,11,22,12,22,244,
        5,22,247,8,22,10,22,12,22,250,9,22,1,23,1,23,1,23,1,23,1,23,1,23,
        1,23,3,23,259,8,23,1,24,1,24,1,25,1,25,1,26,1,26,1,26,1,27,1,27,
        1,27,1,27,5,27,272,8,27,10,27,12,27,275,9,27,3,27,277,8,27,1,27,
        3,27,280,8,27,1,27,1,27,1,28,1,28,1,28,1,28,5,28,288,8,28,10,28,
        12,28,291,9,28,3,28,293,8,28,1,28,3,28,296,8,28,1,28,1,28,1,29,1,
        29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,29,1,
        29,3,29,315,8,29,1,30,1,30,3,30,319,8,30,1,30,1,30,5,30,323,8,30,
        10,30,12,30,326,9,30,1,30,3,30,329,8,30,1,30,1,30,1,30,5,30,334,
        8,30,10,30,12,30,337,9,30,1,30,3,30,340,8,30,1,30,3,30,343,8,30,
        1,30,3,30,346,8,30,1,31,1,31,1,32,1,32,1,32,5,32,353,8,32,10,32,
        12,32,356,9,32,1,32,3,32,359,8,32,1,33,1,33,1,33,3,33,364,8,33,1,
        34,1,34,1,34,1,34,1,34,3,34,371,8,34,1,35,1,35,1,36,1,36,3,36,377,
        8,36,1,37,1,37,1,38,1,38,1,38,0,1,44,39,0,2,4,6,8,10,12,14,16,18,
        20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62,
        64,66,68,70,72,74,76,0,4,1,0,34,35,1,0,28,33,1,0,23,24,1,0,25,27,
        396,0,78,1,0,0,0,2,82,1,0,0,0,4,86,1,0,0,0,6,90,1,0,0,0,8,105,1,
        0,0,0,10,109,1,0,0,0,12,116,1,0,0,0,14,120,1,0,0,0,16,124,1,0,0,
        0,18,136,1,0,0,0,20,141,1,0,0,0,22,143,1,0,0,0,24,158,1,0,0,0,26,
        160,1,0,0,0,28,178,1,0,0,0,30,180,1,0,0,0,32,182,1,0,0,0,34,189,
        1,0,0,0,36,197,1,0,0,0,38,199,1,0,0,0,40,207,1,0,0,0,42,215,1,0,
        0,0,44,223,1,0,0,0,46,258,1,0,0,0,48,260,1,0,0,0,50,262,1,0,0,0,
        52,264,1,0,0,0,54,267,1,0,0,0,56,283,1,0,0,0,58,314,1,0,0,0,60,345,
        1,0,0,0,62,347,1,0,0,0,64,349,1,0,0,0,66,360,1,0,0,0,68,370,1,0,
        0,0,70,372,1,0,0,0,72,376,1,0,0,0,74,378,1,0,0,0,76,380,1,0,0,0,
        78,79,5,1,0,0,79,80,3,30,15,0,80,81,5,0,0,1,81,1,1,0,0,0,82,83,5,
        2,0,0,83,84,3,30,15,0,84,85,5,0,0,1,85,3,1,0,0,0,86,87,5,3,0,0,87,
        88,3,30,15,0,88,89,5,0,0,1,89,5,1,0,0,0,90,91,5,4,0,0,91,94,3,30,
        15,0,92,93,5,36,0,0,93,95,3,30,15,0,94,92,1,0,0,0,94,95,1,0,0,0,
        95,98,1,0,0,0,96,97,5,37,0,0,97,99,3,30,15,0,98,96,1,0,0,0,98,99,
        1,0,0,0,99,101,1,0,0,0,100,102,5,5,0,0,101,100,1,0,0,0,101,102,1,
        0,0,0,102,103,1,0,0,0,103,104,5,0,0,1,104,7,1,0,0,0,105,106,5,6,
        0,0,106,107,3,30,15,0,107,108,5,0,0,1,108,9,1,0,0,0,109,111,5,7,
        0,0,110,112,5,20,0,0,111,110,1,0,0,0,111,112,1,0,0,0,112,113,1,0,
        0,0,113,114,5,36,0,0,114,115,5,0,0,1,115,11,1,0,0,0,116,117,5,8,
        0,0,117,118,5,36,0,0,118,119,5,0,0,1,119,13,1,0,0,0,120,121,5,9,
        0,0,121,122,3,30,15,0,122,123,5,0,0,1,123,15,1,0,0,0,124,128,5,10,
        0,0,125,127,3,20,10,0,126,125,1,0,0,0,127,130,1,0,0,0,128,126,1,
        0,0,0,128,129,1,0,0,0,129,131,1,0,0,0,130,128,1,0,0,0,131,132,5,
        0,0,1,132,17,1,0,0,0,133,135,3,20,10,0,134,133,1,0,0,0,135,138,1,
        0,0,0,136,134,1,0,0,0,136,137,1,0,0,0,137,19,1,0,0,0,138,136,1,0,
        0,0,139,142,3,22,11,0,140,142,3,30,15,0,141,139,1,0,0,0,141,140,
        1,0,0,0,142,21,1,0,0,0,143,144,5,4,0,0,144,147,3,24,12,0,145,146,
        5,36,0,0,146,148,3,30,15,0,147,145,1,0,0,0,147,148,1,0,0,0,148,151,
        1,0,0,0,149,150,5,37,0,0,150,152,3,30,15,0,151,149,1,0,0,0,151,152,
        1,0,0,0,152,154,1,0,0,0,153,155,5,5,0,0,154,153,1,0,0,0,154,155,
        1,0,0,0,155,23,1,0,0,0,156,159,3,70,35,0,157,159,3,26,13,0,158,156,
        1,0,0,0,158,157,1,0,0,0,159,25,1,0,0,0,160,169,5,11,0,0,161,166,
        3,28,14,0,162,163,5,12,0,0,163,165,3,28,14,0,164,162,1,0,0,0,165,
        168,1,0,0,0,166,164,1,0,0,0,166,167,1,0,0,0,167,170,1,0,0,0,168,
        166,1,0,0,0,169,161,1,0,0,0,169,170,1,0,0,0,170,171,1,0,0,0,171,
        172,5,13,0,0,172,27,1,0,0,0,173,179,3,70,35,0,174,175,3,70,35,0,
        175,176,5,36,0,0,176,177,3,70,35,0,177,179,1,0,0,0,178,173,1,0,0,
        0,178,174,1,0,0,0,179,29,1,0,0,0,180,181,3,32,16,0,181,31,1,0,0,
        0,182,186,3,34,17,0,183,185,3,34,17,0,184,183,1,0,0,0,185,188,1,
        0,0,0,186,184,1,0,0,0,186,187,1,0,0,0,187,33,1,0,0,0,188,186,1,0,
        0,0,189,194,3,38,19,0,190,191,7,0,0,0,191,193,3,38,19,0,192,190,
        1,0,0,0,193,196,1,0,0,0,194,192,1,0,0,0,194,195,1,0,0,0,195,35,1,
        0,0,0,196,194,1,0,0,0,197,198,7,0,0,0,198,37,1,0,0,0,199,204,3,40,
        20,0,200,201,7,1,0,0,201,203,3,40,20,0,202,200,1,0,0,0,203,206,1,
        0,0,0,204,202,1,0,0,0,204,205,1,0,0,0,205,39,1,0,0,0,206,204,1,0,
        0,0,207,212,3,42,21,0,208,209,7,2,0,0,209,211,3,42,21,0,210,208,
        1,0,0,0,211,214,1,0,0,0,212,210,1,0,0,0,212,213,1,0,0,0,213,41,1,
        0,0,0,214,212,1,0,0,0,215,220,3,44,22,0,216,217,7,3,0,0,217,219,
        3,44,22,0,218,216,1,0,0,0,219,222,1,0,0,0,220,218,1,0,0,0,220,221,
        1,0,0,0,221,43,1,0,0,0,222,220,1,0,0,0,223,224,6,22,-1,0,224,225,
        3,46,23,0,225,248,1,0,0,0,226,227,10,5,0,0,227,247,3,60,30,0,228,
        229,10,4,0,0,229,247,3,54,27,0,230,231,10,3,0,0,231,247,3,56,28,
        0,232,235,10,2,0,0,233,234,5,14,0,0,234,236,5,20,0,0,235,233,1,0,
        0,0,236,237,1,0,0,0,237,235,1,0,0,0,237,238,1,0,0,0,238,247,1,0,
        0,0,239,242,10,1,0,0,240,241,5,15,0,0,241,243,5,20,0,0,242,240,1,
        0,0,0,243,244,1,0,0,0,244,242,1,0,0,0,244,245,1,0,0,0,245,247,1,
        0,0,0,246,226,1,0,0,0,246,228,1,0,0,0,246,230,1,0,0,0,246,232,1,
        0,0,0,246,239,1,0,0,0,247,250,1,0,0,0,248,246,1,0,0,0,248,249,1,
        0,0,0,249,45,1,0,0,0,250,248,1,0,0,0,251,259,3,70,35,0,252,259,3,
        72,36,0,253,259,3,54,27,0,254,259,3,60,30,0,255,259,3,52,26,0,256,
        259,3,48,24,0,257,259,3,50,25,0,258,251,1,0,0,0,258,252,1,0,0,0,
        258,253,1,0,0,0,258,254,1,0,0,0,258,255,1,0,0,0,258,256,1,0,0,0,
        258,257,1,0,0,0,259,47,1,0,0,0,260,261,5,40,0,0,261,49,1,0,0,0,262,
        263,5,39,0,0,263,51,1,0,0,0,264,265,5,39,0,0,265,266,3,30,15,0,266,
        53,1,0,0,0,267,276,5,11,0,0,268,273,3,58,29,0,269,270,5,12,0,0,270,
        272,3,58,29,0,271,269,1,0,0,0,272,275,1,0,0,0,273,271,1,0,0,0,273,
        274,1,0,0,0,274,277,1,0,0,0,275,273,1,0,0,0,276,268,1,0,0,0,276,
        277,1,0,0,0,277,279,1,0,0,0,278,280,5,12,0,0,279,278,1,0,0,0,279,
        280,1,0,0,0,280,281,1,0,0,0,281,282,5,13,0,0,282,55,1,0,0,0,283,
        292,5,16,0,0,284,289,3,58,29,0,285,286,5,12,0,0,286,288,3,58,29,
        0,287,285,1,0,0,0,288,291,1,0,0,0,289,287,1,0,0,0,289,290,1,0,0,
        0,290,293,1,0,0,0,291,289,1,0,0,0,292,284,1,0,0,0,292,293,1,0,0,
        0,293,295,1,0,0,0,294,296,5,12,0,0,295,294,1,0,0,0,295,296,1,0,0,
        0,296,297,1,0,0,0,297,298,5,17,0,0,298,57,1,0,0,0,299,315,3,30,15,
        0,300,301,3,30,15,0,301,302,5,37,0,0,302,303,3,30,15,0,303,315,1,
        0,0,0,304,305,3,30,15,0,305,306,5,36,0,0,306,307,3,30,15,0,307,315,
        1,0,0,0,308,309,3,30,15,0,309,310,5,36,0,0,310,311,3,30,15,0,311,
        312,5,37,0,0,312,313,3,30,15,0,313,315,1,0,0,0,314,299,1,0,0,0,314,
        300,1,0,0,0,314,304,1,0,0,0,314,308,1,0,0,0,315,59,1,0,0,0,316,318,
        5,18,0,0,317,319,3,64,32,0,318,317,1,0,0,0,318,319,1,0,0,0,319,320,
        1,0,0,0,320,324,5,38,0,0,321,323,3,20,10,0,322,321,1,0,0,0,323,326,
        1,0,0,0,324,322,1,0,0,0,324,325,1,0,0,0,325,328,1,0,0,0,326,324,
        1,0,0,0,327,329,3,30,15,0,328,327,1,0,0,0,328,329,1,0,0,0,329,330,
        1,0,0,0,330,346,5,19,0,0,331,335,5,18,0,0,332,334,3,20,10,0,333,
        332,1,0,0,0,334,337,1,0,0,0,335,333,1,0,0,0,335,336,1,0,0,0,336,
        339,1,0,0,0,337,335,1,0,0,0,338,340,3,30,15,0,339,338,1,0,0,0,339,
        340,1,0,0,0,340,342,1,0,0,0,341,343,3,62,31,0,342,341,1,0,0,0,342,
        343,1,0,0,0,343,344,1,0,0,0,344,346,5,19,0,0,345,316,1,0,0,0,345,
        331,1,0,0,0,346,61,1,0,0,0,347,348,5,5,0,0,348,63,1,0,0,0,349,354,
        3,66,33,0,350,351,5,12,0,0,351,353,3,66,33,0,352,350,1,0,0,0,353,
        356,1,0,0,0,354,352,1,0,0,0,354,355,1,0,0,0,355,358,1,0,0,0,356,
        354,1,0,0,0,357,359,5,12,0,0,358,357,1,0,0,0,358,359,1,0,0,0,359,
        65,1,0,0,0,360,363,3,70,35,0,361,362,5,36,0,0,362,364,3,30,15,0,
        363,361,1,0,0,0,363,364,1,0,0,0,364,67,1,0,0,0,365,371,3,30,15,0,
        366,367,3,70,35,0,367,368,5,36,0,0,368,369,3,30,15,0,369,371,1,0,
        0,0,370,365,1,0,0,0,370,366,1,0,0,0,371,69,1,0,0,0,372,373,5,20,
        0,0,373,71,1,0,0,0,374,377,3,76,38,0,375,377,3,74,37,0,376,374,1,
        0,0,0,376,375,1,0,0,0,377,73,1,0,0,0,378,379,5,22,0,0,379,75,1,0,
        0,0,380,381,5,21,0,0,381,77,1,0,0,0,43,94,98,101,111,128,136,141,
        147,151,154,158,166,169,178,186,194,204,212,220,237,244,246,248,
        258,273,276,279,289,292,295,314,318,324,328,335,339,342,345,354,
        358,363,370,376
    ]

class AxisParser ( Parser ):

    grammarFileName = "Axis.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'unit'", "'mod'", "'def'", "'val'", "';'", 
                     "'use'", "'takes'", "'where'", "'returns'", "'suite'", 
                     "'('", "','", "')'", "'.'", "'::'", "'['", "']'", "'{'", 
                     "'}'", "<INVALID>", "<INVALID>", "<INVALID>", "'+'", 
                     "'-'", "'*'", "'/'", "'%'", "'=='", "'!='", "'<'", 
                     "'<='", "'>'", "'>='", "'&&'", "'||'", "':'", "'='", 
                     "'->'", "'..'", "'_'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "ID", "DECIMAL", "TEXT", "ADD", "SUB", "MUL", "DIV", 
                      "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", 
                      "OR", "COLON", "ASSIGN", "ARROW", "ELLIPSIS", "WILDCARD", 
                      "WS", "COMMENT" ]

    RULE_unitItem = 0
    RULE_modItem = 1
    RULE_defItem = 2
    RULE_valItem = 3
    RULE_useItem = 4
    RULE_takesBlock = 5
    RULE_whereBlock = 6
    RULE_returnsBlock = 7
    RULE_suiteBlock = 8
    RULE_suite = 9
    RULE_statement = 10
    RULE_valStatement = 11
    RULE_pattern = 12
    RULE_tuplePattern = 13
    RULE_tuplePatternElement = 14
    RULE_expression = 15
    RULE_juxtapositionExpr = 16
    RULE_logicalExpr = 17
    RULE_logicalOp = 18
    RULE_comparisonExpr = 19
    RULE_addition = 20
    RULE_product = 21
    RULE_postfix = 22
    RULE_primaryExpr = 23
    RULE_wildcard = 24
    RULE_ellipsis = 25
    RULE_spread = 26
    RULE_tuple = 27
    RULE_shape = 28
    RULE_tupleElement = 29
    RULE_lambda = 30
    RULE_semicolon = 31
    RULE_lambdaParams = 32
    RULE_lambdaParam = 33
    RULE_argument = 34
    RULE_identifier = 35
    RULE_literal = 36
    RULE_text = 37
    RULE_decimal = 38

    ruleNames =  [ "unitItem", "modItem", "defItem", "valItem", "useItem", 
                   "takesBlock", "whereBlock", "returnsBlock", "suiteBlock", 
                   "suite", "statement", "valStatement", "pattern", "tuplePattern", 
                   "tuplePatternElement", "expression", "juxtapositionExpr", 
                   "logicalExpr", "logicalOp", "comparisonExpr", "addition", 
                   "product", "postfix", "primaryExpr", "wildcard", "ellipsis", 
                   "spread", "tuple", "shape", "tupleElement", "lambda", 
                   "semicolon", "lambdaParams", "lambdaParam", "argument", 
                   "identifier", "literal", "text", "decimal" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    ID=20
    DECIMAL=21
    TEXT=22
    ADD=23
    SUB=24
    MUL=25
    DIV=26
    MOD=27
    EQ=28
    NE=29
    LT=30
    LE=31
    GT=32
    GE=33
    AND=34
    OR=35
    COLON=36
    ASSIGN=37
    ARROW=38
    ELLIPSIS=39
    WILDCARD=40
    WS=41
    COMMENT=42

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class UnitItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_unitItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnitItem" ):
                listener.enterUnitItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnitItem" ):
                listener.exitUnitItem(self)




    def unitItem(self):

        localctx = AxisParser.UnitItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_unitItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(AxisParser.T__0)
            self.state = 79
            self.expression()
            self.state = 80
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ModItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_modItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterModItem" ):
                listener.enterModItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitModItem" ):
                listener.exitModItem(self)




    def modItem(self):

        localctx = AxisParser.ModItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_modItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 82
            self.match(AxisParser.T__1)
            self.state = 83
            self.expression()
            self.state = 84
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DefItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_defItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefItem" ):
                listener.enterDefItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefItem" ):
                listener.exitDefItem(self)




    def defItem(self):

        localctx = AxisParser.DefItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_defItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86
            self.match(AxisParser.T__2)
            self.state = 87
            self.expression()
            self.state = 88
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def ASSIGN(self):
            return self.getToken(AxisParser.ASSIGN, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_valItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValItem" ):
                listener.enterValItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValItem" ):
                listener.exitValItem(self)




    def valItem(self):

        localctx = AxisParser.ValItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_valItem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 90
            self.match(AxisParser.T__3)
            self.state = 91
            self.expression()
            self.state = 94
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 92
                self.match(AxisParser.COLON)
                self.state = 93
                self.expression()


            self.state = 98
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==37:
                self.state = 96
                self.match(AxisParser.ASSIGN)
                self.state = 97
                self.expression()


            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 100
                self.match(AxisParser.T__4)


            self.state = 103
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UseItemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_useItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUseItem" ):
                listener.enterUseItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUseItem" ):
                listener.exitUseItem(self)




    def useItem(self):

        localctx = AxisParser.UseItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_useItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(AxisParser.T__5)
            self.state = 106
            self.expression()
            self.state = 107
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TakesBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def ID(self):
            return self.getToken(AxisParser.ID, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_takesBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTakesBlock" ):
                listener.enterTakesBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTakesBlock" ):
                listener.exitTakesBlock(self)




    def takesBlock(self):

        localctx = AxisParser.TakesBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_takesBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 109
            self.match(AxisParser.T__6)
            self.state = 111
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==20:
                self.state = 110
                self.match(AxisParser.ID)


            self.state = 113
            self.match(AxisParser.COLON)
            self.state = 114
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhereBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_whereBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhereBlock" ):
                listener.enterWhereBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhereBlock" ):
                listener.exitWhereBlock(self)




    def whereBlock(self):

        localctx = AxisParser.WhereBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_whereBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 116
            self.match(AxisParser.T__7)
            self.state = 117
            self.match(AxisParser.COLON)
            self.state = 118
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReturnsBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_returnsBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturnsBlock" ):
                listener.enterReturnsBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturnsBlock" ):
                listener.exitReturnsBlock(self)




    def returnsBlock(self):

        localctx = AxisParser.ReturnsBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_returnsBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 120
            self.match(AxisParser.T__8)
            self.state = 121
            self.expression()
            self.state = 122
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SuiteBlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(AxisParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.StatementContext)
            else:
                return self.getTypedRuleContext(AxisParser.StatementContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_suiteBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSuiteBlock" ):
                listener.enterSuiteBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSuiteBlock" ):
                listener.exitSuiteBlock(self)




    def suiteBlock(self):

        localctx = AxisParser.SuiteBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_suiteBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 124
            self.match(AxisParser.T__9)
            self.state = 128
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045904) != 0):
                self.state = 125
                self.statement()
                self.state = 130
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 131
            self.match(AxisParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SuiteContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.StatementContext)
            else:
                return self.getTypedRuleContext(AxisParser.StatementContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_suite

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSuite" ):
                listener.enterSuite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSuite" ):
                listener.exitSuite(self)




    def suite(self):

        localctx = AxisParser.SuiteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_suite)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045904) != 0):
                self.state = 133
                self.statement()
                self.state = 138
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def valStatement(self):
            return self.getTypedRuleContext(AxisParser.ValStatementContext,0)


        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)




    def statement(self):

        localctx = AxisParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_statement)
        try:
            self.state = 141
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [4]:
                self.enterOuterAlt(localctx, 1)
                self.state = 139
                self.valStatement()
                pass
            elif token in [11, 18, 20, 21, 22, 39, 40]:
                self.enterOuterAlt(localctx, 2)
                self.state = 140
                self.expression()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pattern(self):
            return self.getTypedRuleContext(AxisParser.PatternContext,0)


        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def ASSIGN(self):
            return self.getToken(AxisParser.ASSIGN, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_valStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValStatement" ):
                listener.enterValStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValStatement" ):
                listener.exitValStatement(self)




    def valStatement(self):

        localctx = AxisParser.ValStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_valStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 143
            self.match(AxisParser.T__3)

            self.state = 144
            self.pattern()
            self.state = 147
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 145
                self.match(AxisParser.COLON)
                self.state = 146
                self.expression()


            self.state = 151
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==37:
                self.state = 149
                self.match(AxisParser.ASSIGN)
                self.state = 150
                self.expression()


            self.state = 154
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 153
                self.match(AxisParser.T__4)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PatternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(AxisParser.IdentifierContext,0)


        def tuplePattern(self):
            return self.getTypedRuleContext(AxisParser.TuplePatternContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_pattern

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPattern" ):
                listener.enterPattern(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPattern" ):
                listener.exitPattern(self)




    def pattern(self):

        localctx = AxisParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_pattern)
        try:
            self.state = 158
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [20]:
                self.enterOuterAlt(localctx, 1)
                self.state = 156
                self.identifier()
                pass
            elif token in [11]:
                self.enterOuterAlt(localctx, 2)
                self.state = 157
                self.tuplePattern()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TuplePatternContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tuplePatternElement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.TuplePatternElementContext)
            else:
                return self.getTypedRuleContext(AxisParser.TuplePatternElementContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_tuplePattern

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTuplePattern" ):
                listener.enterTuplePattern(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTuplePattern" ):
                listener.exitTuplePattern(self)




    def tuplePattern(self):

        localctx = AxisParser.TuplePatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_tuplePattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(AxisParser.T__10)
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==20:
                self.state = 161
                self.tuplePatternElement()
                self.state = 166
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==12:
                    self.state = 162
                    self.match(AxisParser.T__11)
                    self.state = 163
                    self.tuplePatternElement()
                    self.state = 168
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 171
            self.match(AxisParser.T__12)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TuplePatternElementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.IdentifierContext)
            else:
                return self.getTypedRuleContext(AxisParser.IdentifierContext,i)


        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_tuplePatternElement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTuplePatternElement" ):
                listener.enterTuplePatternElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTuplePatternElement" ):
                listener.exitTuplePatternElement(self)




    def tuplePatternElement(self):

        localctx = AxisParser.TuplePatternElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_tuplePatternElement)
        try:
            self.state = 178
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 173
                self.identifier()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 174
                self.identifier()
                self.state = 175
                self.match(AxisParser.COLON)
                self.state = 176
                self.identifier()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def juxtapositionExpr(self):
            return self.getTypedRuleContext(AxisParser.JuxtapositionExprContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)




    def expression(self):

        localctx = AxisParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            self.juxtapositionExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class JuxtapositionExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def logicalExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.LogicalExprContext)
            else:
                return self.getTypedRuleContext(AxisParser.LogicalExprContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_juxtapositionExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJuxtapositionExpr" ):
                listener.enterJuxtapositionExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJuxtapositionExpr" ):
                listener.exitJuxtapositionExpr(self)




    def juxtapositionExpr(self):

        localctx = AxisParser.JuxtapositionExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_juxtapositionExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            self.logicalExpr()
            self.state = 186
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 183
                    self.logicalExpr() 
                self.state = 188
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,14,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def comparisonExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ComparisonExprContext)
            else:
                return self.getTypedRuleContext(AxisParser.ComparisonExprContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.AND)
            else:
                return self.getToken(AxisParser.AND, i)

        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.OR)
            else:
                return self.getToken(AxisParser.OR, i)

        def getRuleIndex(self):
            return AxisParser.RULE_logicalExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalExpr" ):
                listener.enterLogicalExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalExpr" ):
                listener.exitLogicalExpr(self)




    def logicalExpr(self):

        localctx = AxisParser.LogicalExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_logicalExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self.comparisonExpr()
            self.state = 194
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 190
                    _la = self._input.LA(1)
                    if not(_la==34 or _la==35):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 191
                    self.comparisonExpr() 
                self.state = 196
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LogicalOpContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AND(self):
            return self.getToken(AxisParser.AND, 0)

        def OR(self):
            return self.getToken(AxisParser.OR, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_logicalOp

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalOp" ):
                listener.enterLogicalOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalOp" ):
                listener.exitLogicalOp(self)




    def logicalOp(self):

        localctx = AxisParser.LogicalOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_logicalOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 197
            _la = self._input.LA(1)
            if not(_la==34 or _la==35):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparisonExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def addition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.AdditionContext)
            else:
                return self.getTypedRuleContext(AxisParser.AdditionContext,i)


        def EQ(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.EQ)
            else:
                return self.getToken(AxisParser.EQ, i)

        def NE(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.NE)
            else:
                return self.getToken(AxisParser.NE, i)

        def LT(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.LT)
            else:
                return self.getToken(AxisParser.LT, i)

        def LE(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.LE)
            else:
                return self.getToken(AxisParser.LE, i)

        def GT(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.GT)
            else:
                return self.getToken(AxisParser.GT, i)

        def GE(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.GE)
            else:
                return self.getToken(AxisParser.GE, i)

        def getRuleIndex(self):
            return AxisParser.RULE_comparisonExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparisonExpr" ):
                listener.enterComparisonExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparisonExpr" ):
                listener.exitComparisonExpr(self)




    def comparisonExpr(self):

        localctx = AxisParser.ComparisonExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_comparisonExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            self.addition()
            self.state = 204
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 200
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 16911433728) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 201
                    self.addition() 
                self.state = 206
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AdditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def product(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ProductContext)
            else:
                return self.getTypedRuleContext(AxisParser.ProductContext,i)


        def ADD(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.ADD)
            else:
                return self.getToken(AxisParser.ADD, i)

        def SUB(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.SUB)
            else:
                return self.getToken(AxisParser.SUB, i)

        def getRuleIndex(self):
            return AxisParser.RULE_addition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddition" ):
                listener.enterAddition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddition" ):
                listener.exitAddition(self)




    def addition(self):

        localctx = AxisParser.AdditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_addition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 207
            self.product()
            self.state = 212
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,17,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 208
                    _la = self._input.LA(1)
                    if not(_la==23 or _la==24):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 209
                    self.product() 
                self.state = 214
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProductContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def postfix(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.PostfixContext)
            else:
                return self.getTypedRuleContext(AxisParser.PostfixContext,i)


        def MUL(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.MUL)
            else:
                return self.getToken(AxisParser.MUL, i)

        def DIV(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.DIV)
            else:
                return self.getToken(AxisParser.DIV, i)

        def MOD(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.MOD)
            else:
                return self.getToken(AxisParser.MOD, i)

        def getRuleIndex(self):
            return AxisParser.RULE_product

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProduct" ):
                listener.enterProduct(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProduct" ):
                listener.exitProduct(self)




    def product(self):

        localctx = AxisParser.ProductContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_product)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 215
            self.postfix(0)
            self.state = 220
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,18,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 216
                    _la = self._input.LA(1)
                    if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 234881024) != 0)):
                        self._errHandler.recoverInline(self)
                    else:
                        self._errHandler.reportMatch(self)
                        self.consume()
                    self.state = 217
                    self.postfix(0) 
                self.state = 222
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,18,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PostfixContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return AxisParser.RULE_postfix

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class CallContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def tuple_(self):
            return self.getTypedRuleContext(AxisParser.TupleContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCall" ):
                listener.enterCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCall" ):
                listener.exitCall(self)


    class PassContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def primaryExpr(self):
            return self.getTypedRuleContext(AxisParser.PrimaryExprContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPass" ):
                listener.enterPass(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPass" ):
                listener.exitPass(self)


    class MemberAccessContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.ID)
            else:
                return self.getToken(AxisParser.ID, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMemberAccess" ):
                listener.enterMemberAccess(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMemberAccess" ):
                listener.exitMemberAccess(self)


    class TrailingLambdaContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def lambda_(self):
            return self.getTypedRuleContext(AxisParser.LambdaContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTrailingLambda" ):
                listener.enterTrailingLambda(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTrailingLambda" ):
                listener.exitTrailingLambda(self)


    class ScopeAccessContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(AxisParser.ID)
            else:
                return self.getToken(AxisParser.ID, i)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterScopeAccess" ):
                listener.enterScopeAccess(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitScopeAccess" ):
                listener.exitScopeAccess(self)


    class IndexContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def shape(self):
            return self.getTypedRuleContext(AxisParser.ShapeContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIndex" ):
                listener.enterIndex(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIndex" ):
                listener.exitIndex(self)



    def postfix(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = AxisParser.PostfixContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 44
        self.enterRecursionRule(localctx, 44, self.RULE_postfix, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = AxisParser.PassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 224
            self.primaryExpr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 248
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,22,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 246
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,21,self._ctx)
                    if la_ == 1:
                        localctx = AxisParser.TrailingLambdaContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 226
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 227
                        self.lambda_()
                        pass

                    elif la_ == 2:
                        localctx = AxisParser.CallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 228
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 229
                        self.tuple_()
                        pass

                    elif la_ == 3:
                        localctx = AxisParser.IndexContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 230
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 231
                        self.shape()
                        pass

                    elif la_ == 4:
                        localctx = AxisParser.MemberAccessContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 232
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 235 
                        self._errHandler.sync(self)
                        _alt = 1
                        while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                            if _alt == 1:
                                self.state = 233
                                self.match(AxisParser.T__13)
                                self.state = 234
                                self.match(AxisParser.ID)

                            else:
                                raise NoViableAltException(self)
                            self.state = 237 
                            self._errHandler.sync(self)
                            _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

                        pass

                    elif la_ == 5:
                        localctx = AxisParser.ScopeAccessContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 239
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 242 
                        self._errHandler.sync(self)
                        _alt = 1
                        while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                            if _alt == 1:
                                self.state = 240
                                self.match(AxisParser.T__14)
                                self.state = 241
                                self.match(AxisParser.ID)

                            else:
                                raise NoViableAltException(self)
                            self.state = 244 
                            self._errHandler.sync(self)
                            _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

                        pass

             
                self.state = 250
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,22,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class PrimaryExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(AxisParser.IdentifierContext,0)


        def literal(self):
            return self.getTypedRuleContext(AxisParser.LiteralContext,0)


        def tuple_(self):
            return self.getTypedRuleContext(AxisParser.TupleContext,0)


        def lambda_(self):
            return self.getTypedRuleContext(AxisParser.LambdaContext,0)


        def spread(self):
            return self.getTypedRuleContext(AxisParser.SpreadContext,0)


        def wildcard(self):
            return self.getTypedRuleContext(AxisParser.WildcardContext,0)


        def ellipsis(self):
            return self.getTypedRuleContext(AxisParser.EllipsisContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_primaryExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrimaryExpr" ):
                listener.enterPrimaryExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrimaryExpr" ):
                listener.exitPrimaryExpr(self)




    def primaryExpr(self):

        localctx = AxisParser.PrimaryExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_primaryExpr)
        try:
            self.state = 258
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,23,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 251
                self.identifier()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 252
                self.literal()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 253
                self.tuple_()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 254
                self.lambda_()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 255
                self.spread()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 256
                self.wildcard()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 257
                self.ellipsis()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WildcardContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WILDCARD(self):
            return self.getToken(AxisParser.WILDCARD, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_wildcard

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWildcard" ):
                listener.enterWildcard(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWildcard" ):
                listener.exitWildcard(self)




    def wildcard(self):

        localctx = AxisParser.WildcardContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_wildcard)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 260
            self.match(AxisParser.WILDCARD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EllipsisContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ELLIPSIS(self):
            return self.getToken(AxisParser.ELLIPSIS, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_ellipsis

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEllipsis" ):
                listener.enterEllipsis(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEllipsis" ):
                listener.exitEllipsis(self)




    def ellipsis(self):

        localctx = AxisParser.EllipsisContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_ellipsis)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 262
            self.match(AxisParser.ELLIPSIS)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SpreadContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ELLIPSIS(self):
            return self.getToken(AxisParser.ELLIPSIS, 0)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_spread

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpread" ):
                listener.enterSpread(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpread" ):
                listener.exitSpread(self)




    def spread(self):

        localctx = AxisParser.SpreadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_spread)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            self.match(AxisParser.ELLIPSIS)
            self.state = 265
            self.expression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TupleContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tupleElement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.TupleElementContext)
            else:
                return self.getTypedRuleContext(AxisParser.TupleElementContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_tuple

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTuple" ):
                listener.enterTuple(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTuple" ):
                listener.exitTuple(self)




    def tuple_(self):

        localctx = AxisParser.TupleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_tuple)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 267
            self.match(AxisParser.T__10)
            self.state = 276
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045888) != 0):
                self.state = 268
                self.tupleElement()
                self.state = 273
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,24,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 269
                        self.match(AxisParser.T__11)
                        self.state = 270
                        self.tupleElement() 
                    self.state = 275
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,24,self._ctx)



            self.state = 279
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 278
                self.match(AxisParser.T__11)


            self.state = 281
            self.match(AxisParser.T__12)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ShapeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tupleElement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.TupleElementContext)
            else:
                return self.getTypedRuleContext(AxisParser.TupleElementContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_shape

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterShape" ):
                listener.enterShape(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitShape" ):
                listener.exitShape(self)




    def shape(self):

        localctx = AxisParser.ShapeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_shape)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 283
            self.match(AxisParser.T__15)
            self.state = 292
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045888) != 0):
                self.state = 284
                self.tupleElement()
                self.state = 289
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,27,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 285
                        self.match(AxisParser.T__11)
                        self.state = 286
                        self.tupleElement() 
                    self.state = 291
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,27,self._ctx)



            self.state = 295
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 294
                self.match(AxisParser.T__11)


            self.state = 297
            self.match(AxisParser.T__16)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TupleElementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return AxisParser.RULE_tupleElement

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class TupleElementSingleContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementSingle" ):
                listener.enterTupleElementSingle(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementSingle" ):
                listener.exitTupleElementSingle(self)


    class TupleElementBoundedAssignationContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)

        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)
        def ASSIGN(self):
            return self.getToken(AxisParser.ASSIGN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementBoundedAssignation" ):
                listener.enterTupleElementBoundedAssignation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementBoundedAssignation" ):
                listener.exitTupleElementBoundedAssignation(self)


    class TupleElementAssignationContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)

        def ASSIGN(self):
            return self.getToken(AxisParser.ASSIGN, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementAssignation" ):
                listener.enterTupleElementAssignation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementAssignation" ):
                listener.exitTupleElementAssignation(self)


    class TupleElementBoundedContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)

        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementBounded" ):
                listener.enterTupleElementBounded(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementBounded" ):
                listener.exitTupleElementBounded(self)



    def tupleElement(self):

        localctx = AxisParser.TupleElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_tupleElement)
        try:
            self.state = 314
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,30,self._ctx)
            if la_ == 1:
                localctx = AxisParser.TupleElementSingleContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 299
                self.expression()
                pass

            elif la_ == 2:
                localctx = AxisParser.TupleElementAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 300
                self.expression()
                self.state = 301
                self.match(AxisParser.ASSIGN)
                self.state = 302
                self.expression()
                pass

            elif la_ == 3:
                localctx = AxisParser.TupleElementBoundedContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 304
                self.expression()
                self.state = 305
                self.match(AxisParser.COLON)
                self.state = 306
                self.expression()
                pass

            elif la_ == 4:
                localctx = AxisParser.TupleElementBoundedAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 308
                self.expression()
                self.state = 309
                self.match(AxisParser.COLON)
                self.state = 310
                self.expression()
                self.state = 311
                self.match(AxisParser.ASSIGN)
                self.state = 312
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LambdaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return AxisParser.RULE_lambda

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class BasicSuiteContext(LambdaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.LambdaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.StatementContext)
            else:
                return self.getTypedRuleContext(AxisParser.StatementContext,i)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)

        def semicolon(self):
            return self.getTypedRuleContext(AxisParser.SemicolonContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBasicSuite" ):
                listener.enterBasicSuite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBasicSuite" ):
                listener.exitBasicSuite(self)


    class LambdaSuiteContext(LambdaContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.LambdaContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ARROW(self):
            return self.getToken(AxisParser.ARROW, 0)
        def lambdaParams(self):
            return self.getTypedRuleContext(AxisParser.LambdaParamsContext,0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.StatementContext)
            else:
                return self.getTypedRuleContext(AxisParser.StatementContext,i)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLambdaSuite" ):
                listener.enterLambdaSuite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLambdaSuite" ):
                listener.exitLambdaSuite(self)



    def lambda_(self):

        localctx = AxisParser.LambdaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_lambda)
        self._la = 0 # Token type
        try:
            self.state = 345
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                localctx = AxisParser.LambdaSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 316
                self.match(AxisParser.T__17)
                self.state = 318
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==20:
                    self.state = 317
                    self.lambdaParams()


                self.state = 320
                self.match(AxisParser.ARROW)
                self.state = 324
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,32,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 321
                        self.statement() 
                    self.state = 326
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,32,self._ctx)

                self.state = 328
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045888) != 0):
                    self.state = 327
                    self.expression()


                self.state = 330
                self.match(AxisParser.T__18)
                pass

            elif la_ == 2:
                localctx = AxisParser.BasicSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 331
                self.match(AxisParser.T__17)
                self.state = 335
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,34,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 332
                        self.statement() 
                    self.state = 337
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,34,self._ctx)

                self.state = 339
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1649275045888) != 0):
                    self.state = 338
                    self.expression()


                self.state = 342
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 341
                    self.semicolon()


                self.state = 344
                self.match(AxisParser.T__18)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SemicolonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return AxisParser.RULE_semicolon

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSemicolon" ):
                listener.enterSemicolon(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSemicolon" ):
                listener.exitSemicolon(self)




    def semicolon(self):

        localctx = AxisParser.SemicolonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_semicolon)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 347
            self.match(AxisParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LambdaParamsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def lambdaParam(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.LambdaParamContext)
            else:
                return self.getTypedRuleContext(AxisParser.LambdaParamContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_lambdaParams

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLambdaParams" ):
                listener.enterLambdaParams(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLambdaParams" ):
                listener.exitLambdaParams(self)




    def lambdaParams(self):

        localctx = AxisParser.LambdaParamsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_lambdaParams)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 349
            self.lambdaParam()
            self.state = 354
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,38,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 350
                    self.match(AxisParser.T__11)
                    self.state = 351
                    self.lambdaParam() 
                self.state = 356
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,38,self._ctx)

            self.state = 358
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==12:
                self.state = 357
                self.match(AxisParser.T__11)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LambdaParamContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(AxisParser.IdentifierContext,0)


        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_lambdaParam

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLambdaParam" ):
                listener.enterLambdaParam(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLambdaParam" ):
                listener.exitLambdaParam(self)




    def lambdaParam(self):

        localctx = AxisParser.LambdaParamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_lambdaParam)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 360
            self.identifier()
            self.state = 363
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 361
                self.match(AxisParser.COLON)
                self.state = 362
                self.expression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def identifier(self):
            return self.getTypedRuleContext(AxisParser.IdentifierContext,0)


        def COLON(self):
            return self.getToken(AxisParser.COLON, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_argument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgument" ):
                listener.enterArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgument" ):
                listener.exitArgument(self)




    def argument(self):

        localctx = AxisParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_argument)
        try:
            self.state = 370
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,41,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 365
                self.expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 366
                self.identifier()
                self.state = 367
                self.match(AxisParser.COLON)
                self.state = 368
                self.expression()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(AxisParser.ID, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_identifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifier" ):
                listener.enterIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifier" ):
                listener.exitIdentifier(self)




    def identifier(self):

        localctx = AxisParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 372
            self.match(AxisParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def decimal(self):
            return self.getTypedRuleContext(AxisParser.DecimalContext,0)


        def text(self):
            return self.getTypedRuleContext(AxisParser.TextContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)




    def literal(self):

        localctx = AxisParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_literal)
        try:
            self.state = 376
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [21]:
                self.enterOuterAlt(localctx, 1)
                self.state = 374
                self.decimal()
                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 2)
                self.state = 375
                self.text()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TextContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(AxisParser.TEXT, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_text

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterText" ):
                listener.enterText(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitText" ):
                listener.exitText(self)




    def text(self):

        localctx = AxisParser.TextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_text)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 378
            self.match(AxisParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DecimalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DECIMAL(self):
            return self.getToken(AxisParser.DECIMAL, 0)

        def getRuleIndex(self):
            return AxisParser.RULE_decimal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDecimal" ):
                listener.enterDecimal(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDecimal" ):
                listener.exitDecimal(self)




    def decimal(self):

        localctx = AxisParser.DecimalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_decimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 380
            self.match(AxisParser.DECIMAL)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[22] = self.postfix_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def postfix_sempred(self, localctx:PostfixContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 1)
         




