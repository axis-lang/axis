# Generated from src/axis/codebase/grammar/Axis.g4 by ANTLR 4.13.2
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
        4,1,34,319,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,1,0,5,0,64,8,0,10,0,12,0,
        67,9,0,1,0,1,0,1,1,1,1,1,1,1,2,1,2,1,2,1,2,3,2,78,8,2,1,2,1,2,3,
        2,82,8,2,1,2,3,2,85,8,2,1,3,1,3,1,4,1,4,1,4,1,4,3,4,93,8,4,1,4,1,
        4,3,4,97,8,4,1,4,3,4,100,8,4,1,5,1,5,3,5,104,8,5,1,6,1,6,1,6,1,6,
        5,6,110,8,6,10,6,12,6,113,9,6,3,6,115,8,6,1,6,1,6,1,7,1,7,1,7,1,
        7,1,7,3,7,124,8,7,1,8,1,8,1,8,1,8,3,8,130,8,8,1,9,1,9,5,9,134,8,
        9,10,9,12,9,137,9,9,1,10,1,10,1,10,5,10,142,8,10,10,10,12,10,145,
        9,10,1,11,1,11,1,12,1,12,1,12,5,12,152,8,12,10,12,12,12,155,9,12,
        1,13,1,13,1,13,5,13,160,8,13,10,13,12,13,163,9,13,1,14,1,14,1,14,
        5,14,168,8,14,10,14,12,14,171,9,14,1,15,1,15,1,15,1,15,1,15,1,15,
        1,15,1,15,1,15,1,15,1,15,1,15,5,15,185,8,15,10,15,12,15,188,9,15,
        3,15,190,8,15,1,15,1,15,1,15,1,15,4,15,196,8,15,11,15,12,15,197,
        5,15,200,8,15,10,15,12,15,203,9,15,1,16,1,16,1,16,1,16,1,16,1,16,
        3,16,211,8,16,1,17,1,17,1,18,1,18,1,19,1,19,1,19,1,20,1,20,1,20,
        1,20,5,20,224,8,20,10,20,12,20,227,9,20,3,20,229,8,20,1,20,3,20,
        232,8,20,1,20,1,20,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,1,21,
        1,21,1,21,1,21,1,21,1,21,1,21,3,21,251,8,21,1,22,1,22,3,22,255,8,
        22,1,22,1,22,5,22,259,8,22,10,22,12,22,262,9,22,1,22,3,22,265,8,
        22,1,22,1,22,1,22,5,22,270,8,22,10,22,12,22,273,9,22,1,22,3,22,276,
        8,22,1,22,3,22,279,8,22,1,22,3,22,282,8,22,1,23,1,23,1,24,1,24,1,
        24,5,24,289,8,24,10,24,12,24,292,9,24,1,24,3,24,295,8,24,1,25,1,
        25,1,25,3,25,300,8,25,1,26,1,26,1,26,1,26,1,26,3,26,307,8,26,1,27,
        1,27,1,28,1,28,3,28,313,8,28,1,29,1,29,1,30,1,30,1,30,0,1,30,31,
        0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,
        46,48,50,52,54,56,58,60,0,4,1,0,30,31,1,0,24,29,1,0,19,20,1,0,21,
        23,336,0,65,1,0,0,0,2,70,1,0,0,0,4,73,1,0,0,0,6,86,1,0,0,0,8,88,
        1,0,0,0,10,103,1,0,0,0,12,105,1,0,0,0,14,123,1,0,0,0,16,129,1,0,
        0,0,18,131,1,0,0,0,20,138,1,0,0,0,22,146,1,0,0,0,24,148,1,0,0,0,
        26,156,1,0,0,0,28,164,1,0,0,0,30,172,1,0,0,0,32,210,1,0,0,0,34,212,
        1,0,0,0,36,214,1,0,0,0,38,216,1,0,0,0,40,219,1,0,0,0,42,250,1,0,
        0,0,44,281,1,0,0,0,46,283,1,0,0,0,48,285,1,0,0,0,50,296,1,0,0,0,
        52,306,1,0,0,0,54,308,1,0,0,0,56,312,1,0,0,0,58,314,1,0,0,0,60,316,
        1,0,0,0,62,64,3,6,3,0,63,62,1,0,0,0,64,67,1,0,0,0,65,63,1,0,0,0,
        65,66,1,0,0,0,66,68,1,0,0,0,67,65,1,0,0,0,68,69,5,0,0,1,69,1,1,0,
        0,0,70,71,5,1,0,0,71,72,3,16,8,0,72,3,1,0,0,0,73,74,5,2,0,0,74,77,
        3,16,8,0,75,76,5,3,0,0,76,78,3,16,8,0,77,75,1,0,0,0,77,78,1,0,0,
        0,78,81,1,0,0,0,79,80,5,4,0,0,80,82,3,16,8,0,81,79,1,0,0,0,81,82,
        1,0,0,0,82,84,1,0,0,0,83,85,5,5,0,0,84,83,1,0,0,0,84,85,1,0,0,0,
        85,5,1,0,0,0,86,87,3,8,4,0,87,7,1,0,0,0,88,89,5,2,0,0,89,92,3,10,
        5,0,90,91,5,3,0,0,91,93,3,16,8,0,92,90,1,0,0,0,92,93,1,0,0,0,93,
        96,1,0,0,0,94,95,5,4,0,0,95,97,3,16,8,0,96,94,1,0,0,0,96,97,1,0,
        0,0,97,99,1,0,0,0,98,100,5,5,0,0,99,98,1,0,0,0,99,100,1,0,0,0,100,
        9,1,0,0,0,101,104,3,54,27,0,102,104,3,12,6,0,103,101,1,0,0,0,103,
        102,1,0,0,0,104,11,1,0,0,0,105,114,5,6,0,0,106,111,3,14,7,0,107,
        108,5,7,0,0,108,110,3,14,7,0,109,107,1,0,0,0,110,113,1,0,0,0,111,
        109,1,0,0,0,111,112,1,0,0,0,112,115,1,0,0,0,113,111,1,0,0,0,114,
        106,1,0,0,0,114,115,1,0,0,0,115,116,1,0,0,0,116,117,5,8,0,0,117,
        13,1,0,0,0,118,124,3,54,27,0,119,120,3,54,27,0,120,121,5,3,0,0,121,
        122,3,54,27,0,122,124,1,0,0,0,123,118,1,0,0,0,123,119,1,0,0,0,124,
        15,1,0,0,0,125,130,3,18,9,0,126,130,3,34,17,0,127,130,3,36,18,0,
        128,130,3,38,19,0,129,125,1,0,0,0,129,126,1,0,0,0,129,127,1,0,0,
        0,129,128,1,0,0,0,130,17,1,0,0,0,131,135,3,20,10,0,132,134,3,20,
        10,0,133,132,1,0,0,0,134,137,1,0,0,0,135,133,1,0,0,0,135,136,1,0,
        0,0,136,19,1,0,0,0,137,135,1,0,0,0,138,143,3,24,12,0,139,140,7,0,
        0,0,140,142,3,24,12,0,141,139,1,0,0,0,142,145,1,0,0,0,143,141,1,
        0,0,0,143,144,1,0,0,0,144,21,1,0,0,0,145,143,1,0,0,0,146,147,7,0,
        0,0,147,23,1,0,0,0,148,153,3,26,13,0,149,150,7,1,0,0,150,152,3,26,
        13,0,151,149,1,0,0,0,152,155,1,0,0,0,153,151,1,0,0,0,153,154,1,0,
        0,0,154,25,1,0,0,0,155,153,1,0,0,0,156,161,3,28,14,0,157,158,7,2,
        0,0,158,160,3,28,14,0,159,157,1,0,0,0,160,163,1,0,0,0,161,159,1,
        0,0,0,161,162,1,0,0,0,162,27,1,0,0,0,163,161,1,0,0,0,164,169,3,30,
        15,0,165,166,7,3,0,0,166,168,3,30,15,0,167,165,1,0,0,0,168,171,1,
        0,0,0,169,167,1,0,0,0,169,170,1,0,0,0,170,29,1,0,0,0,171,169,1,0,
        0,0,172,173,6,15,-1,0,173,174,3,32,16,0,174,201,1,0,0,0,175,176,
        10,4,0,0,176,200,3,44,22,0,177,178,10,3,0,0,178,200,3,40,20,0,179,
        180,10,2,0,0,180,189,5,9,0,0,181,186,3,16,8,0,182,183,5,7,0,0,183,
        185,3,16,8,0,184,182,1,0,0,0,185,188,1,0,0,0,186,184,1,0,0,0,186,
        187,1,0,0,0,187,190,1,0,0,0,188,186,1,0,0,0,189,181,1,0,0,0,189,
        190,1,0,0,0,190,191,1,0,0,0,191,200,5,10,0,0,192,195,10,1,0,0,193,
        194,5,11,0,0,194,196,3,54,27,0,195,193,1,0,0,0,196,197,1,0,0,0,197,
        195,1,0,0,0,197,198,1,0,0,0,198,200,1,0,0,0,199,175,1,0,0,0,199,
        177,1,0,0,0,199,179,1,0,0,0,199,192,1,0,0,0,200,203,1,0,0,0,201,
        199,1,0,0,0,201,202,1,0,0,0,202,31,1,0,0,0,203,201,1,0,0,0,204,211,
        3,54,27,0,205,211,3,56,28,0,206,211,3,40,20,0,207,211,3,44,22,0,
        208,211,3,34,17,0,209,211,3,36,18,0,210,204,1,0,0,0,210,205,1,0,
        0,0,210,206,1,0,0,0,210,207,1,0,0,0,210,208,1,0,0,0,210,209,1,0,
        0,0,211,33,1,0,0,0,212,213,5,12,0,0,213,35,1,0,0,0,214,215,5,13,
        0,0,215,37,1,0,0,0,216,217,5,13,0,0,217,218,3,16,8,0,218,39,1,0,
        0,0,219,228,5,6,0,0,220,225,3,42,21,0,221,222,5,7,0,0,222,224,3,
        42,21,0,223,221,1,0,0,0,224,227,1,0,0,0,225,223,1,0,0,0,225,226,
        1,0,0,0,226,229,1,0,0,0,227,225,1,0,0,0,228,220,1,0,0,0,228,229,
        1,0,0,0,229,231,1,0,0,0,230,232,5,7,0,0,231,230,1,0,0,0,231,232,
        1,0,0,0,232,233,1,0,0,0,233,234,5,8,0,0,234,41,1,0,0,0,235,251,3,
        16,8,0,236,237,3,16,8,0,237,238,5,4,0,0,238,239,3,16,8,0,239,251,
        1,0,0,0,240,241,3,16,8,0,241,242,5,3,0,0,242,243,3,16,8,0,243,251,
        1,0,0,0,244,245,3,16,8,0,245,246,5,3,0,0,246,247,3,16,8,0,247,248,
        5,4,0,0,248,249,3,16,8,0,249,251,1,0,0,0,250,235,1,0,0,0,250,236,
        1,0,0,0,250,240,1,0,0,0,250,244,1,0,0,0,251,43,1,0,0,0,252,254,5,
        14,0,0,253,255,3,48,24,0,254,253,1,0,0,0,254,255,1,0,0,0,255,256,
        1,0,0,0,256,260,5,32,0,0,257,259,3,6,3,0,258,257,1,0,0,0,259,262,
        1,0,0,0,260,258,1,0,0,0,260,261,1,0,0,0,261,264,1,0,0,0,262,260,
        1,0,0,0,263,265,3,16,8,0,264,263,1,0,0,0,264,265,1,0,0,0,265,266,
        1,0,0,0,266,282,5,15,0,0,267,271,5,14,0,0,268,270,3,6,3,0,269,268,
        1,0,0,0,270,273,1,0,0,0,271,269,1,0,0,0,271,272,1,0,0,0,272,275,
        1,0,0,0,273,271,1,0,0,0,274,276,3,16,8,0,275,274,1,0,0,0,275,276,
        1,0,0,0,276,278,1,0,0,0,277,279,3,46,23,0,278,277,1,0,0,0,278,279,
        1,0,0,0,279,280,1,0,0,0,280,282,5,15,0,0,281,252,1,0,0,0,281,267,
        1,0,0,0,282,45,1,0,0,0,283,284,5,5,0,0,284,47,1,0,0,0,285,290,3,
        50,25,0,286,287,5,7,0,0,287,289,3,50,25,0,288,286,1,0,0,0,289,292,
        1,0,0,0,290,288,1,0,0,0,290,291,1,0,0,0,291,294,1,0,0,0,292,290,
        1,0,0,0,293,295,5,7,0,0,294,293,1,0,0,0,294,295,1,0,0,0,295,49,1,
        0,0,0,296,299,3,54,27,0,297,298,5,3,0,0,298,300,3,16,8,0,299,297,
        1,0,0,0,299,300,1,0,0,0,300,51,1,0,0,0,301,307,3,16,8,0,302,303,
        3,54,27,0,303,304,5,3,0,0,304,305,3,16,8,0,305,307,1,0,0,0,306,301,
        1,0,0,0,306,302,1,0,0,0,307,53,1,0,0,0,308,309,5,16,0,0,309,55,1,
        0,0,0,310,313,3,60,30,0,311,313,3,58,29,0,312,310,1,0,0,0,312,311,
        1,0,0,0,313,57,1,0,0,0,314,315,5,18,0,0,315,59,1,0,0,0,316,317,5,
        17,0,0,317,61,1,0,0,0,39,65,77,81,84,92,96,99,103,111,114,123,129,
        135,143,153,161,169,186,189,197,199,201,210,225,228,231,250,254,
        260,264,271,275,278,281,290,294,299,306,312
    ]

class AxisParser ( Parser ):

    grammarFileName = "Axis.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'def'", "'val'", "':'", "'='", "';'", 
                     "'('", "','", "')'", "'['", "']'", "'.'", "'_'", "'..'", 
                     "'{'", "'}'", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "'+'", "'-'", "'*'", "'/'", "'%'", "'=='", "'!='", 
                     "'<'", "'<='", "'>'", "'>='", "'&&'", "'||'", "'->'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "ID", "DECIMAL", "TEXT", "ADD", "SUB", "MUL", "DIV", 
                      "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", 
                      "OR", "ARROW", "WS", "COMMENT" ]

    RULE_suite = 0
    RULE_defItem = 1
    RULE_valItem = 2
    RULE_statement = 3
    RULE_valStatement = 4
    RULE_pattern = 5
    RULE_tuplePattern = 6
    RULE_tuplePatternElement = 7
    RULE_expression = 8
    RULE_juxtapositionExpr = 9
    RULE_logicalExpr = 10
    RULE_logicalOp = 11
    RULE_comparisonExpr = 12
    RULE_addition = 13
    RULE_product = 14
    RULE_postfix = 15
    RULE_primaryExpr = 16
    RULE_wildcard = 17
    RULE_ellipsis = 18
    RULE_spread = 19
    RULE_tuple = 20
    RULE_tupleElement = 21
    RULE_lambda = 22
    RULE_semicolon = 23
    RULE_lambdaParams = 24
    RULE_lambdaParam = 25
    RULE_argument = 26
    RULE_identifier = 27
    RULE_literal = 28
    RULE_text = 29
    RULE_decimal = 30

    ruleNames =  [ "suite", "defItem", "valItem", "statement", "valStatement", 
                   "pattern", "tuplePattern", "tuplePatternElement", "expression", 
                   "juxtapositionExpr", "logicalExpr", "logicalOp", "comparisonExpr", 
                   "addition", "product", "postfix", "primaryExpr", "wildcard", 
                   "ellipsis", "spread", "tuple", "tupleElement", "lambda", 
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
    ARROW=32
    WS=33
    COMMENT=34

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class SuiteContext(ParserRuleContext):
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
            return AxisParser.RULE_suite

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSuite" ):
                listener.enterSuite(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSuite" ):
                listener.exitSuite(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSuite" ):
                return visitor.visitSuite(self)
            else:
                return visitor.visitChildren(self)




    def suite(self):

        localctx = AxisParser.SuiteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_suite)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==2:
                self.state = 62
                self.statement()
                self.state = 67
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 68
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


        def getRuleIndex(self):
            return AxisParser.RULE_defItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDefItem" ):
                listener.enterDefItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDefItem" ):
                listener.exitDefItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDefItem" ):
                return visitor.visitDefItem(self)
            else:
                return visitor.visitChildren(self)




    def defItem(self):

        localctx = AxisParser.DefItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_defItem)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(AxisParser.T__0)
            self.state = 71
            self.expression()
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


        def getRuleIndex(self):
            return AxisParser.RULE_valItem

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValItem" ):
                listener.enterValItem(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValItem" ):
                listener.exitValItem(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValItem" ):
                return visitor.visitValItem(self)
            else:
                return visitor.visitChildren(self)




    def valItem(self):

        localctx = AxisParser.ValItemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_valItem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(AxisParser.T__1)

            self.state = 74
            self.expression()
            self.state = 77
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 75
                self.match(AxisParser.T__2)
                self.state = 76
                self.expression()


            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 79
                self.match(AxisParser.T__3)
                self.state = 80
                self.expression()


            self.state = 84
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==5:
                self.state = 83
                self.match(AxisParser.T__4)


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


        def getRuleIndex(self):
            return AxisParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = AxisParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86
            self.valStatement()
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


        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def getRuleIndex(self):
            return AxisParser.RULE_valStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValStatement" ):
                listener.enterValStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValStatement" ):
                listener.exitValStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValStatement" ):
                return visitor.visitValStatement(self)
            else:
                return visitor.visitChildren(self)




    def valStatement(self):

        localctx = AxisParser.ValStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_valStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 88
            self.match(AxisParser.T__1)

            self.state = 89
            self.pattern()
            self.state = 92
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 90
                self.match(AxisParser.T__2)
                self.state = 91
                self.expression()


            self.state = 96
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==4:
                self.state = 94
                self.match(AxisParser.T__3)
                self.state = 95
                self.expression()


            self.state = 99
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 98
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPattern" ):
                return visitor.visitPattern(self)
            else:
                return visitor.visitChildren(self)




    def pattern(self):

        localctx = AxisParser.PatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_pattern)
        try:
            self.state = 103
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 101
                self.identifier()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 2)
                self.state = 102
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTuplePattern" ):
                return visitor.visitTuplePattern(self)
            else:
                return visitor.visitChildren(self)




    def tuplePattern(self):

        localctx = AxisParser.TuplePatternContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_tuplePattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(AxisParser.T__5)
            self.state = 114
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 106
                self.tuplePatternElement()
                self.state = 111
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==7:
                    self.state = 107
                    self.match(AxisParser.T__6)
                    self.state = 108
                    self.tuplePatternElement()
                    self.state = 113
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 116
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


        def getRuleIndex(self):
            return AxisParser.RULE_tuplePatternElement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTuplePatternElement" ):
                listener.enterTuplePatternElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTuplePatternElement" ):
                listener.exitTuplePatternElement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTuplePatternElement" ):
                return visitor.visitTuplePatternElement(self)
            else:
                return visitor.visitChildren(self)




    def tuplePatternElement(self):

        localctx = AxisParser.TuplePatternElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_tuplePatternElement)
        try:
            self.state = 123
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,10,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 118
                self.identifier()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 119
                self.identifier()
                self.state = 120
                self.match(AxisParser.T__2)
                self.state = 121
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = AxisParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_expression)
        try:
            self.state = 129
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,11,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 125
                self.juxtapositionExpr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 126
                self.wildcard()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 127
                self.ellipsis()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 128
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJuxtapositionExpr" ):
                return visitor.visitJuxtapositionExpr(self)
            else:
                return visitor.visitChildren(self)




    def juxtapositionExpr(self):

        localctx = AxisParser.JuxtapositionExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_juxtapositionExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 131
            self.logicalExpr()
            self.state = 135
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 132
                    self.logicalExpr() 
                self.state = 137
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalExpr" ):
                return visitor.visitLogicalExpr(self)
            else:
                return visitor.visitChildren(self)




    def logicalExpr(self):

        localctx = AxisParser.LogicalExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_logicalExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 138
            self.comparisonExpr()
            self.state = 143
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==30 or _la==31:
                self.state = 139
                _la = self._input.LA(1)
                if not(_la==30 or _la==31):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 140
                self.comparisonExpr()
                self.state = 145
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalOp" ):
                return visitor.visitLogicalOp(self)
            else:
                return visitor.visitChildren(self)




    def logicalOp(self):

        localctx = AxisParser.LogicalOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_logicalOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 146
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparisonExpr" ):
                return visitor.visitComparisonExpr(self)
            else:
                return visitor.visitChildren(self)




    def comparisonExpr(self):

        localctx = AxisParser.ComparisonExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_comparisonExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 148
            self.addition()
            self.state = 153
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 1056964608) != 0):
                self.state = 149
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 1056964608) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 150
                self.addition()
                self.state = 155
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddition" ):
                return visitor.visitAddition(self)
            else:
                return visitor.visitChildren(self)




    def addition(self):

        localctx = AxisParser.AdditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_addition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 156
            self.product()
            self.state = 161
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==19 or _la==20:
                self.state = 157
                _la = self._input.LA(1)
                if not(_la==19 or _la==20):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 158
                self.product()
                self.state = 163
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProduct" ):
                return visitor.visitProduct(self)
            else:
                return visitor.visitChildren(self)




    def product(self):

        localctx = AxisParser.ProductContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_product)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 164
            self.postfix(0)
            self.state = 169
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 14680064) != 0):
                self.state = 165
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 14680064) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 166
                self.postfix(0)
                self.state = 171
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCall" ):
                return visitor.visitCall(self)
            else:
                return visitor.visitChildren(self)


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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPass" ):
                return visitor.visitPass(self)
            else:
                return visitor.visitChildren(self)


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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMemberAccess" ):
                return visitor.visitMemberAccess(self)
            else:
                return visitor.visitChildren(self)


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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTrailingCall" ):
                return visitor.visitTrailingCall(self)
            else:
                return visitor.visitChildren(self)


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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIndexing" ):
                return visitor.visitIndexing(self)
            else:
                return visitor.visitChildren(self)



    def postfix(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = AxisParser.PostfixContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 30
        self.enterRecursionRule(localctx, 30, self.RULE_postfix, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = AxisParser.PassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 173
            self.primaryExpr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 201
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,21,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 199
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,20,self._ctx)
                    if la_ == 1:
                        localctx = AxisParser.TrailingCallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 175
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 176
                        self.lambda_()
                        pass

                    elif la_ == 2:
                        localctx = AxisParser.CallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 177
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 178
                        self.tuple_()
                        pass

                    elif la_ == 3:
                        localctx = AxisParser.IndexingContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 179
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 180
                        self.match(AxisParser.T__8)
                        self.state = 189
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                            self.state = 181
                            self.expression()
                            self.state = 186
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)
                            while _la==7:
                                self.state = 182
                                self.match(AxisParser.T__6)
                                self.state = 183
                                self.expression()
                                self.state = 188
                                self._errHandler.sync(self)
                                _la = self._input.LA(1)



                        self.state = 191
                        self.match(AxisParser.T__9)
                        pass

                    elif la_ == 4:
                        localctx = AxisParser.MemberAccessContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 192
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 195 
                        self._errHandler.sync(self)
                        _alt = 1
                        while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                            if _alt == 1:
                                self.state = 193
                                self.match(AxisParser.T__10)
                                self.state = 194
                                self.identifier()

                            else:
                                raise NoViableAltException(self)
                            self.state = 197 
                            self._errHandler.sync(self)
                            _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

                        pass

             
                self.state = 203
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrimaryExpr" ):
                return visitor.visitPrimaryExpr(self)
            else:
                return visitor.visitChildren(self)




    def primaryExpr(self):

        localctx = AxisParser.PrimaryExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_primaryExpr)
        try:
            self.state = 210
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 204
                self.identifier()
                pass
            elif token in [17, 18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 205
                self.literal()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 3)
                self.state = 206
                self.tuple_()
                pass
            elif token in [14]:
                self.enterOuterAlt(localctx, 4)
                self.state = 207
                self.lambda_()
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 5)
                self.state = 208
                self.wildcard()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 6)
                self.state = 209
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWildcard" ):
                return visitor.visitWildcard(self)
            else:
                return visitor.visitChildren(self)




    def wildcard(self):

        localctx = AxisParser.WildcardContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_wildcard)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 212
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEllipsis" ):
                return visitor.visitEllipsis(self)
            else:
                return visitor.visitChildren(self)




    def ellipsis(self):

        localctx = AxisParser.EllipsisContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_ellipsis)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 214
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpread" ):
                return visitor.visitSpread(self)
            else:
                return visitor.visitChildren(self)




    def spread(self):

        localctx = AxisParser.SpreadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_spread)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 216
            self.match(AxisParser.T__12)
            self.state = 217
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTuple" ):
                return visitor.visitTuple(self)
            else:
                return visitor.visitChildren(self)




    def tuple_(self):

        localctx = AxisParser.TupleContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_tuple)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 219
            self.match(AxisParser.T__5)
            self.state = 228
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                self.state = 220
                self.tupleElement()
                self.state = 225
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,23,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 221
                        self.match(AxisParser.T__6)
                        self.state = 222
                        self.tupleElement() 
                    self.state = 227
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,23,self._ctx)



            self.state = 231
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 230
                self.match(AxisParser.T__6)


            self.state = 233
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTupleElementSingle" ):
                return visitor.visitTupleElementSingle(self)
            else:
                return visitor.visitChildren(self)


    class TupleElementBoundedAssignationContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementBoundedAssignation" ):
                listener.enterTupleElementBoundedAssignation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementBoundedAssignation" ):
                listener.exitTupleElementBoundedAssignation(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTupleElementBoundedAssignation" ):
                return visitor.visitTupleElementBoundedAssignation(self)
            else:
                return visitor.visitChildren(self)


    class TupleElementAssignationContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementAssignation" ):
                listener.enterTupleElementAssignation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementAssignation" ):
                listener.exitTupleElementAssignation(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTupleElementAssignation" ):
                return visitor.visitTupleElementAssignation(self)
            else:
                return visitor.visitChildren(self)


    class TupleElementBoundedContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTupleElementBounded" ):
                listener.enterTupleElementBounded(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTupleElementBounded" ):
                listener.exitTupleElementBounded(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTupleElementBounded" ):
                return visitor.visitTupleElementBounded(self)
            else:
                return visitor.visitChildren(self)



    def tupleElement(self):

        localctx = AxisParser.TupleElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_tupleElement)
        try:
            self.state = 250
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
            if la_ == 1:
                localctx = AxisParser.TupleElementSingleContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 235
                self.expression()
                pass

            elif la_ == 2:
                localctx = AxisParser.TupleElementAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 236
                self.expression()
                self.state = 237
                self.match(AxisParser.T__3)
                self.state = 238
                self.expression()
                pass

            elif la_ == 3:
                localctx = AxisParser.TupleElementBoundedContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 240
                self.expression()
                self.state = 241
                self.match(AxisParser.T__2)
                self.state = 242
                self.expression()
                pass

            elif la_ == 4:
                localctx = AxisParser.TupleElementBoundedAssignationContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 244
                self.expression()
                self.state = 245
                self.match(AxisParser.T__2)
                self.state = 246
                self.expression()
                self.state = 247
                self.match(AxisParser.T__3)
                self.state = 248
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBasicSuite" ):
                return visitor.visitBasicSuite(self)
            else:
                return visitor.visitChildren(self)


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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLambdaSuite" ):
                return visitor.visitLambdaSuite(self)
            else:
                return visitor.visitChildren(self)



    def lambda_(self):

        localctx = AxisParser.LambdaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_lambda)
        self._la = 0 # Token type
        try:
            self.state = 281
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                localctx = AxisParser.LambdaSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 252
                self.match(AxisParser.T__13)
                self.state = 254
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==16:
                    self.state = 253
                    self.lambdaParams()


                self.state = 256
                self.match(AxisParser.ARROW)
                self.state = 260
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 257
                    self.statement()
                    self.state = 262
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 264
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                    self.state = 263
                    self.expression()


                self.state = 266
                self.match(AxisParser.T__14)
                pass

            elif la_ == 2:
                localctx = AxisParser.BasicSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 267
                self.match(AxisParser.T__13)
                self.state = 271
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 268
                    self.statement()
                    self.state = 273
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 275
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 487488) != 0):
                    self.state = 274
                    self.expression()


                self.state = 278
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==5:
                    self.state = 277
                    self.semicolon()


                self.state = 280
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSemicolon" ):
                return visitor.visitSemicolon(self)
            else:
                return visitor.visitChildren(self)




    def semicolon(self):

        localctx = AxisParser.SemicolonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_semicolon)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 283
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLambdaParams" ):
                return visitor.visitLambdaParams(self)
            else:
                return visitor.visitChildren(self)




    def lambdaParams(self):

        localctx = AxisParser.LambdaParamsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_lambdaParams)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 285
            self.lambdaParam()
            self.state = 290
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,34,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 286
                    self.match(AxisParser.T__6)
                    self.state = 287
                    self.lambdaParam() 
                self.state = 292
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,34,self._ctx)

            self.state = 294
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==7:
                self.state = 293
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLambdaParam" ):
                return visitor.visitLambdaParam(self)
            else:
                return visitor.visitChildren(self)




    def lambdaParam(self):

        localctx = AxisParser.LambdaParamContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_lambdaParam)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 296
            self.identifier()
            self.state = 299
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 297
                self.match(AxisParser.T__2)
                self.state = 298
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


        def getRuleIndex(self):
            return AxisParser.RULE_argument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgument" ):
                listener.enterArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgument" ):
                listener.exitArgument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgument" ):
                return visitor.visitArgument(self)
            else:
                return visitor.visitChildren(self)




    def argument(self):

        localctx = AxisParser.ArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_argument)
        try:
            self.state = 306
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,37,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 301
                self.expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 302
                self.identifier()
                self.state = 303
                self.match(AxisParser.T__2)
                self.state = 304
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier" ):
                return visitor.visitIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def identifier(self):

        localctx = AxisParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 308
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = AxisParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_literal)
        try:
            self.state = 312
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [17]:
                self.enterOuterAlt(localctx, 1)
                self.state = 310
                self.decimal()
                pass
            elif token in [18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 311
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitText" ):
                return visitor.visitText(self)
            else:
                return visitor.visitChildren(self)




    def text(self):

        localctx = AxisParser.TextContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_text)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 314
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDecimal" ):
                return visitor.visitDecimal(self)
            else:
                return visitor.visitChildren(self)




    def decimal(self):

        localctx = AxisParser.DecimalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_decimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 316
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
        self._predicates[15] = self.postfix_sempred
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
         




