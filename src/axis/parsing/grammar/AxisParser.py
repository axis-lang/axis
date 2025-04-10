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
        4,1,36,339,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,32,1,0,
        1,0,1,0,1,0,1,1,1,1,1,1,1,1,3,1,75,8,1,1,1,1,1,3,1,79,8,1,1,1,3,
        1,82,8,1,1,1,1,1,1,2,1,2,1,2,1,2,1,3,1,3,5,3,92,8,3,10,3,12,3,95,
        9,3,1,3,1,3,1,4,5,4,100,8,4,10,4,12,4,103,9,4,1,5,1,5,3,5,107,8,
        5,1,6,1,6,1,6,1,6,3,6,113,8,6,1,6,1,6,3,6,117,8,6,1,6,3,6,120,8,
        6,1,7,1,7,3,7,124,8,7,1,8,1,8,1,8,1,8,5,8,130,8,8,10,8,12,8,133,
        9,8,3,8,135,8,8,1,8,1,8,1,9,1,9,1,9,1,9,1,9,3,9,144,8,9,1,10,1,10,
        1,10,1,10,3,10,150,8,10,1,11,1,11,5,11,154,8,11,10,11,12,11,157,
        9,11,1,12,1,12,1,12,5,12,162,8,12,10,12,12,12,165,9,12,1,13,1,13,
        1,14,1,14,1,14,5,14,172,8,14,10,14,12,14,175,9,14,1,15,1,15,1,15,
        5,15,180,8,15,10,15,12,15,183,9,15,1,16,1,16,1,16,5,16,188,8,16,
        10,16,12,16,191,9,16,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,
        1,17,1,17,1,17,5,17,205,8,17,10,17,12,17,208,9,17,3,17,210,8,17,
        1,17,1,17,1,17,1,17,4,17,216,8,17,11,17,12,17,217,5,17,220,8,17,
        10,17,12,17,223,9,17,1,18,1,18,1,18,1,18,1,18,1,18,3,18,231,8,18,
        1,19,1,19,1,20,1,20,1,21,1,21,1,21,1,22,1,22,1,22,1,22,5,22,244,
        8,22,10,22,12,22,247,9,22,3,22,249,8,22,1,22,3,22,252,8,22,1,22,
        1,22,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,
        1,23,1,23,1,23,3,23,271,8,23,1,24,1,24,3,24,275,8,24,1,24,1,24,5,
        24,279,8,24,10,24,12,24,282,9,24,1,24,3,24,285,8,24,1,24,1,24,1,
        24,5,24,290,8,24,10,24,12,24,293,9,24,1,24,3,24,296,8,24,1,24,3,
        24,299,8,24,1,24,3,24,302,8,24,1,25,1,25,1,26,1,26,1,26,5,26,309,
        8,26,10,26,12,26,312,9,26,1,26,3,26,315,8,26,1,27,1,27,1,27,3,27,
        320,8,27,1,28,1,28,1,28,1,28,1,28,3,28,327,8,28,1,29,1,29,1,30,1,
        30,3,30,333,8,30,1,31,1,31,1,32,1,32,1,32,0,1,34,33,0,2,4,6,8,10,
        12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,
        56,58,60,62,64,0,4,1,0,30,31,1,0,24,29,1,0,19,20,1,0,21,23,356,0,
        66,1,0,0,0,2,70,1,0,0,0,4,85,1,0,0,0,6,89,1,0,0,0,8,101,1,0,0,0,
        10,106,1,0,0,0,12,108,1,0,0,0,14,123,1,0,0,0,16,125,1,0,0,0,18,143,
        1,0,0,0,20,149,1,0,0,0,22,151,1,0,0,0,24,158,1,0,0,0,26,166,1,0,
        0,0,28,168,1,0,0,0,30,176,1,0,0,0,32,184,1,0,0,0,34,192,1,0,0,0,
        36,230,1,0,0,0,38,232,1,0,0,0,40,234,1,0,0,0,42,236,1,0,0,0,44,239,
        1,0,0,0,46,270,1,0,0,0,48,301,1,0,0,0,50,303,1,0,0,0,52,305,1,0,
        0,0,54,316,1,0,0,0,56,326,1,0,0,0,58,328,1,0,0,0,60,332,1,0,0,0,
        62,334,1,0,0,0,64,336,1,0,0,0,66,67,5,1,0,0,67,68,3,20,10,0,68,69,
        5,0,0,1,69,1,1,0,0,0,70,71,5,2,0,0,71,74,3,20,10,0,72,73,5,32,0,
        0,73,75,3,20,10,0,74,72,1,0,0,0,74,75,1,0,0,0,75,78,1,0,0,0,76,77,
        5,33,0,0,77,79,3,20,10,0,78,76,1,0,0,0,78,79,1,0,0,0,79,81,1,0,0,
        0,80,82,5,3,0,0,81,80,1,0,0,0,81,82,1,0,0,0,82,83,1,0,0,0,83,84,
        5,0,0,1,84,3,1,0,0,0,85,86,5,4,0,0,86,87,3,20,10,0,87,88,5,0,0,1,
        88,5,1,0,0,0,89,93,5,5,0,0,90,92,3,10,5,0,91,90,1,0,0,0,92,95,1,
        0,0,0,93,91,1,0,0,0,93,94,1,0,0,0,94,96,1,0,0,0,95,93,1,0,0,0,96,
        97,5,0,0,1,97,7,1,0,0,0,98,100,3,10,5,0,99,98,1,0,0,0,100,103,1,
        0,0,0,101,99,1,0,0,0,101,102,1,0,0,0,102,9,1,0,0,0,103,101,1,0,0,
        0,104,107,3,12,6,0,105,107,3,20,10,0,106,104,1,0,0,0,106,105,1,0,
        0,0,107,11,1,0,0,0,108,109,5,2,0,0,109,112,3,14,7,0,110,111,5,32,
        0,0,111,113,3,20,10,0,112,110,1,0,0,0,112,113,1,0,0,0,113,116,1,
        0,0,0,114,115,5,33,0,0,115,117,3,20,10,0,116,114,1,0,0,0,116,117,
        1,0,0,0,117,119,1,0,0,0,118,120,5,3,0,0,119,118,1,0,0,0,119,120,
        1,0,0,0,120,13,1,0,0,0,121,124,3,58,29,0,122,124,3,16,8,0,123,121,
        1,0,0,0,123,122,1,0,0,0,124,15,1,0,0,0,125,134,5,6,0,0,126,131,3,
        18,9,0,127,128,5,7,0,0,128,130,3,18,9,0,129,127,1,0,0,0,130,133,
        1,0,0,0,131,129,1,0,0,0,131,132,1,0,0,0,132,135,1,0,0,0,133,131,
        1,0,0,0,134,126,1,0,0,0,134,135,1,0,0,0,135,136,1,0,0,0,136,137,
        5,8,0,0,137,17,1,0,0,0,138,144,3,58,29,0,139,140,3,58,29,0,140,141,
        5,32,0,0,141,142,3,58,29,0,142,144,1,0,0,0,143,138,1,0,0,0,143,139,
        1,0,0,0,144,19,1,0,0,0,145,150,3,22,11,0,146,150,3,38,19,0,147,150,
        3,40,20,0,148,150,3,42,21,0,149,145,1,0,0,0,149,146,1,0,0,0,149,
        147,1,0,0,0,149,148,1,0,0,0,150,21,1,0,0,0,151,155,3,24,12,0,152,
        154,3,24,12,0,153,152,1,0,0,0,154,157,1,0,0,0,155,153,1,0,0,0,155,
        156,1,0,0,0,156,23,1,0,0,0,157,155,1,0,0,0,158,163,3,28,14,0,159,
        160,7,0,0,0,160,162,3,28,14,0,161,159,1,0,0,0,162,165,1,0,0,0,163,
        161,1,0,0,0,163,164,1,0,0,0,164,25,1,0,0,0,165,163,1,0,0,0,166,167,
        7,0,0,0,167,27,1,0,0,0,168,173,3,30,15,0,169,170,7,1,0,0,170,172,
        3,30,15,0,171,169,1,0,0,0,172,175,1,0,0,0,173,171,1,0,0,0,173,174,
        1,0,0,0,174,29,1,0,0,0,175,173,1,0,0,0,176,181,3,32,16,0,177,178,
        7,2,0,0,178,180,3,32,16,0,179,177,1,0,0,0,180,183,1,0,0,0,181,179,
        1,0,0,0,181,182,1,0,0,0,182,31,1,0,0,0,183,181,1,0,0,0,184,189,3,
        34,17,0,185,186,7,3,0,0,186,188,3,34,17,0,187,185,1,0,0,0,188,191,
        1,0,0,0,189,187,1,0,0,0,189,190,1,0,0,0,190,33,1,0,0,0,191,189,1,
        0,0,0,192,193,6,17,-1,0,193,194,3,36,18,0,194,221,1,0,0,0,195,196,
        10,4,0,0,196,220,3,48,24,0,197,198,10,3,0,0,198,220,3,44,22,0,199,
        200,10,2,0,0,200,209,5,9,0,0,201,206,3,20,10,0,202,203,5,7,0,0,203,
        205,3,20,10,0,204,202,1,0,0,0,205,208,1,0,0,0,206,204,1,0,0,0,206,
        207,1,0,0,0,207,210,1,0,0,0,208,206,1,0,0,0,209,201,1,0,0,0,209,
        210,1,0,0,0,210,211,1,0,0,0,211,220,5,10,0,0,212,215,10,1,0,0,213,
        214,5,11,0,0,214,216,3,58,29,0,215,213,1,0,0,0,216,217,1,0,0,0,217,
        215,1,0,0,0,217,218,1,0,0,0,218,220,1,0,0,0,219,195,1,0,0,0,219,
        197,1,0,0,0,219,199,1,0,0,0,219,212,1,0,0,0,220,223,1,0,0,0,221,
        219,1,0,0,0,221,222,1,0,0,0,222,35,1,0,0,0,223,221,1,0,0,0,224,231,
        3,58,29,0,225,231,3,60,30,0,226,231,3,44,22,0,227,231,3,48,24,0,
        228,231,3,38,19,0,229,231,3,40,20,0,230,224,1,0,0,0,230,225,1,0,
        0,0,230,226,1,0,0,0,230,227,1,0,0,0,230,228,1,0,0,0,230,229,1,0,
        0,0,231,37,1,0,0,0,232,233,5,12,0,0,233,39,1,0,0,0,234,235,5,13,
        0,0,235,41,1,0,0,0,236,237,5,13,0,0,237,238,3,20,10,0,238,43,1,0,
        0,0,239,248,5,6,0,0,240,245,3,46,23,0,241,242,5,7,0,0,242,244,3,
        46,23,0,243,241,1,0,0,0,244,247,1,0,0,0,245,243,1,0,0,0,245,246,
        1,0,0,0,246,249,1,0,0,0,247,245,1,0,0,0,248,240,1,0,0,0,248,249,
        1,0,0,0,249,251,1,0,0,0,250,252,5,7,0,0,251,250,1,0,0,0,251,252,
        1,0,0,0,252,253,1,0,0,0,253,254,5,8,0,0,254,45,1,0,0,0,255,271,3,
        20,10,0,256,257,3,20,10,0,257,258,5,33,0,0,258,259,3,20,10,0,259,
        271,1,0,0,0,260,261,3,20,10,0,261,262,5,32,0,0,262,263,3,20,10,0,
        263,271,1,0,0,0,264,265,3,20,10,0,265,266,5,32,0,0,266,267,3,20,
        10,0,267,268,5,33,0,0,268,269,3,20,10,0,269,271,1,0,0,0,270,255,
        1,0,0,0,270,256,1,0,0,0,270,260,1,0,0,0,270,264,1,0,0,0,271,47,1,
        0,0,0,272,274,5,14,0,0,273,275,3,52,26,0,274,273,1,0,0,0,274,275,
        1,0,0,0,275,276,1,0,0,0,276,280,5,34,0,0,277,279,3,10,5,0,278,277,
        1,0,0,0,279,282,1,0,0,0,280,278,1,0,0,0,280,281,1,0,0,0,281,284,
        1,0,0,0,282,280,1,0,0,0,283,285,3,20,10,0,284,283,1,0,0,0,284,285,
        1,0,0,0,285,286,1,0,0,0,286,302,5,15,0,0,287,291,5,14,0,0,288,290,
        3,10,5,0,289,288,1,0,0,0,290,293,1,0,0,0,291,289,1,0,0,0,291,292,
        1,0,0,0,292,295,1,0,0,0,293,291,1,0,0,0,294,296,3,20,10,0,295,294,
        1,0,0,0,295,296,1,0,0,0,296,298,1,0,0,0,297,299,3,50,25,0,298,297,
        1,0,0,0,298,299,1,0,0,0,299,300,1,0,0,0,300,302,5,15,0,0,301,272,
        1,0,0,0,301,287,1,0,0,0,302,49,1,0,0,0,303,304,5,3,0,0,304,51,1,
        0,0,0,305,310,3,54,27,0,306,307,5,7,0,0,307,309,3,54,27,0,308,306,
        1,0,0,0,309,312,1,0,0,0,310,308,1,0,0,0,310,311,1,0,0,0,311,314,
        1,0,0,0,312,310,1,0,0,0,313,315,5,7,0,0,314,313,1,0,0,0,314,315,
        1,0,0,0,315,53,1,0,0,0,316,319,3,58,29,0,317,318,5,32,0,0,318,320,
        3,20,10,0,319,317,1,0,0,0,319,320,1,0,0,0,320,55,1,0,0,0,321,327,
        3,20,10,0,322,323,3,58,29,0,323,324,5,32,0,0,324,325,3,20,10,0,325,
        327,1,0,0,0,326,321,1,0,0,0,326,322,1,0,0,0,327,57,1,0,0,0,328,329,
        5,16,0,0,329,59,1,0,0,0,330,333,3,64,32,0,331,333,3,62,31,0,332,
        330,1,0,0,0,332,331,1,0,0,0,333,61,1,0,0,0,334,335,5,18,0,0,335,
        63,1,0,0,0,336,337,5,17,0,0,337,65,1,0,0,0,41,74,78,81,93,101,106,
        112,116,119,123,131,134,143,149,155,163,173,181,189,206,209,217,
        219,221,230,245,248,251,270,274,280,284,291,295,298,301,310,314,
        319,326,332
    ]

class AxisParser ( Parser ):

    grammarFileName = "Axis.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'def'", "'val'", "';'", "'returns'", 
                     "'suite'", "'('", "','", "')'", "'['", "']'", "'.'", 
                     "'_'", "'..'", "'{'", "'}'", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "'+'", "'-'", "'*'", "'/'", "'%'", "'=='", 
                     "'!='", "'<'", "'<='", "'>'", "'>='", "'&&'", "'||'", 
                     "':'", "'='", "'->'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "ID", "DECIMAL", "TEXT", "ADD", "SUB", "MUL", "DIV", 
                      "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", 
                      "OR", "COLON", "ASSIGN", "ARROW", "WS", "COMMENT" ]

    RULE_defItem = 0
    RULE_valItem = 1
    RULE_returnsBlock = 2
    RULE_suiteBlock = 3
    RULE_suite = 4
    RULE_statement = 5
    RULE_valStatement = 6
    RULE_pattern = 7
    RULE_tuplePattern = 8
    RULE_tuplePatternElement = 9
    RULE_expression = 10
    RULE_juxtapositionExpr = 11
    RULE_logicalExpr = 12
    RULE_logicalOp = 13
    RULE_comparisonExpr = 14
    RULE_addition = 15
    RULE_product = 16
    RULE_postfix = 17
    RULE_primaryExpr = 18
    RULE_wildcard = 19
    RULE_ellipsis = 20
    RULE_spread = 21
    RULE_tuple = 22
    RULE_tupleElement = 23
    RULE_lambda = 24
    RULE_semicolon = 25
    RULE_lambdaParams = 26
    RULE_lambdaParam = 27
    RULE_argument = 28
    RULE_identifier = 29
    RULE_literal = 30
    RULE_text = 31
    RULE_decimal = 32

    ruleNames =  [ "defItem", "valItem", "returnsBlock", "suiteBlock", "suite", 
                   "statement", "valStatement", "pattern", "tuplePattern", 
                   "tuplePatternElement", "expression", "juxtapositionExpr", 
                   "logicalExpr", "logicalOp", "comparisonExpr", "addition", 
                   "product", "postfix", "primaryExpr", "wildcard", "ellipsis", 
                   "spread", "tuple", "tupleElement", "lambda", "semicolon", 
                   "lambdaParams", "lambdaParam", "argument", "identifier", 
                   "literal", "text", "decimal" ]

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
    ID=16
    DECIMAL=17
    TEXT=18
    ADD=19
    SUB=20
    MUL=21
    DIV=22
    MOD=23
    EQ=24
    NE=25
    LT=26
    LE=27
    GT=28
    GE=29
    AND=30
    OR=31
    COLON=32
    ASSIGN=33
    ARROW=34
    WS=35
    COMMENT=36

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




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
        self.enterRule(localctx, 0, self.RULE_defItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(AxisParser.T__0)
            self.state = 67
            self.expression()
            self.state = 68
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
        self.enterRule(localctx, 2, self.RULE_valItem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(AxisParser.T__1)
            self.state = 71
            self.expression()
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 72
                self.match(AxisParser.COLON)
                self.state = 73
                self.expression()


            self.state = 78
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==33:
                self.state = 76
                self.match(AxisParser.ASSIGN)
                self.state = 77
                self.expression()


            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 80
                self.match(AxisParser.T__2)


            self.state = 83
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
        self.enterRule(localctx, 4, self.RULE_returnsBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 85
            self.match(AxisParser.T__3)
            self.state = 86
            self.expression()
            self.state = 87
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
        self.enterRule(localctx, 6, self.RULE_suiteBlock)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 89
            self.match(AxisParser.T__4)
            self.state = 93
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 487492) != 0):
                self.state = 90
                self.statement()
                self.state = 95
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 96
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
        self.enterRule(localctx, 8, self.RULE_suite)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 487492) != 0):
                self.state = 98
                self.statement()
                self.state = 103
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
        self.enterRule(localctx, 10, self.RULE_statement)
        try:
            self.state = 106
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 104
                self.valStatement()
                pass
            elif token in [6, 12, 13, 14, 16, 17, 18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 105
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
        self.enterRule(localctx, 12, self.RULE_valStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 108
            self.match(AxisParser.T__1)

            self.state = 109
            self.pattern()
            self.state = 112
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 110
                self.match(AxisParser.COLON)
                self.state = 111
                self.expression()


            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==33:
                self.state = 114
                self.match(AxisParser.ASSIGN)
                self.state = 115
                self.expression()


            self.state = 119
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
            if la_ == 1:
                self.state = 118
                self.match(AxisParser.T__2)


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
        self.enterRule(localctx, 14, self.RULE_pattern)
        try:
            self.state = 123
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 121
                self.identifier()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 2)
                self.state = 122
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
        self.enterRule(localctx, 16, self.RULE_tuplePattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 125
            self.match(AxisParser.T__5)
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 126
                self.tuplePatternElement()
                self.state = 131
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==7:
                    self.state = 127
                    self.match(AxisParser.T__6)
                    self.state = 128
                    self.tuplePatternElement()
                    self.state = 133
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 136
            self.match(AxisParser.T__7)
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
        self.enterRule(localctx, 18, self.RULE_tuplePatternElement)
        try:
            self.state = 143
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 138
                self.identifier()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 139
                self.identifier()
                self.state = 140
                self.match(AxisParser.COLON)
                self.state = 141
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


        def wildcard(self):
            return self.getTypedRuleContext(AxisParser.WildcardContext,0)


        def ellipsis(self):
            return self.getTypedRuleContext(AxisParser.EllipsisContext,0)


        def spread(self):
            return self.getTypedRuleContext(AxisParser.SpreadContext,0)


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
        self.enterRule(localctx, 20, self.RULE_expression)
        try:
            self.state = 149
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 145
                self.juxtapositionExpr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 146
                self.wildcard()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 147
                self.ellipsis()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 148
                self.spread()
                pass


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
        self.enterRule(localctx, 22, self.RULE_juxtapositionExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self.logicalExpr()
            self.state = 155
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,14,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 152
                    self.logicalExpr() 
                self.state = 157
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
        self.enterRule(localctx, 24, self.RULE_logicalExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 158
            self.comparisonExpr()
            self.state = 163
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==30 or _la==31:
                self.state = 159
                _la = self._input.LA(1)
                if not(_la==30 or _la==31):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 160
                self.comparisonExpr()
                self.state = 165
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 26, self.RULE_logicalOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 166
            _la = self._input.LA(1)
            if not(_la==30 or _la==31):
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
        self.enterRule(localctx, 28, self.RULE_comparisonExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 168
            self.addition()
            self.state = 173
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 1056964608) != 0):
                self.state = 169
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1056964608) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 170
                self.addition()
                self.state = 175
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 30, self.RULE_addition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 176
            self.product()
            self.state = 181
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==19 or _la==20:
                self.state = 177
                _la = self._input.LA(1)
                if not(_la==19 or _la==20):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 178
                self.product()
                self.state = 183
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 32, self.RULE_product)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 184
            self.postfix(0)
            self.state = 189
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14680064) != 0):
                self.state = 185
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 14680064) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 186
                self.postfix(0)
                self.state = 191
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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

        def identifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.IdentifierContext)
            else:
                return self.getTypedRuleContext(AxisParser.IdentifierContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMemberAccess" ):
                listener.enterMemberAccess(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMemberAccess" ):
                listener.exitMemberAccess(self)


    class TrailingCallContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def lambda_(self):
            return self.getTypedRuleContext(AxisParser.LambdaContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTrailingCall" ):
                listener.enterTrailingCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTrailingCall" ):
                listener.exitTrailingCall(self)


    class IndexingContext(PostfixContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.PostfixContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def postfix(self):
            return self.getTypedRuleContext(AxisParser.PostfixContext,0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIndexing" ):
                listener.enterIndexing(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIndexing" ):
                listener.exitIndexing(self)



    def postfix(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = AxisParser.PostfixContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 34
        self.enterRecursionRule(localctx, 34, self.RULE_postfix, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = AxisParser.PassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 193
            self.primaryExpr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 221
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,23,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 219
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
                    if la_ == 1:
                        localctx = AxisParser.TrailingCallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 195
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 196
                        self.lambda_()
                        pass

                    elif la_ == 2:
                        localctx = AxisParser.CallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 197
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 198
                        self.tuple_()
                        pass

                    elif la_ == 3:
                        localctx = AxisParser.IndexingContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 199
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 200
                        self.match(AxisParser.T__8)
                        self.state = 209
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                            self.state = 201
                            self.expression()
                            self.state = 206
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)
                            while _la==7:
                                self.state = 202
                                self.match(AxisParser.T__6)
                                self.state = 203
                                self.expression()
                                self.state = 208
                                self._errHandler.sync(self)
                                _la = self._input.LA(1)



                        self.state = 211
                        self.match(AxisParser.T__9)
                        pass

                    elif la_ == 4:
                        localctx = AxisParser.MemberAccessContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 212
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 215 
                        self._errHandler.sync(self)
                        _alt = 1
                        while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                            if _alt == 1:
                                self.state = 213
                                self.match(AxisParser.T__10)
                                self.state = 214
                                self.identifier()

                            else:
                                raise NoViableAltException(self)
                            self.state = 217 
                            self._errHandler.sync(self)
                            _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

                        pass

             
                self.state = 223
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,23,self._ctx)

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
        self.enterRule(localctx, 36, self.RULE_primaryExpr)
        try:
            self.state = 230
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 224
                self.identifier()
                pass
            elif token in [17, 18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 225
                self.literal()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 3)
                self.state = 226
                self.tuple_()
                pass
            elif token in [14]:
                self.enterOuterAlt(localctx, 4)
                self.state = 227
                self.lambda_()
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 5)
                self.state = 228
                self.wildcard()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 6)
                self.state = 229
                self.ellipsis()
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


    class WildcardContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


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
        self.enterRule(localctx, 38, self.RULE_wildcard)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 232
            self.match(AxisParser.T__11)
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
        self.enterRule(localctx, 40, self.RULE_ellipsis)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 234
            self.match(AxisParser.T__12)
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
        self.enterRule(localctx, 42, self.RULE_spread)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 236
            self.match(AxisParser.T__12)
            self.state = 237
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
        self.enterRule(localctx, 44, self.RULE_tuple)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 239
            self.match(AxisParser.T__5)
            self.state = 248
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                self.state = 240
                self.tupleElement()
                self.state = 245
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,25,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 241
                        self.match(AxisParser.T__6)
                        self.state = 242
                        self.tupleElement() 
                    self.state = 247
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,25,self._ctx)



            self.state = 251
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 250
                self.match(AxisParser.T__6)


            self.state = 253
            self.match(AxisParser.T__7)
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
        self.enterRule(localctx, 46, self.RULE_tupleElement)
        try:
            self.state = 270
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
            if la_ == 1:
                localctx = AxisParser.TupleElementSingleContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 255
                self.expression()
                pass

            elif la_ == 2:
                localctx = AxisParser.TupleElementAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 256
                self.expression()
                self.state = 257
                self.match(AxisParser.ASSIGN)
                self.state = 258
                self.expression()
                pass

            elif la_ == 3:
                localctx = AxisParser.TupleElementBoundedContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 260
                self.expression()
                self.state = 261
                self.match(AxisParser.COLON)
                self.state = 262
                self.expression()
                pass

            elif la_ == 4:
                localctx = AxisParser.TupleElementBoundedAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 264
                self.expression()
                self.state = 265
                self.match(AxisParser.COLON)
                self.state = 266
                self.expression()
                self.state = 267
                self.match(AxisParser.ASSIGN)
                self.state = 268
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
        self.enterRule(localctx, 48, self.RULE_lambda)
        self._la = 0 # Token type
        try:
            self.state = 301
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,35,self._ctx)
            if la_ == 1:
                localctx = AxisParser.LambdaSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 272
                self.match(AxisParser.T__13)
                self.state = 274
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==16:
                    self.state = 273
                    self.lambdaParams()


                self.state = 276
                self.match(AxisParser.ARROW)
                self.state = 280
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,30,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 277
                        self.statement() 
                    self.state = 282
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,30,self._ctx)

                self.state = 284
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                    self.state = 283
                    self.expression()


                self.state = 286
                self.match(AxisParser.T__14)
                pass

            elif la_ == 2:
                localctx = AxisParser.BasicSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 287
                self.match(AxisParser.T__13)
                self.state = 291
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,32,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 288
                        self.statement() 
                    self.state = 293
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,32,self._ctx)

                self.state = 295
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                    self.state = 294
                    self.expression()


                self.state = 298
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 297
                    self.semicolon()


                self.state = 300
                self.match(AxisParser.T__14)
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
        self.enterRule(localctx, 50, self.RULE_semicolon)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 303
            self.match(AxisParser.T__2)
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
        self.enterRule(localctx, 52, self.RULE_lambdaParams)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 305
            self.lambdaParam()
            self.state = 310
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,36,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 306
                    self.match(AxisParser.T__6)
                    self.state = 307
                    self.lambdaParam() 
                self.state = 312
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,36,self._ctx)

            self.state = 314
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 313
                self.match(AxisParser.T__6)


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
        self.enterRule(localctx, 54, self.RULE_lambdaParam)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 316
            self.identifier()
            self.state = 319
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==32:
                self.state = 317
                self.match(AxisParser.COLON)
                self.state = 318
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
        self.enterRule(localctx, 56, self.RULE_argument)
        try:
            self.state = 326
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,39,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 321
                self.expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 322
                self.identifier()
                self.state = 323
                self.match(AxisParser.COLON)
                self.state = 324
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
        self.enterRule(localctx, 58, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 328
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
        self.enterRule(localctx, 60, self.RULE_literal)
        try:
            self.state = 332
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [17]:
                self.enterOuterAlt(localctx, 1)
                self.state = 330
                self.decimal()
                pass
            elif token in [18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 331
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
        self.enterRule(localctx, 62, self.RULE_text)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 334
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
        self.enterRule(localctx, 64, self.RULE_decimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 336
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
        self._predicates[17] = self.postfix_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def postfix_sempred(self, localctx:PostfixContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 1)
         




