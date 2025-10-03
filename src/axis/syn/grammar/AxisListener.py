# Generated from src/axis/syn/grammar/Axis.g4 by ANTLR 4.13.2
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


    # Enter a parse tree produced by AxisParser#useBlock.
    def enterUseBlock(self, ctx:AxisParser.UseBlockContext):
        pass

    # Exit a parse tree produced by AxisParser#useBlock.
    def exitUseBlock(self, ctx:AxisParser.UseBlockContext):
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


    # Enter a parse tree produced by AxisParser#expr.
    def enterExpr(self, ctx:AxisParser.ExprContext):
        pass

    # Exit a parse tree produced by AxisParser#expr.
    def exitExpr(self, ctx:AxisParser.ExprContext):
        pass


    # Enter a parse tree produced by AxisParser#compoundExpr.
    def enterCompoundExpr(self, ctx:AxisParser.CompoundExprContext):
        pass

    # Exit a parse tree produced by AxisParser#compoundExpr.
    def exitCompoundExpr(self, ctx:AxisParser.CompoundExprContext):
        pass


    # Enter a parse tree produced by AxisParser#rangeExpr.
    def enterRangeExpr(self, ctx:AxisParser.RangeExprContext):
        pass

    # Exit a parse tree produced by AxisParser#rangeExpr.
    def exitRangeExpr(self, ctx:AxisParser.RangeExprContext):
        pass


    # Enter a parse tree produced by AxisParser#rangeOp.
    def enterRangeOp(self, ctx:AxisParser.RangeOpContext):
        pass

    # Exit a parse tree produced by AxisParser#rangeOp.
    def exitRangeOp(self, ctx:AxisParser.RangeOpContext):
        pass


    # Enter a parse tree produced by AxisParser#logicExpr.
    def enterLogicExpr(self, ctx:AxisParser.LogicExprContext):
        pass

    # Exit a parse tree produced by AxisParser#logicExpr.
    def exitLogicExpr(self, ctx:AxisParser.LogicExprContext):
        pass


    # Enter a parse tree produced by AxisParser#logicOp.
    def enterLogicOp(self, ctx:AxisParser.LogicOpContext):
        pass

    # Exit a parse tree produced by AxisParser#logicOp.
    def exitLogicOp(self, ctx:AxisParser.LogicOpContext):
        pass


    # Enter a parse tree produced by AxisParser#comparisonExpr.
    def enterComparisonExpr(self, ctx:AxisParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by AxisParser#comparisonExpr.
    def exitComparisonExpr(self, ctx:AxisParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by AxisParser#comparisonOp.
    def enterComparisonOp(self, ctx:AxisParser.ComparisonOpContext):
        pass

    # Exit a parse tree produced by AxisParser#comparisonOp.
    def exitComparisonOp(self, ctx:AxisParser.ComparisonOpContext):
        pass


    # Enter a parse tree produced by AxisParser#additiveExpr.
    def enterAdditiveExpr(self, ctx:AxisParser.AdditiveExprContext):
        pass

    # Exit a parse tree produced by AxisParser#additiveExpr.
    def exitAdditiveExpr(self, ctx:AxisParser.AdditiveExprContext):
        pass


    # Enter a parse tree produced by AxisParser#additiveOp.
    def enterAdditiveOp(self, ctx:AxisParser.AdditiveOpContext):
        pass

    # Exit a parse tree produced by AxisParser#additiveOp.
    def exitAdditiveOp(self, ctx:AxisParser.AdditiveOpContext):
        pass


    # Enter a parse tree produced by AxisParser#productiveExpr.
    def enterProductiveExpr(self, ctx:AxisParser.ProductiveExprContext):
        pass

    # Exit a parse tree produced by AxisParser#productiveExpr.
    def exitProductiveExpr(self, ctx:AxisParser.ProductiveExprContext):
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


    # Enter a parse tree produced by AxisParser#EtcExpr.
    def enterEtcExpr(self, ctx:AxisParser.EtcExprContext):
        pass

    # Exit a parse tree produced by AxisParser#EtcExpr.
    def exitEtcExpr(self, ctx:AxisParser.EtcExprContext):
        pass


    # Enter a parse tree produced by AxisParser#SignExpr.
    def enterSignExpr(self, ctx:AxisParser.SignExprContext):
        pass

    # Exit a parse tree produced by AxisParser#SignExpr.
    def exitSignExpr(self, ctx:AxisParser.SignExprContext):
        pass


    # Enter a parse tree produced by AxisParser#signOp.
    def enterSignOp(self, ctx:AxisParser.SignOpContext):
        pass

    # Exit a parse tree produced by AxisParser#signOp.
    def exitSignOp(self, ctx:AxisParser.SignOpContext):
        pass


    # Enter a parse tree produced by AxisParser#etcOp.
    def enterEtcOp(self, ctx:AxisParser.EtcOpContext):
        pass

    # Exit a parse tree produced by AxisParser#etcOp.
    def exitEtcOp(self, ctx:AxisParser.EtcOpContext):
        pass


    # Enter a parse tree produced by AxisParser#prefixOp.
    def enterPrefixOp(self, ctx:AxisParser.PrefixOpContext):
        pass

    # Exit a parse tree produced by AxisParser#prefixOp.
    def exitPrefixOp(self, ctx:AxisParser.PrefixOpContext):
        pass


    # Enter a parse tree produced by AxisParser#ApplyExpr.
    def enterApplyExpr(self, ctx:AxisParser.ApplyExprContext):
        pass

    # Exit a parse tree produced by AxisParser#ApplyExpr.
    def exitApplyExpr(self, ctx:AxisParser.ApplyExprContext):
        pass


    # Enter a parse tree produced by AxisParser#MemberExpr.
    def enterMemberExpr(self, ctx:AxisParser.MemberExprContext):
        pass

    # Exit a parse tree produced by AxisParser#MemberExpr.
    def exitMemberExpr(self, ctx:AxisParser.MemberExprContext):
        pass


    # Enter a parse tree produced by AxisParser#PostfixPass.
    def enterPostfixPass(self, ctx:AxisParser.PostfixPassContext):
        pass

    # Exit a parse tree produced by AxisParser#PostfixPass.
    def exitPostfixPass(self, ctx:AxisParser.PostfixPassContext):
        pass


    # Enter a parse tree produced by AxisParser#TrailExpr.
    def enterTrailExpr(self, ctx:AxisParser.TrailExprContext):
        pass

    # Exit a parse tree produced by AxisParser#TrailExpr.
    def exitTrailExpr(self, ctx:AxisParser.TrailExprContext):
        pass


    # Enter a parse tree produced by AxisParser#IndexExpr.
    def enterIndexExpr(self, ctx:AxisParser.IndexExprContext):
        pass

    # Exit a parse tree produced by AxisParser#IndexExpr.
    def exitIndexExpr(self, ctx:AxisParser.IndexExprContext):
        pass


    # Enter a parse tree produced by AxisParser#ScopeExpr.
    def enterScopeExpr(self, ctx:AxisParser.ScopeExprContext):
        pass

    # Exit a parse tree produced by AxisParser#ScopeExpr.
    def exitScopeExpr(self, ctx:AxisParser.ScopeExprContext):
        pass


    # Enter a parse tree produced by AxisParser#primaryExpr.
    def enterPrimaryExpr(self, ctx:AxisParser.PrimaryExprContext):
        pass

    # Exit a parse tree produced by AxisParser#primaryExpr.
    def exitPrimaryExpr(self, ctx:AxisParser.PrimaryExprContext):
        pass


    # Enter a parse tree produced by AxisParser#ellipsisExpr.
    def enterEllipsisExpr(self, ctx:AxisParser.EllipsisExprContext):
        pass

    # Exit a parse tree produced by AxisParser#ellipsisExpr.
    def exitEllipsisExpr(self, ctx:AxisParser.EllipsisExprContext):
        pass


    # Enter a parse tree produced by AxisParser#wildcardExpr.
    def enterWildcardExpr(self, ctx:AxisParser.WildcardExprContext):
        pass

    # Exit a parse tree produced by AxisParser#wildcardExpr.
    def exitWildcardExpr(self, ctx:AxisParser.WildcardExprContext):
        pass


    # Enter a parse tree produced by AxisParser#symExpr.
    def enterSymExpr(self, ctx:AxisParser.SymExprContext):
        pass

    # Exit a parse tree produced by AxisParser#symExpr.
    def exitSymExpr(self, ctx:AxisParser.SymExprContext):
        pass


    # Enter a parse tree produced by AxisParser#litExpr.
    def enterLitExpr(self, ctx:AxisParser.LitExprContext):
        pass

    # Exit a parse tree produced by AxisParser#litExpr.
    def exitLitExpr(self, ctx:AxisParser.LitExprContext):
        pass


    # Enter a parse tree produced by AxisParser#tupleExpr.
    def enterTupleExpr(self, ctx:AxisParser.TupleExprContext):
        pass

    # Exit a parse tree produced by AxisParser#tupleExpr.
    def exitTupleExpr(self, ctx:AxisParser.TupleExprContext):
        pass


    # Enter a parse tree produced by AxisParser#shapeExpr.
    def enterShapeExpr(self, ctx:AxisParser.ShapeExprContext):
        pass

    # Exit a parse tree produced by AxisParser#shapeExpr.
    def exitShapeExpr(self, ctx:AxisParser.ShapeExprContext):
        pass


    # Enter a parse tree produced by AxisParser#tupleElement.
    def enterTupleElement(self, ctx:AxisParser.TupleElementContext):
        pass

    # Exit a parse tree produced by AxisParser#tupleElement.
    def exitTupleElement(self, ctx:AxisParser.TupleElementContext):
        pass


    # Enter a parse tree produced by AxisParser#tuplePositionalElement.
    def enterTuplePositionalElement(self, ctx:AxisParser.TuplePositionalElementContext):
        pass

    # Exit a parse tree produced by AxisParser#tuplePositionalElement.
    def exitTuplePositionalElement(self, ctx:AxisParser.TuplePositionalElementContext):
        pass


    # Enter a parse tree produced by AxisParser#tupleNominalElement.
    def enterTupleNominalElement(self, ctx:AxisParser.TupleNominalElementContext):
        pass

    # Exit a parse tree produced by AxisParser#tupleNominalElement.
    def exitTupleNominalElement(self, ctx:AxisParser.TupleNominalElementContext):
        pass


    # Enter a parse tree produced by AxisParser#tupleSpreadElement.
    def enterTupleSpreadElement(self, ctx:AxisParser.TupleSpreadElementContext):
        pass

    # Exit a parse tree produced by AxisParser#tupleSpreadElement.
    def exitTupleSpreadElement(self, ctx:AxisParser.TupleSpreadElementContext):
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