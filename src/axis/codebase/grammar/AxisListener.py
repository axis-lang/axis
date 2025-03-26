# Generated from src/axislang/grammar/Axis.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .AxisParser import AxisParser
else:
    from AxisParser import AxisParser

# This class defines a complete listener for a parse tree produced by AxisParser.
class AxisListener(ParseTreeListener):

    # Enter a parse tree produced by AxisParser#file.
    def enterFile(self, ctx:AxisParser.FileContext):
        pass

    # Exit a parse tree produced by AxisParser#file.
    def exitFile(self, ctx:AxisParser.FileContext):
        pass


    # Enter a parse tree produced by AxisParser#statement.
    def enterStatement(self, ctx:AxisParser.StatementContext):
        pass

    # Exit a parse tree produced by AxisParser#statement.
    def exitStatement(self, ctx:AxisParser.StatementContext):
        pass


    # Enter a parse tree produced by AxisParser#valStatement.
    def enterValStatement(self, ctx:AxisParser.ValStatementContext):
        pass

    # Exit a parse tree produced by AxisParser#valStatement.
    def exitValStatement(self, ctx:AxisParser.ValStatementContext):
        pass


    # Enter a parse tree produced by AxisParser#pattern.
    def enterPattern(self, ctx:AxisParser.PatternContext):
        pass

    # Exit a parse tree produced by AxisParser#pattern.
    def exitPattern(self, ctx:AxisParser.PatternContext):
        pass


    # Enter a parse tree produced by AxisParser#tuplePattern.
    def enterTuplePattern(self, ctx:AxisParser.TuplePatternContext):
        pass

    # Exit a parse tree produced by AxisParser#tuplePattern.
    def exitTuplePattern(self, ctx:AxisParser.TuplePatternContext):
        pass


    # Enter a parse tree produced by AxisParser#tuplePatternElement.
    def enterTuplePatternElement(self, ctx:AxisParser.TuplePatternElementContext):
        pass

    # Exit a parse tree produced by AxisParser#tuplePatternElement.
    def exitTuplePatternElement(self, ctx:AxisParser.TuplePatternElementContext):
        pass


    # Enter a parse tree produced by AxisParser#expression.
    def enterExpression(self, ctx:AxisParser.ExpressionContext):
        pass

    # Exit a parse tree produced by AxisParser#expression.
    def exitExpression(self, ctx:AxisParser.ExpressionContext):
        pass


    # Enter a parse tree produced by AxisParser#juxtapositionExpr.
    def enterJuxtapositionExpr(self, ctx:AxisParser.JuxtapositionExprContext):
        pass

    # Exit a parse tree produced by AxisParser#juxtapositionExpr.
    def exitJuxtapositionExpr(self, ctx:AxisParser.JuxtapositionExprContext):
        pass


    # Enter a parse tree produced by AxisParser#logicalExpr.
    def enterLogicalExpr(self, ctx:AxisParser.LogicalExprContext):
        pass

    # Exit a parse tree produced by AxisParser#logicalExpr.
    def exitLogicalExpr(self, ctx:AxisParser.LogicalExprContext):
        pass


    # Enter a parse tree produced by AxisParser#comparisonExpr.
    def enterComparisonExpr(self, ctx:AxisParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by AxisParser#comparisonExpr.
    def exitComparisonExpr(self, ctx:AxisParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by AxisParser#addition.
    def enterAddition(self, ctx:AxisParser.AdditionContext):
        pass

    # Exit a parse tree produced by AxisParser#addition.
    def exitAddition(self, ctx:AxisParser.AdditionContext):
        pass


    # Enter a parse tree produced by AxisParser#product.
    def enterProduct(self, ctx:AxisParser.ProductContext):
        pass

    # Exit a parse tree produced by AxisParser#product.
    def exitProduct(self, ctx:AxisParser.ProductContext):
        pass


    # Enter a parse tree produced by AxisParser#Call.
    def enterCall(self, ctx:AxisParser.CallContext):
        pass

    # Exit a parse tree produced by AxisParser#Call.
    def exitCall(self, ctx:AxisParser.CallContext):
        pass


    # Enter a parse tree produced by AxisParser#Pass.
    def enterPass(self, ctx:AxisParser.PassContext):
        pass

    # Exit a parse tree produced by AxisParser#Pass.
    def exitPass(self, ctx:AxisParser.PassContext):
        pass


    # Enter a parse tree produced by AxisParser#MemberAccess.
    def enterMemberAccess(self, ctx:AxisParser.MemberAccessContext):
        pass

    # Exit a parse tree produced by AxisParser#MemberAccess.
    def exitMemberAccess(self, ctx:AxisParser.MemberAccessContext):
        pass


    # Enter a parse tree produced by AxisParser#TrailingCall.
    def enterTrailingCall(self, ctx:AxisParser.TrailingCallContext):
        pass

    # Exit a parse tree produced by AxisParser#TrailingCall.
    def exitTrailingCall(self, ctx:AxisParser.TrailingCallContext):
        pass


    # Enter a parse tree produced by AxisParser#Indexing.
    def enterIndexing(self, ctx:AxisParser.IndexingContext):
        pass

    # Exit a parse tree produced by AxisParser#Indexing.
    def exitIndexing(self, ctx:AxisParser.IndexingContext):
        pass


    # Enter a parse tree produced by AxisParser#primaryExpr.
    def enterPrimaryExpr(self, ctx:AxisParser.PrimaryExprContext):
        pass

    # Exit a parse tree produced by AxisParser#primaryExpr.
    def exitPrimaryExpr(self, ctx:AxisParser.PrimaryExprContext):
        pass


    # Enter a parse tree produced by AxisParser#wildcard.
    def enterWildcard(self, ctx:AxisParser.WildcardContext):
        pass

    # Exit a parse tree produced by AxisParser#wildcard.
    def exitWildcard(self, ctx:AxisParser.WildcardContext):
        pass


    # Enter a parse tree produced by AxisParser#spread.
    def enterSpread(self, ctx:AxisParser.SpreadContext):
        pass

    # Exit a parse tree produced by AxisParser#spread.
    def exitSpread(self, ctx:AxisParser.SpreadContext):
        pass


    # Enter a parse tree produced by AxisParser#range.
    def enterRange(self, ctx:AxisParser.RangeContext):
        pass

    # Exit a parse tree produced by AxisParser#range.
    def exitRange(self, ctx:AxisParser.RangeContext):
        pass


    # Enter a parse tree produced by AxisParser#tuple.
    def enterTuple(self, ctx:AxisParser.TupleContext):
        pass

    # Exit a parse tree produced by AxisParser#tuple.
    def exitTuple(self, ctx:AxisParser.TupleContext):
        pass


    # Enter a parse tree produced by AxisParser#UnnamedTupleElement.
    def enterUnnamedTupleElement(self, ctx:AxisParser.UnnamedTupleElementContext):
        pass

    # Exit a parse tree produced by AxisParser#UnnamedTupleElement.
    def exitUnnamedTupleElement(self, ctx:AxisParser.UnnamedTupleElementContext):
        pass


    # Enter a parse tree produced by AxisParser#NamedTupleElement.
    def enterNamedTupleElement(self, ctx:AxisParser.NamedTupleElementContext):
        pass

    # Exit a parse tree produced by AxisParser#NamedTupleElement.
    def exitNamedTupleElement(self, ctx:AxisParser.NamedTupleElementContext):
        pass


    # Enter a parse tree produced by AxisParser#DynamicTupleElement.
    def enterDynamicTupleElement(self, ctx:AxisParser.DynamicTupleElementContext):
        pass

    # Exit a parse tree produced by AxisParser#DynamicTupleElement.
    def exitDynamicTupleElement(self, ctx:AxisParser.DynamicTupleElementContext):
        pass


    # Enter a parse tree produced by AxisParser#SpreadTupleElement.
    def enterSpreadTupleElement(self, ctx:AxisParser.SpreadTupleElementContext):
        pass

    # Exit a parse tree produced by AxisParser#SpreadTupleElement.
    def exitSpreadTupleElement(self, ctx:AxisParser.SpreadTupleElementContext):
        pass


    # Enter a parse tree produced by AxisParser#LambdaSuite.
    def enterLambdaSuite(self, ctx:AxisParser.LambdaSuiteContext):
        pass

    # Exit a parse tree produced by AxisParser#LambdaSuite.
    def exitLambdaSuite(self, ctx:AxisParser.LambdaSuiteContext):
        pass


    # Enter a parse tree produced by AxisParser#BasicSuite.
    def enterBasicSuite(self, ctx:AxisParser.BasicSuiteContext):
        pass

    # Exit a parse tree produced by AxisParser#BasicSuite.
    def exitBasicSuite(self, ctx:AxisParser.BasicSuiteContext):
        pass


    # Enter a parse tree produced by AxisParser#semicolon.
    def enterSemicolon(self, ctx:AxisParser.SemicolonContext):
        pass

    # Exit a parse tree produced by AxisParser#semicolon.
    def exitSemicolon(self, ctx:AxisParser.SemicolonContext):
        pass


    # Enter a parse tree produced by AxisParser#lambdaParams.
    def enterLambdaParams(self, ctx:AxisParser.LambdaParamsContext):
        pass

    # Exit a parse tree produced by AxisParser#lambdaParams.
    def exitLambdaParams(self, ctx:AxisParser.LambdaParamsContext):
        pass


    # Enter a parse tree produced by AxisParser#lambdaParam.
    def enterLambdaParam(self, ctx:AxisParser.LambdaParamContext):
        pass

    # Exit a parse tree produced by AxisParser#lambdaParam.
    def exitLambdaParam(self, ctx:AxisParser.LambdaParamContext):
        pass


    # Enter a parse tree produced by AxisParser#argument.
    def enterArgument(self, ctx:AxisParser.ArgumentContext):
        pass

    # Exit a parse tree produced by AxisParser#argument.
    def exitArgument(self, ctx:AxisParser.ArgumentContext):
        pass


    # Enter a parse tree produced by AxisParser#identifier.
    def enterIdentifier(self, ctx:AxisParser.IdentifierContext):
        pass

    # Exit a parse tree produced by AxisParser#identifier.
    def exitIdentifier(self, ctx:AxisParser.IdentifierContext):
        pass


    # Enter a parse tree produced by AxisParser#literal.
    def enterLiteral(self, ctx:AxisParser.LiteralContext):
        pass

    # Exit a parse tree produced by AxisParser#literal.
    def exitLiteral(self, ctx:AxisParser.LiteralContext):
        pass


    # Enter a parse tree produced by AxisParser#text.
    def enterText(self, ctx:AxisParser.TextContext):
        pass

    # Exit a parse tree produced by AxisParser#text.
    def exitText(self, ctx:AxisParser.TextContext):
        pass


    # Enter a parse tree produced by AxisParser#decimal.
    def enterDecimal(self, ctx:AxisParser.DecimalContext):
        pass

    # Exit a parse tree produced by AxisParser#decimal.
    def exitDecimal(self, ctx:AxisParser.DecimalContext):
        pass



del AxisParser