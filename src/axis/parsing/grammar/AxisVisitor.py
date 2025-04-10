# Generated from src/axis/codebase/grammar/Axis.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .AxisParser import AxisParser
else:
    from AxisParser import AxisParser

# This class defines a complete generic visitor for a parse tree produced by AxisParser.

class AxisVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by AxisParser#suite.
    def visitSuite(self, ctx:AxisParser.SuiteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#defItem.
    def visitDefItem(self, ctx:AxisParser.DefItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#valItem.
    def visitValItem(self, ctx:AxisParser.ValItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#statement.
    def visitStatement(self, ctx:AxisParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#valStatement.
    def visitValStatement(self, ctx:AxisParser.ValStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#pattern.
    def visitPattern(self, ctx:AxisParser.PatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#tuplePattern.
    def visitTuplePattern(self, ctx:AxisParser.TuplePatternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#tuplePatternElement.
    def visitTuplePatternElement(self, ctx:AxisParser.TuplePatternElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#expression.
    def visitExpression(self, ctx:AxisParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#juxtapositionExpr.
    def visitJuxtapositionExpr(self, ctx:AxisParser.JuxtapositionExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#logicalExpr.
    def visitLogicalExpr(self, ctx:AxisParser.LogicalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#logicalOp.
    def visitLogicalOp(self, ctx:AxisParser.LogicalOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#comparisonExpr.
    def visitComparisonExpr(self, ctx:AxisParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#addition.
    def visitAddition(self, ctx:AxisParser.AdditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#product.
    def visitProduct(self, ctx:AxisParser.ProductContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#Call.
    def visitCall(self, ctx:AxisParser.CallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#Pass.
    def visitPass(self, ctx:AxisParser.PassContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#MemberAccess.
    def visitMemberAccess(self, ctx:AxisParser.MemberAccessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#TrailingCall.
    def visitTrailingCall(self, ctx:AxisParser.TrailingCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#Indexing.
    def visitIndexing(self, ctx:AxisParser.IndexingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#primaryExpr.
    def visitPrimaryExpr(self, ctx:AxisParser.PrimaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#wildcard.
    def visitWildcard(self, ctx:AxisParser.WildcardContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#ellipsis.
    def visitEllipsis(self, ctx:AxisParser.EllipsisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#spread.
    def visitSpread(self, ctx:AxisParser.SpreadContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#tuple.
    def visitTuple(self, ctx:AxisParser.TupleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#TupleElementSingle.
    def visitTupleElementSingle(self, ctx:AxisParser.TupleElementSingleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#TupleElementAssignation.
    def visitTupleElementAssignation(self, ctx:AxisParser.TupleElementAssignationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#TupleElementBounded.
    def visitTupleElementBounded(self, ctx:AxisParser.TupleElementBoundedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#TupleElementBoundedAssignation.
    def visitTupleElementBoundedAssignation(self, ctx:AxisParser.TupleElementBoundedAssignationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#LambdaSuite.
    def visitLambdaSuite(self, ctx:AxisParser.LambdaSuiteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#BasicSuite.
    def visitBasicSuite(self, ctx:AxisParser.BasicSuiteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#semicolon.
    def visitSemicolon(self, ctx:AxisParser.SemicolonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#lambdaParams.
    def visitLambdaParams(self, ctx:AxisParser.LambdaParamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#lambdaParam.
    def visitLambdaParam(self, ctx:AxisParser.LambdaParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#argument.
    def visitArgument(self, ctx:AxisParser.ArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#identifier.
    def visitIdentifier(self, ctx:AxisParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#literal.
    def visitLiteral(self, ctx:AxisParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#text.
    def visitText(self, ctx:AxisParser.TextContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by AxisParser#decimal.
    def visitDecimal(self, ctx:AxisParser.DecimalContext):
        return self.visitChildren(ctx)



del AxisParser