// Generated from /home/jdluque/Workspace/prodisign/protobase/src/axislang/grammar/Axis.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link AxisParser}.
 */
public interface AxisListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link AxisParser#program}.
	 * @param ctx the parse tree
	 */
	void enterProgram(AxisParser.ProgramContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#program}.
	 * @param ctx the parse tree
	 */
	void exitProgram(AxisParser.ProgramContext ctx);
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
	 * Enter a parse tree produced by {@link AxisParser#typeDefinition}.
	 * @param ctx the parse tree
	 */
	void enterTypeDefinition(AxisParser.TypeDefinitionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#typeDefinition}.
	 * @param ctx the parse tree
	 */
	void exitTypeDefinition(AxisParser.TypeDefinitionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#tupleTypeDefinition}.
	 * @param ctx the parse tree
	 */
	void enterTupleTypeDefinition(AxisParser.TupleTypeDefinitionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#tupleTypeDefinition}.
	 * @param ctx the parse tree
	 */
	void exitTupleTypeDefinition(AxisParser.TupleTypeDefinitionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#parameterDefinition}.
	 * @param ctx the parse tree
	 */
	void enterParameterDefinition(AxisParser.ParameterDefinitionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#parameterDefinition}.
	 * @param ctx the parse tree
	 */
	void exitParameterDefinition(AxisParser.ParameterDefinitionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#functionDefinition}.
	 * @param ctx the parse tree
	 */
	void enterFunctionDefinition(AxisParser.FunctionDefinitionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#functionDefinition}.
	 * @param ctx the parse tree
	 */
	void exitFunctionDefinition(AxisParser.FunctionDefinitionContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#whereClause}.
	 * @param ctx the parse tree
	 */
	void enterWhereClause(AxisParser.WhereClauseContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#whereClause}.
	 * @param ctx the parse tree
	 */
	void exitWhereClause(AxisParser.WhereClauseContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#typeConstraint}.
	 * @param ctx the parse tree
	 */
	void enterTypeConstraint(AxisParser.TypeConstraintContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#typeConstraint}.
	 * @param ctx the parse tree
	 */
	void exitTypeConstraint(AxisParser.TypeConstraintContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#valueDeclaration}.
	 * @param ctx the parse tree
	 */
	void enterValueDeclaration(AxisParser.ValueDeclarationContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#valueDeclaration}.
	 * @param ctx the parse tree
	 */
	void exitValueDeclaration(AxisParser.ValueDeclarationContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#typeExpression}.
	 * @param ctx the parse tree
	 */
	void enterTypeExpression(AxisParser.TypeExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#typeExpression}.
	 * @param ctx the parse tree
	 */
	void exitTypeExpression(AxisParser.TypeExpressionContext ctx);
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
	 * Enter a parse tree produced by {@link AxisParser#namedArgument}.
	 * @param ctx the parse tree
	 */
	void enterNamedArgument(AxisParser.NamedArgumentContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#namedArgument}.
	 * @param ctx the parse tree
	 */
	void exitNamedArgument(AxisParser.NamedArgumentContext ctx);
	/**
	 * Enter a parse tree produced by {@link AxisParser#assertStatement}.
	 * @param ctx the parse tree
	 */
	void enterAssertStatement(AxisParser.AssertStatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link AxisParser#assertStatement}.
	 * @param ctx the parse tree
	 */
	void exitAssertStatement(AxisParser.AssertStatementContext ctx);
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
}