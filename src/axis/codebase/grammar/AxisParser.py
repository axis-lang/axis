# Generated from src/axislang/grammar/Axis.g4 by ANTLR 4.13.2
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
        4,1,33,286,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,1,0,5,0,58,8,0,10,0,12,0,61,9,0,1,0,1,0,1,1,1,1,1,2,1,
        2,1,2,1,2,3,2,71,8,2,1,2,1,2,3,2,75,8,2,1,2,3,2,78,8,2,1,3,1,3,3,
        3,82,8,3,1,4,1,4,1,4,1,4,5,4,88,8,4,10,4,12,4,91,9,4,3,4,93,8,4,
        1,4,1,4,1,5,1,5,1,5,1,5,1,5,3,5,102,8,5,1,6,1,6,1,7,1,7,5,7,108,
        8,7,10,7,12,7,111,9,7,1,8,1,8,1,8,5,8,116,8,8,10,8,12,8,119,9,8,
        1,9,1,9,1,9,5,9,124,8,9,10,9,12,9,127,9,9,1,10,1,10,1,10,5,10,132,
        8,10,10,10,12,10,135,9,10,1,11,1,11,1,11,5,11,140,8,11,10,11,12,
        11,143,9,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,5,12,157,8,12,10,12,12,12,160,9,12,3,12,162,8,12,1,12,1,
        12,1,12,1,12,4,12,168,8,12,11,12,12,12,169,5,12,172,8,12,10,12,12,
        12,175,9,12,1,13,1,13,1,13,1,13,3,13,181,8,13,1,14,1,14,1,15,1,15,
        1,16,1,16,1,16,1,17,1,17,1,17,1,17,5,17,194,8,17,10,17,12,17,197,
        9,17,3,17,199,8,17,1,17,3,17,202,8,17,1,17,1,17,1,18,1,18,1,18,1,
        18,1,18,1,18,1,18,1,18,1,18,1,18,1,18,1,18,3,18,218,8,18,1,19,1,
        19,3,19,222,8,19,1,19,1,19,5,19,226,8,19,10,19,12,19,229,9,19,1,
        19,3,19,232,8,19,1,19,1,19,1,19,5,19,237,8,19,10,19,12,19,240,9,
        19,1,19,3,19,243,8,19,1,19,3,19,246,8,19,1,19,3,19,249,8,19,1,20,
        1,20,1,21,1,21,1,21,5,21,256,8,21,10,21,12,21,259,9,21,1,21,3,21,
        262,8,21,1,22,1,22,1,22,3,22,267,8,22,1,23,1,23,1,23,1,23,1,23,3,
        23,274,8,23,1,24,1,24,1,25,1,25,3,25,280,8,25,1,26,1,26,1,27,1,27,
        1,27,0,1,24,28,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,
        36,38,40,42,44,46,48,50,52,54,0,4,1,0,29,30,1,0,23,28,1,0,18,19,
        1,0,20,22,298,0,59,1,0,0,0,2,64,1,0,0,0,4,66,1,0,0,0,6,81,1,0,0,
        0,8,83,1,0,0,0,10,101,1,0,0,0,12,103,1,0,0,0,14,105,1,0,0,0,16,112,
        1,0,0,0,18,120,1,0,0,0,20,128,1,0,0,0,22,136,1,0,0,0,24,144,1,0,
        0,0,26,180,1,0,0,0,28,182,1,0,0,0,30,184,1,0,0,0,32,186,1,0,0,0,
        34,189,1,0,0,0,36,217,1,0,0,0,38,248,1,0,0,0,40,250,1,0,0,0,42,252,
        1,0,0,0,44,263,1,0,0,0,46,273,1,0,0,0,48,275,1,0,0,0,50,279,1,0,
        0,0,52,281,1,0,0,0,54,283,1,0,0,0,56,58,3,2,1,0,57,56,1,0,0,0,58,
        61,1,0,0,0,59,57,1,0,0,0,59,60,1,0,0,0,60,62,1,0,0,0,61,59,1,0,0,
        0,62,63,5,0,0,1,63,1,1,0,0,0,64,65,3,4,2,0,65,3,1,0,0,0,66,67,5,
        1,0,0,67,70,3,6,3,0,68,69,5,2,0,0,69,71,3,12,6,0,70,68,1,0,0,0,70,
        71,1,0,0,0,71,74,1,0,0,0,72,73,5,3,0,0,73,75,3,12,6,0,74,72,1,0,
        0,0,74,75,1,0,0,0,75,77,1,0,0,0,76,78,5,4,0,0,77,76,1,0,0,0,77,78,
        1,0,0,0,78,5,1,0,0,0,79,82,3,48,24,0,80,82,3,8,4,0,81,79,1,0,0,0,
        81,80,1,0,0,0,82,7,1,0,0,0,83,92,5,5,0,0,84,89,3,10,5,0,85,86,5,
        6,0,0,86,88,3,10,5,0,87,85,1,0,0,0,88,91,1,0,0,0,89,87,1,0,0,0,89,
        90,1,0,0,0,90,93,1,0,0,0,91,89,1,0,0,0,92,84,1,0,0,0,92,93,1,0,0,
        0,93,94,1,0,0,0,94,95,5,7,0,0,95,9,1,0,0,0,96,102,3,48,24,0,97,98,
        3,48,24,0,98,99,5,2,0,0,99,100,3,48,24,0,100,102,1,0,0,0,101,96,
        1,0,0,0,101,97,1,0,0,0,102,11,1,0,0,0,103,104,3,14,7,0,104,13,1,
        0,0,0,105,109,3,16,8,0,106,108,3,16,8,0,107,106,1,0,0,0,108,111,
        1,0,0,0,109,107,1,0,0,0,109,110,1,0,0,0,110,15,1,0,0,0,111,109,1,
        0,0,0,112,117,3,18,9,0,113,114,7,0,0,0,114,116,3,18,9,0,115,113,
        1,0,0,0,116,119,1,0,0,0,117,115,1,0,0,0,117,118,1,0,0,0,118,17,1,
        0,0,0,119,117,1,0,0,0,120,125,3,20,10,0,121,122,7,1,0,0,122,124,
        3,20,10,0,123,121,1,0,0,0,124,127,1,0,0,0,125,123,1,0,0,0,125,126,
        1,0,0,0,126,19,1,0,0,0,127,125,1,0,0,0,128,133,3,22,11,0,129,130,
        7,2,0,0,130,132,3,22,11,0,131,129,1,0,0,0,132,135,1,0,0,0,133,131,
        1,0,0,0,133,134,1,0,0,0,134,21,1,0,0,0,135,133,1,0,0,0,136,141,3,
        24,12,0,137,138,7,3,0,0,138,140,3,24,12,0,139,137,1,0,0,0,140,143,
        1,0,0,0,141,139,1,0,0,0,141,142,1,0,0,0,142,23,1,0,0,0,143,141,1,
        0,0,0,144,145,6,12,-1,0,145,146,3,26,13,0,146,173,1,0,0,0,147,148,
        10,4,0,0,148,172,3,38,19,0,149,150,10,3,0,0,150,172,3,34,17,0,151,
        152,10,2,0,0,152,161,5,8,0,0,153,158,3,12,6,0,154,155,5,6,0,0,155,
        157,3,12,6,0,156,154,1,0,0,0,157,160,1,0,0,0,158,156,1,0,0,0,158,
        159,1,0,0,0,159,162,1,0,0,0,160,158,1,0,0,0,161,153,1,0,0,0,161,
        162,1,0,0,0,162,163,1,0,0,0,163,172,5,9,0,0,164,167,10,1,0,0,165,
        166,5,10,0,0,166,168,3,48,24,0,167,165,1,0,0,0,168,169,1,0,0,0,169,
        167,1,0,0,0,169,170,1,0,0,0,170,172,1,0,0,0,171,147,1,0,0,0,171,
        149,1,0,0,0,171,151,1,0,0,0,171,164,1,0,0,0,172,175,1,0,0,0,173,
        171,1,0,0,0,173,174,1,0,0,0,174,25,1,0,0,0,175,173,1,0,0,0,176,181,
        3,48,24,0,177,181,3,50,25,0,178,181,3,34,17,0,179,181,3,38,19,0,
        180,176,1,0,0,0,180,177,1,0,0,0,180,178,1,0,0,0,180,179,1,0,0,0,
        181,27,1,0,0,0,182,183,5,11,0,0,183,29,1,0,0,0,184,185,5,12,0,0,
        185,31,1,0,0,0,186,187,5,12,0,0,187,188,3,12,6,0,188,33,1,0,0,0,
        189,198,5,5,0,0,190,195,3,36,18,0,191,192,5,6,0,0,192,194,3,36,18,
        0,193,191,1,0,0,0,194,197,1,0,0,0,195,193,1,0,0,0,195,196,1,0,0,
        0,196,199,1,0,0,0,197,195,1,0,0,0,198,190,1,0,0,0,198,199,1,0,0,
        0,199,201,1,0,0,0,200,202,5,6,0,0,201,200,1,0,0,0,201,202,1,0,0,
        0,202,203,1,0,0,0,203,204,5,7,0,0,204,35,1,0,0,0,205,218,3,12,6,
        0,206,207,5,15,0,0,207,208,5,3,0,0,208,218,3,12,6,0,209,210,5,13,
        0,0,210,211,3,12,6,0,211,212,5,14,0,0,212,213,5,3,0,0,213,214,3,
        12,6,0,214,218,1,0,0,0,215,216,5,12,0,0,216,218,3,12,6,0,217,205,
        1,0,0,0,217,206,1,0,0,0,217,209,1,0,0,0,217,215,1,0,0,0,218,37,1,
        0,0,0,219,221,5,13,0,0,220,222,3,42,21,0,221,220,1,0,0,0,221,222,
        1,0,0,0,222,223,1,0,0,0,223,227,5,31,0,0,224,226,3,2,1,0,225,224,
        1,0,0,0,226,229,1,0,0,0,227,225,1,0,0,0,227,228,1,0,0,0,228,231,
        1,0,0,0,229,227,1,0,0,0,230,232,3,12,6,0,231,230,1,0,0,0,231,232,
        1,0,0,0,232,233,1,0,0,0,233,249,5,14,0,0,234,238,5,13,0,0,235,237,
        3,2,1,0,236,235,1,0,0,0,237,240,1,0,0,0,238,236,1,0,0,0,238,239,
        1,0,0,0,239,242,1,0,0,0,240,238,1,0,0,0,241,243,3,12,6,0,242,241,
        1,0,0,0,242,243,1,0,0,0,243,245,1,0,0,0,244,246,3,40,20,0,245,244,
        1,0,0,0,245,246,1,0,0,0,246,247,1,0,0,0,247,249,5,14,0,0,248,219,
        1,0,0,0,248,234,1,0,0,0,249,39,1,0,0,0,250,251,5,4,0,0,251,41,1,
        0,0,0,252,257,3,44,22,0,253,254,5,6,0,0,254,256,3,44,22,0,255,253,
        1,0,0,0,256,259,1,0,0,0,257,255,1,0,0,0,257,258,1,0,0,0,258,261,
        1,0,0,0,259,257,1,0,0,0,260,262,5,6,0,0,261,260,1,0,0,0,261,262,
        1,0,0,0,262,43,1,0,0,0,263,266,3,48,24,0,264,265,5,2,0,0,265,267,
        3,12,6,0,266,264,1,0,0,0,266,267,1,0,0,0,267,45,1,0,0,0,268,274,
        3,12,6,0,269,270,3,48,24,0,270,271,5,2,0,0,271,272,3,12,6,0,272,
        274,1,0,0,0,273,268,1,0,0,0,273,269,1,0,0,0,274,47,1,0,0,0,275,276,
        5,15,0,0,276,49,1,0,0,0,277,280,3,54,27,0,278,280,3,52,26,0,279,
        277,1,0,0,0,279,278,1,0,0,0,280,51,1,0,0,0,281,282,5,17,0,0,282,
        53,1,0,0,0,283,284,5,16,0,0,284,55,1,0,0,0,35,59,70,74,77,81,89,
        92,101,109,117,125,133,141,158,161,169,171,173,180,195,198,201,217,
        221,227,231,238,242,245,248,257,261,266,273,279
    ]

class AxisParser ( Parser ):

    grammarFileName = "Axis.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'val'", "':'", "'='", "';'", "'('", "','", 
                     "')'", "'['", "']'", "'.'", "'_'", "'..'", "'{'", "'}'", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "'+'", "'-'", 
                     "'*'", "'/'", "'%'", "'=='", "'!='", "'<'", "'<='", 
                     "'>'", "'>='", "'&&'", "'||'", "'->'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "ID", "DECIMAL", 
                      "TEXT", "ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "NE", 
                      "LT", "LE", "GT", "GE", "AND", "OR", "ARROW", "WS", 
                      "COMMENT" ]

    RULE_file = 0
    RULE_statement = 1
    RULE_valStatement = 2
    RULE_pattern = 3
    RULE_tuplePattern = 4
    RULE_tuplePatternElement = 5
    RULE_expression = 6
    RULE_juxtapositionExpr = 7
    RULE_logicalExpr = 8
    RULE_comparisonExpr = 9
    RULE_addition = 10
    RULE_product = 11
    RULE_postfix = 12
    RULE_primaryExpr = 13
    RULE_wildcard = 14
    RULE_spread = 15
    RULE_range = 16
    RULE_tuple = 17
    RULE_tupleElement = 18
    RULE_suite = 19
    RULE_semicolon = 20
    RULE_lambdaParams = 21
    RULE_lambdaParam = 22
    RULE_argument = 23
    RULE_identifier = 24
    RULE_literal = 25
    RULE_text = 26
    RULE_decimal = 27

    ruleNames =  [ "file", "statement", "valStatement", "pattern", "tuplePattern", 
                   "tuplePatternElement", "expression", "juxtapositionExpr", 
                   "logicalExpr", "comparisonExpr", "addition", "product", 
                   "postfix", "primaryExpr", "wildcard", "spread", "range", 
                   "tuple", "tupleElement", "suite", "semicolon", "lambdaParams", 
                   "lambdaParam", "argument", "identifier", "literal", "text", 
                   "decimal" ]

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
    ID=15
    DECIMAL=16
    TEXT=17
    ADD=18
    SUB=19
    MUL=20
    DIV=21
    MOD=22
    EQ=23
    NE=24
    LT=25
    LE=26
    GT=27
    GE=28
    AND=29
    OR=30
    ARROW=31
    WS=32
    COMMENT=33

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class FileContext(ParserRuleContext):
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
            return AxisParser.RULE_file

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFile" ):
                listener.enterFile(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFile" ):
                listener.exitFile(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFile" ):
                return visitor.visitFile(self)
            else:
                return visitor.visitChildren(self)




    def file_(self):

        localctx = AxisParser.FileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_file)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 56
                self.statement()
                self.state = 61
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 62
            self.match(AxisParser.EOF)
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
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
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
        self.enterRule(localctx, 4, self.RULE_valStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(AxisParser.T__0)

            self.state = 67
            self.pattern()
            self.state = 70
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 68
                self.match(AxisParser.T__1)
                self.state = 69
                self.expression()


            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 72
                self.match(AxisParser.T__2)
                self.state = 73
                self.expression()


            self.state = 77
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.state = 76
                self.match(AxisParser.T__3)


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
        self.enterRule(localctx, 6, self.RULE_pattern)
        try:
            self.state = 81
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [15]:
                self.enterOuterAlt(localctx, 1)
                self.state = 79
                self.identifier()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 2)
                self.state = 80
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
        self.enterRule(localctx, 8, self.RULE_tuplePattern)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(AxisParser.T__4)
            self.state = 92
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==15:
                self.state = 84
                self.tuplePatternElement()
                self.state = 89
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==6:
                    self.state = 85
                    self.match(AxisParser.T__5)
                    self.state = 86
                    self.tuplePatternElement()
                    self.state = 91
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)



            self.state = 94
            self.match(AxisParser.T__6)
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
        self.enterRule(localctx, 10, self.RULE_tuplePatternElement)
        try:
            self.state = 101
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 96
                self.identifier()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 97
                self.identifier()
                self.state = 98
                self.match(AxisParser.T__1)
                self.state = 99
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)




    def expression(self):

        localctx = AxisParser.ExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
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

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJuxtapositionExpr" ):
                return visitor.visitJuxtapositionExpr(self)
            else:
                return visitor.visitChildren(self)




    def juxtapositionExpr(self):

        localctx = AxisParser.JuxtapositionExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_juxtapositionExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.logicalExpr()
            self.state = 109
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 106
                    self.logicalExpr() 
                self.state = 111
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

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
        self.enterRule(localctx, 16, self.RULE_logicalExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 112
            self.comparisonExpr()
            self.state = 117
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==29 or _la==30:
                self.state = 113
                _la = self._input.LA(1)
                if not(_la==29 or _la==30):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 114
                self.comparisonExpr()
                self.state = 119
                self._errHandler.sync(self)
                _la = self._input.LA(1)

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
        self.enterRule(localctx, 18, self.RULE_comparisonExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 120
            self.addition()
            self.state = 125
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 528482304) != 0):
                self.state = 121
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 528482304) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 122
                self.addition()
                self.state = 127
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
        self.enterRule(localctx, 20, self.RULE_addition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 128
            self.product()
            self.state = 133
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==18 or _la==19:
                self.state = 129
                _la = self._input.LA(1)
                if not(_la==18 or _la==19):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 130
                self.product()
                self.state = 135
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
        self.enterRule(localctx, 22, self.RULE_product)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 136
            self.postfix(0)
            self.state = 141
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 7340032) != 0):
                self.state = 137
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 7340032) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 138
                self.postfix(0)
                self.state = 143
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

        def suite(self):
            return self.getTypedRuleContext(AxisParser.SuiteContext,0)


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
        _startState = 24
        self.enterRecursionRule(localctx, 24, self.RULE_postfix, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            localctx = AxisParser.PassContext(self, localctx)
            self._ctx = localctx
            _prevctx = localctx

            self.state = 145
            self.primaryExpr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 173
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,17,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 171
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
                    if la_ == 1:
                        localctx = AxisParser.TrailingCallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 147
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 148
                        self.suite()
                        pass

                    elif la_ == 2:
                        localctx = AxisParser.CallContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 149
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 150
                        self.tuple_()
                        pass

                    elif la_ == 3:
                        localctx = AxisParser.IndexingContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 151
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 152
                        self.match(AxisParser.T__7)
                        self.state = 161
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if (((_la) & ~0x3f) == 0 and ((1 << _la) & 237600) != 0):
                            self.state = 153
                            self.expression()
                            self.state = 158
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)
                            while _la==6:
                                self.state = 154
                                self.match(AxisParser.T__5)
                                self.state = 155
                                self.expression()
                                self.state = 160
                                self._errHandler.sync(self)
                                _la = self._input.LA(1)



                        self.state = 163
                        self.match(AxisParser.T__8)
                        pass

                    elif la_ == 4:
                        localctx = AxisParser.MemberAccessContext(self, AxisParser.PostfixContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_postfix)
                        self.state = 164
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 167 
                        self._errHandler.sync(self)
                        _alt = 1
                        while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                            if _alt == 1:
                                self.state = 165
                                self.match(AxisParser.T__9)
                                self.state = 166
                                self.identifier()

                            else:
                                raise NoViableAltException(self)
                            self.state = 169 
                            self._errHandler.sync(self)
                            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

                        pass

             
                self.state = 175
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,17,self._ctx)

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


        def suite(self):
            return self.getTypedRuleContext(AxisParser.SuiteContext,0)


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
        self.enterRule(localctx, 26, self.RULE_primaryExpr)
        try:
            self.state = 180
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [15]:
                self.enterOuterAlt(localctx, 1)
                self.state = 176
                self.identifier()
                pass
            elif token in [16, 17]:
                self.enterOuterAlt(localctx, 2)
                self.state = 177
                self.literal()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 3)
                self.state = 178
                self.tuple_()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 4)
                self.state = 179
                self.suite()
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
        self.enterRule(localctx, 28, self.RULE_wildcard)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            self.match(AxisParser.T__10)
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
        self.enterRule(localctx, 30, self.RULE_spread)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 184
            self.match(AxisParser.T__11)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RangeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def getRuleIndex(self):
            return AxisParser.RULE_range

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRange" ):
                listener.enterRange(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRange" ):
                listener.exitRange(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRange" ):
                return visitor.visitRange(self)
            else:
                return visitor.visitChildren(self)




    def range_(self):

        localctx = AxisParser.RangeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_range)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 186
            self.match(AxisParser.T__11)
            self.state = 187
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
        self.enterRule(localctx, 34, self.RULE_tuple)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self.match(AxisParser.T__4)
            self.state = 198
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 241696) != 0):
                self.state = 190
                self.tupleElement()
                self.state = 195
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,19,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 191
                        self.match(AxisParser.T__5)
                        self.state = 192
                        self.tupleElement() 
                    self.state = 197
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,19,self._ctx)



            self.state = 201
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 200
                self.match(AxisParser.T__5)


            self.state = 203
            self.match(AxisParser.T__6)
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



    class UnnamedTupleElementContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnnamedTupleElement" ):
                listener.enterUnnamedTupleElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnnamedTupleElement" ):
                listener.exitUnnamedTupleElement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnnamedTupleElement" ):
                return visitor.visitUnnamedTupleElement(self)
            else:
                return visitor.visitChildren(self)


    class NamedTupleElementContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ID(self):
            return self.getToken(AxisParser.ID, 0)
        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNamedTupleElement" ):
                listener.enterNamedTupleElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNamedTupleElement" ):
                listener.exitNamedTupleElement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNamedTupleElement" ):
                return visitor.visitNamedTupleElement(self)
            else:
                return visitor.visitChildren(self)


    class DynamicTupleElementContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(AxisParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(AxisParser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDynamicTupleElement" ):
                listener.enterDynamicTupleElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDynamicTupleElement" ):
                listener.exitDynamicTupleElement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDynamicTupleElement" ):
                return visitor.visitDynamicTupleElement(self)
            else:
                return visitor.visitChildren(self)


    class SpreadTupleElementContext(TupleElementContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.TupleElementContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(AxisParser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSpreadTupleElement" ):
                listener.enterSpreadTupleElement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSpreadTupleElement" ):
                listener.exitSpreadTupleElement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSpreadTupleElement" ):
                return visitor.visitSpreadTupleElement(self)
            else:
                return visitor.visitChildren(self)



    def tupleElement(self):

        localctx = AxisParser.TupleElementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_tupleElement)
        try:
            self.state = 217
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
            if la_ == 1:
                localctx = AxisParser.UnnamedTupleElementContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 205
                self.expression()
                pass

            elif la_ == 2:
                localctx = AxisParser.NamedTupleElementContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 206
                self.match(AxisParser.ID)
                self.state = 207
                self.match(AxisParser.T__2)
                self.state = 208
                self.expression()
                pass

            elif la_ == 3:
                localctx = AxisParser.DynamicTupleElementContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 209
                self.match(AxisParser.T__12)
                self.state = 210
                self.expression()
                self.state = 211
                self.match(AxisParser.T__13)
                self.state = 212
                self.match(AxisParser.T__2)
                self.state = 213
                self.expression()
                pass

            elif la_ == 4:
                localctx = AxisParser.SpreadTupleElementContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 215
                self.match(AxisParser.T__11)
                self.state = 216
                self.expression()
                pass


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


        def getRuleIndex(self):
            return AxisParser.RULE_suite

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class BasicSuiteContext(SuiteContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.SuiteContext
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


    class LambdaSuiteContext(SuiteContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a AxisParser.SuiteContext
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



    def suite(self):

        localctx = AxisParser.SuiteContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_suite)
        self._la = 0 # Token type
        try:
            self.state = 248
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                localctx = AxisParser.LambdaSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 219
                self.match(AxisParser.T__12)
                self.state = 221
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==15:
                    self.state = 220
                    self.lambdaParams()


                self.state = 223
                self.match(AxisParser.ARROW)
                self.state = 227
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1:
                    self.state = 224
                    self.statement()
                    self.state = 229
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 231
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 237600) != 0):
                    self.state = 230
                    self.expression()


                self.state = 233
                self.match(AxisParser.T__13)
                pass

            elif la_ == 2:
                localctx = AxisParser.BasicSuiteContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 234
                self.match(AxisParser.T__12)
                self.state = 238
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==1:
                    self.state = 235
                    self.statement()
                    self.state = 240
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 242
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 237600) != 0):
                    self.state = 241
                    self.expression()


                self.state = 245
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==4:
                    self.state = 244
                    self.semicolon()


                self.state = 247
                self.match(AxisParser.T__13)
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
        self.enterRule(localctx, 40, self.RULE_semicolon)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 250
            self.match(AxisParser.T__3)
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
        self.enterRule(localctx, 42, self.RULE_lambdaParams)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 252
            self.lambdaParam()
            self.state = 257
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,30,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 253
                    self.match(AxisParser.T__5)
                    self.state = 254
                    self.lambdaParam() 
                self.state = 259
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,30,self._ctx)

            self.state = 261
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 260
                self.match(AxisParser.T__5)


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
        self.enterRule(localctx, 44, self.RULE_lambdaParam)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 263
            self.identifier()
            self.state = 266
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 264
                self.match(AxisParser.T__1)
                self.state = 265
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
        self.enterRule(localctx, 46, self.RULE_argument)
        try:
            self.state = 273
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,33,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 268
                self.expression()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 269
                self.identifier()
                self.state = 270
                self.match(AxisParser.T__1)
                self.state = 271
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
        self.enterRule(localctx, 48, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 275
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
        self.enterRule(localctx, 50, self.RULE_literal)
        try:
            self.state = 279
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 277
                self.decimal()
                pass
            elif token in [17]:
                self.enterOuterAlt(localctx, 2)
                self.state = 278
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
        self.enterRule(localctx, 52, self.RULE_text)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 281
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
        self.enterRule(localctx, 54, self.RULE_decimal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 283
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
        self._predicates[12] = self.postfix_sempred
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
         




