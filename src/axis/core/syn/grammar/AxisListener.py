# Generated from src/axis/core/syn/grammar/Axis.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .AxisParser import AxisParser
else:
    from AxisParser import AxisParser

# This class defines a complete listener for a parse tree produced by AxisParser.
class AxisListener(ParseTreeListener):

    # Enter a parse tree produced by AxisParser#unitItem.
    def enterUnitItem(self, ctx:AxisParser.UnitItemContext):
        pass

    # Exit a parse tree produced by AxisParser#unitItem.
    def exitUnitItem(self, ctx:AxisParser.UnitItemContext):
        pass


    # Enter a parse tree produced by AxisParser#modItem.
    def enterModItem(self, ctx:AxisParser.ModItemContext):
        pass

    # Exit a parse tree produced by AxisParser#modItem.
    def exitModItem(self, ctx:AxisParser.ModItemContext):
        pass


    # Enter a parse tree produced by AxisParser#defItem.
    def enterDefItem(self, ctx:AxisParser.DefItemContext):
        pass

    # Exit a parse tree produced by AxisParser#defItem.
    def exitDefItem(self, ctx:AxisParser.DefItemContext):
        pass


    # Enter a parse tree produced by AxisParser#valItem.
    def enterValItem(self, ctx:AxisParser.ValItemContext):
        pass

    # Exit a parse tree produced by AxisParser#valItem.
    def exitValItem(self, ctx:AxisParser.ValItemContext):
        pass


    # Enter a parse tree produced by AxisParser#useItem.
    def enterUseItem(self, ctx:AxisParser.UseItemContext):
        pass

    # Exit a parse tree produced by AxisParser#useItem.
    def exitUseItem(self, ctx:AxisParser.UseItemContext):
        pass


    # Enter a parse tree produced by AxisParser#takesBlock.
    def enterTakesBlock(self, ctx:AxisParser.TakesBlockContext):
        pass

    # Exit a parse tree produced by AxisParser#takesBlock.
    def exitTakesBlock(self, ctx:AxisParser.TakesBlockContext):
        pass


    # Enter a parse tree produced by AxisParser#whereBlock.
    def enterWhereBlock(self, ctx:AxisParser.WhereBlockContext):
        pass

    # Exit a parse tree produced by AxisParser#whereBlock.
    def exitWhereBlock(self, ctx:AxisParser.WhereBlockContext):
        pass


    # Enter a parse tree produced by AxisParser#returnsBlock.
    def enterReturnsBlock(self, ctx:AxisParser.ReturnsBlockContext):
        pass

    # Exit a parse tree produced by AxisParser#returnsBlock.
    def exitReturnsBlock(self, ctx:AxisParser.ReturnsBlockContext):
        pass


    # Enter a parse tree produced by AxisParser#suiteBlock.
    def enterSuiteBlock(self, ctx:AxisParser.SuiteBlockContext):
        pass

    # Exit a parse tree produced by AxisParser#suiteBlock.
    def exitSuiteBlock(self, ctx:AxisParser.SuiteBlockContext):
        pass


    # Enter a parse tree produced by AxisParser#suite.
    def enterSuite(self, ctx:AxisParser.SuiteContext):
        pass

    # Exit a parse tree produced by AxisParser#suite.
    def exitSuite(self, ctx:AxisParser.SuiteContext):
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


    # Enter a parse tree produced by AxisParser#juxtaposition.
    def enterJuxtaposition(self, ctx:AxisParser.JuxtapositionContext):
        pass

    # Exit a parse tree produced by AxisParser#juxtaposition.
    def exitJuxtaposition(self, ctx:AxisParser.JuxtapositionContext):
        pass


    # Enter a parse tree produced by AxisParser#range.
    def enterRange(self, ctx:AxisParser.RangeContext):
        pass

    # Exit a parse tree produced by AxisParser#range.
    def exitRange(self, ctx:AxisParser.RangeContext):
        pass


    # Enter a parse tree produced by AxisParser#logical.
    def enterLogical(self, ctx:AxisParser.LogicalContext):
        pass

    # Exit a parse tree produced by AxisParser#logical.
    def exitLogical(self, ctx:AxisParser.LogicalContext):
        pass


    # Enter a parse tree produced by AxisParser#logicalOp.
    def enterLogicalOp(self, ctx:AxisParser.LogicalOpContext):
        pass

    # Exit a parse tree produced by AxisParser#logicalOp.
    def exitLogicalOp(self, ctx:AxisParser.LogicalOpContext):
        pass


    # Enter a parse tree produced by AxisParser#comparison.
    def enterComparison(self, ctx:AxisParser.ComparisonContext):
        pass

    # Exit a parse tree produced by AxisParser#comparison.
    def exitComparison(self, ctx:AxisParser.ComparisonContext):
        pass


    # Enter a parse tree produced by AxisParser#comparisonOp.
    def enterComparisonOp(self, ctx:AxisParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by AxisParser#comparisonOp.
    def exitComparisonOp(self, ctx:AxisParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by AxisParser#addition.
    def enterAddition(self, ctx:AxisParser.AdditionContext):
        pass

    # Exit a parse tree produced by AxisParser#addition.
    def exitAddition(self, ctx:AxisParser.AdditionContext):
        pass


    # Enter a parse tree produced by AxisParser#additiveOp.
    def enterAdditiveOp(self, ctx:AxisParser.AdditiveOpContext):
        pass

    # Exit a parse tree produced by AxisParser#additiveOp.
    def exitAdditiveOp(self, ctx:AxisParser.AdditiveOpContext):
        pass


    # Enter a parse tree produced by AxisParser#product.
    def enterProduct(self, ctx:AxisParser.ProductContext):
        pass

    # Exit a parse tree produced by AxisParser#product.
    def exitProduct(self, ctx:AxisParser.ProductContext):
        pass


    # Enter a parse tree produced by AxisParser#productiveOp.
    def enterProductiveOp(self, ctx:AxisParser.ProductiveOpContext):
        pass

    # Exit a parse tree produced by AxisParser#productiveOp.
    def exitProductiveOp(self, ctx:AxisParser.ProductiveOpContext):
        pass


    # Enter a parse tree produced by AxisParser#PrefixPass.
    def enterPrefixPass(self, ctx:AxisParser.PrefixPassContext):
        pass

    # Exit a parse tree produced by AxisParser#PrefixPass.
    def exitPrefixPass(self, ctx:AxisParser.PrefixPassContext):
        pass


    # Enter a parse tree produced by AxisParser#Call.
    def enterCall(self, ctx:AxisParser.CallContext):
        pass

    # Exit a parse tree produced by AxisParser#Call.
    def exitCall(self, ctx:AxisParser.CallContext):
        pass


    # Enter a parse tree produced by AxisParser#MemberAccess.
    def enterMemberAccess(self, ctx:AxisParser.MemberAccessContext):
        pass

    # Exit a parse tree produced by AxisParser#MemberAccess.
    def exitMemberAccess(self, ctx:AxisParser.MemberAccessContext):
        pass


    # Enter a parse tree produced by AxisParser#TrailingLambda.
    def enterTrailingLambda(self, ctx:AxisParser.TrailingLambdaContext):
        pass

    # Exit a parse tree produced by AxisParser#TrailingLambda.
    def exitTrailingLambda(self, ctx:AxisParser.TrailingLambdaContext):
        pass


    # Enter a parse tree produced by AxisParser#ScopeAccess.
    def enterScopeAccess(self, ctx:AxisParser.ScopeAccessContext):
        pass

    # Exit a parse tree produced by AxisParser#ScopeAccess.
    def exitScopeAccess(self, ctx:AxisParser.ScopeAccessContext):
        pass


    # Enter a parse tree produced by AxisParser#PostfixPass.
    def enterPostfixPass(self, ctx:AxisParser.PostfixPassContext):
        pass

    # Exit a parse tree produced by AxisParser#PostfixPass.
    def exitPostfixPass(self, ctx:AxisParser.PostfixPassContext):
        pass


    # Enter a parse tree produced by AxisParser#Index.
    def enterIndex(self, ctx:AxisParser.IndexContext):
        pass

    # Exit a parse tree produced by AxisParser#Index.
    def exitIndex(self, ctx:AxisParser.IndexContext):
        pass


    # Enter a parse tree produced by AxisParser#primary.
    def enterPrimary(self, ctx:AxisParser.PrimaryContext):
        pass

    # Exit a parse tree produced by AxisParser#primary.
    def exitPrimary(self, ctx:AxisParser.PrimaryContext):
        pass


    # Enter a parse tree produced by AxisParser#sym.
    def enterSym(self, ctx:AxisParser.SymContext):
        pass

    # Exit a parse tree produced by AxisParser#sym.
    def exitSym(self, ctx:AxisParser.SymContext):
        pass


    # Enter a parse tree produced by AxisParser#lit.
    def enterLit(self, ctx:AxisParser.LitContext):
        pass

    # Exit a parse tree produced by AxisParser#lit.
    def exitLit(self, ctx:AxisParser.LitContext):
        pass


    # Enter a parse tree produced by AxisParser#tuple.
    def enterTuple(self, ctx:AxisParser.TupleContext):
        pass

    # Exit a parse tree produced by AxisParser#tuple.
    def exitTuple(self, ctx:AxisParser.TupleContext):
        pass


    # Enter a parse tree produced by AxisParser#shape.
    def enterShape(self, ctx:AxisParser.ShapeContext):
        pass

    # Exit a parse tree produced by AxisParser#shape.
    def exitShape(self, ctx:AxisParser.ShapeContext):
        pass


    # Enter a parse tree produced by AxisParser#ValueElement.
    def enterValueElement(self, ctx:AxisParser.ValueElementContext):
        pass

    # Exit a parse tree produced by AxisParser#ValueElement.
    def exitValueElement(self, ctx:AxisParser.ValueElementContext):
        pass


    # Enter a parse tree produced by AxisParser#NamedElement.
    def enterNamedElement(self, ctx:AxisParser.NamedElementContext):
        pass

    # Exit a parse tree produced by AxisParser#NamedElement.
    def exitNamedElement(self, ctx:AxisParser.NamedElementContext):
        pass


    # Enter a parse tree produced by AxisParser#SpreadElement.
    def enterSpreadElement(self, ctx:AxisParser.SpreadElementContext):
        pass

    # Exit a parse tree produced by AxisParser#SpreadElement.
    def exitSpreadElement(self, ctx:AxisParser.SpreadElementContext):
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



del AxisParser