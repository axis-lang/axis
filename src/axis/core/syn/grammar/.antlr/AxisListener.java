// Generated from /home/jdluque/Workspace/prodisign/axis/src/axis/parsing/grammar/Axis.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link AxisParser}.
 */
public interface AxisListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link AxisParser#defItem}.
	 * @param ctx the parse tree
	 */
	void enterDefItem(AxisParser.DefItemContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#defItem}.
	 * @param ctx the parse tree
	 */
	void exitDefItem(AxisParser.DefItemContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#valItem}.
	 * @param ctx the parse tree
	 */
	void enterValItem(AxisParser.ValItemContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#valItem}.
	 * @param ctx the parse tree
	 */
	void exitValItem(AxisParser.ValItemContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#returnsBlock}.
	 * @param ctx the parse tree
	 */
	void enterReturnsBlock(AxisParser.ReturnsBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#returnsBlock}.
	 * @param ctx the parse tree
	 */
	void exitReturnsBlock(AxisParser.ReturnsBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#suiteBlock}.
	 * @param ctx the parse tree
	 */
	void enterSuiteBlock(AxisParser.SuiteBlockContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#suiteBlock}.
	 * @param ctx the parse tree
	 */
	void exitSuiteBlock(AxisParser.SuiteBlockContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#suite}.
	 * @param ctx the parse tree
	 */
	void enterSuite(AxisParser.SuiteContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#suite}.
	 * @param ctx the parse tree
	 */
	void exitSuite(AxisParser.SuiteContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#statement}.
	 * @param ctx the parse tree
	 */
	void enterStatement(AxisParser.StatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#statement}.
	 * @param ctx the parse tree
	 */
	void exitStatement(AxisParser.StatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#valStatement}.
	 * @param ctx the parse tree
	 */
	void enterValStatement(AxisParser.ValStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#valStatement}.
	 * @param ctx the parse tree
	 */
	void exitValStatement(AxisParser.ValStatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#pattern}.
	 * @param ctx the parse tree
	 */
	void enterPattern(AxisParser.PatternContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#pattern}.
	 * @param ctx the parse tree
	 */
	void exitPattern(AxisParser.PatternContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#tuplePattern}.
	 * @param ctx the parse tree
	 */
	void enterTuplePattern(AxisParser.TuplePatternContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#tuplePattern}.
	 * @param ctx the parse tree
	 */
	void exitTuplePattern(AxisParser.TuplePatternContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#tuplePatternElement}.
	 * @param ctx the parse tree
	 */
	void enterTuplePatternElement(AxisParser.TuplePatternElementContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#tuplePatternElement}.
	 * @param ctx the parse tree
	 */
	void exitTuplePatternElement(AxisParser.TuplePatternElementContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#expression}.
	 * @param ctx the parse tree
	 */
	void enterExpression(AxisParser.ExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#expression}.
	 * @param ctx the parse tree
	 */
	void exitExpression(AxisParser.ExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#juxtapositionExpr}.
	 * @param ctx the parse tree
	 */
	void enterJuxtapositionExpr(AxisParser.JuxtapositionExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#juxtapositionExpr}.
	 * @param ctx the parse tree
	 */
	void exitJuxtapositionExpr(AxisParser.JuxtapositionExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#logicalExpr}.
	 * @param ctx the parse tree
	 */
	void enterLogicalExpr(AxisParser.LogicalExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#logicalExpr}.
	 * @param ctx the parse tree
	 */
	void exitLogicalExpr(AxisParser.LogicalExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#logicalOp}.
	 * @param ctx the parse tree
	 */
	void enterLogicalOp(AxisParser.LogicalOpContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#logicalOp}.
	 * @param ctx the parse tree
	 */
	void exitLogicalOp(AxisParser.LogicalOpContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#comparisonExpr}.
	 * @param ctx the parse tree
	 */
	void enterComparisonExpr(AxisParser.ComparisonExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#comparisonExpr}.
	 * @param ctx the parse tree
	 */
	void exitComparisonExpr(AxisParser.ComparisonExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#addition}.
	 * @param ctx the parse tree
	 */
	void enterAddition(AxisParser.AdditionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#addition}.
	 * @param ctx the parse tree
	 */
	void exitAddition(AxisParser.AdditionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#product}.
	 * @param ctx the parse tree
	 */
	void enterProduct(AxisParser.ProductContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#product}.
	 * @param ctx the parse tree
	 */
	void exitProduct(AxisParser.ProductContext ctx);
	/**
	 * Enter a parse tree produced by the {@code Call}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterCall(AxisParser.CallContext ctx);
	/**
	 * Exit a parse tree produced by the {@code Call}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitCall(AxisParser.CallContext ctx);
	/**
	 * Enter a parse tree produced by the {@code Pass}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterPass(AxisParser.PassContext ctx);
	/**
	 * Exit a parse tree produced by the {@code Pass}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitPass(AxisParser.PassContext ctx);
	/**
	 * Enter a parse tree produced by the {@code MemberAccess}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterMemberAccess(AxisParser.MemberAccessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code MemberAccess}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitMemberAccess(AxisParser.MemberAccessContext ctx);
	/**
	 * Enter a parse tree produced by the {@code TrailingLambda}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterTrailingLambda(AxisParser.TrailingLambdaContext ctx);
	/**
	 * Exit a parse tree produced by the {@code TrailingLambda}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitTrailingLambda(AxisParser.TrailingLambdaContext ctx);
	/**
	 * Enter a parse tree produced by the {@code ScopeAccess}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterScopeAccess(AxisParser.ScopeAccessContext ctx);
	/**
	 * Exit a parse tree produced by the {@code ScopeAccess}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitScopeAccess(AxisParser.ScopeAccessContext ctx);
	/**
	 * Enter a parse tree produced by the {@code Index}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void enterIndex(AxisParser.IndexContext ctx);
	/**
	 * Exit a parse tree produced by the {@code Index}
	 * labeled alternative in {@link AxisParser#postfix}.
	 * @param ctx the parse tree
	 */
	void exitIndex(AxisParser.IndexContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#primaryExpr}.
	 * @param ctx the parse tree
	 */
	void enterPrimaryExpr(AxisParser.PrimaryExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#primaryExpr}.
	 * @param ctx the parse tree
	 */
	void exitPrimaryExpr(AxisParser.PrimaryExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#wildcard}.
	 * @param ctx the parse tree
	 */
	void enterWildcard(AxisParser.WildcardContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#wildcard}.
	 * @param ctx the parse tree
	 */
	void exitWildcard(AxisParser.WildcardContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#ellipsis}.
	 * @param ctx the parse tree
	 */
	void enterEllipsis(AxisParser.EllipsisContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#ellipsis}.
	 * @param ctx the parse tree
	 */
	void exitEllipsis(AxisParser.EllipsisContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#spread}.
	 * @param ctx the parse tree
	 */
	void enterSpread(AxisParser.SpreadContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#spread}.
	 * @param ctx the parse tree
	 */
	void exitSpread(AxisParser.SpreadContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#tuple}.
	 * @param ctx the parse tree
	 */
	void enterTuple(AxisParser.TupleContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#tuple}.
	 * @param ctx the parse tree
	 */
	void exitTuple(AxisParser.TupleContext ctx);
	/**
	 * Enter a parse tree produced by the {@code TupleElementSingle}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void enterTupleElementSingle(AxisParser.TupleElementSingleContext ctx);
	/**
	 * Exit a parse tree produced by the {@code TupleElementSingle}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void exitTupleElementSingle(AxisParser.TupleElementSingleContext ctx);
	/**
	 * Enter a parse tree produced by the {@code TupleElementAssignation}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void enterTupleElementAssignation(AxisParser.TupleElementAssignationContext ctx);
	/**
	 * Exit a parse tree produced by the {@code TupleElementAssignation}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void exitTupleElementAssignation(AxisParser.TupleElementAssignationContext ctx);
	/**
	 * Enter a parse tree produced by the {@code TupleElementBounded}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void enterTupleElementBounded(AxisParser.TupleElementBoundedContext ctx);
	/**
	 * Exit a parse tree produced by the {@code TupleElementBounded}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void exitTupleElementBounded(AxisParser.TupleElementBoundedContext ctx);
	/**
	 * Enter a parse tree produced by the {@code TupleElementBoundedAssignation}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void enterTupleElementBoundedAssignation(AxisParser.TupleElementBoundedAssignationContext ctx);
	/**
	 * Exit a parse tree produced by the {@code TupleElementBoundedAssignation}
	 * labeled alternative in {@link AxisParser#tupleElement}.
	 * @param ctx the parse tree
	 */
	void exitTupleElementBoundedAssignation(AxisParser.TupleElementBoundedAssignationContext ctx);
	/**
	 * Enter a parse tree produced by the {@code LambdaSuite}
	 * labeled alternative in {@link AxisParser#lambda}.
	 * @param ctx the parse tree
	 */
	void enterLambdaSuite(AxisParser.LambdaSuiteContext ctx);
	/**
	 * Exit a parse tree produced by the {@code LambdaSuite}
	 * labeled alternative in {@link AxisParser#lambda}.
	 * @param ctx the parse tree
	 */
	void exitLambdaSuite(AxisParser.LambdaSuiteContext ctx);
	/**
	 * Enter a parse tree produced by the {@code BasicSuite}
	 * labeled alternative in {@link AxisParser#lambda}.
	 * @param ctx the parse tree
	 */
	void enterBasicSuite(AxisParser.BasicSuiteContext ctx);
	/**
	 * Exit a parse tree produced by the {@code BasicSuite}
	 * labeled alternative in {@link AxisParser#lambda}.
	 * @param ctx the parse tree
	 */
	void exitBasicSuite(AxisParser.BasicSuiteContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#semicolon}.
	 * @param ctx the parse tree
	 */
	void enterSemicolon(AxisParser.SemicolonContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#semicolon}.
	 * @param ctx the parse tree
	 */
	void exitSemicolon(AxisParser.SemicolonContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#lambdaParams}.
	 * @param ctx the parse tree
	 */
	void enterLambdaParams(AxisParser.LambdaParamsContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#lambdaParams}.
	 * @param ctx the parse tree
	 */
	void exitLambdaParams(AxisParser.LambdaParamsContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#lambdaParam}.
	 * @param ctx the parse tree
	 */
	void enterLambdaParam(AxisParser.LambdaParamContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#lambdaParam}.
	 * @param ctx the parse tree
	 */
	void exitLambdaParam(AxisParser.LambdaParamContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#argument}.
	 * @param ctx the parse tree
	 */
	void enterArgument(AxisParser.ArgumentContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#argument}.
	 * @param ctx the parse tree
	 */
	void exitArgument(AxisParser.ArgumentContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#identifier}.
	 * @param ctx the parse tree
	 */
	void enterIdentifier(AxisParser.IdentifierContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#identifier}.
	 * @param ctx the parse tree
	 */
	void exitIdentifier(AxisParser.IdentifierContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#literal}.
	 * @param ctx the parse tree
	 */
	void enterLiteral(AxisParser.LiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#literal}.
	 * @param ctx the parse tree
	 */
	void exitLiteral(AxisParser.LiteralContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#text}.
	 * @param ctx the parse tree
	 */
	void enterText(AxisParser.TextContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#text}.
	 * @param ctx the parse tree
	 */
	void exitText(AxisParser.TextContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#decimal}.
	 * @param ctx the parse tree
	 */
	void enterDecimal(AxisParser.DecimalContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#decimal}.
	 * @param ctx the parse tree
	 */
	void exitDecimal(AxisParser.DecimalContext ctx);
}