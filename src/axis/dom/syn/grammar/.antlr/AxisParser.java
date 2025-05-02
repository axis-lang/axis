// Generated from /home/jdluque/Workspace/prodisign/axis/src/axis/parsing/grammar/Axis.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue"})
public class AxisParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, T__13=14, T__14=15, T__15=16, T__16=17, 
		T__17=18, T__18=19, ID=20, DECIMAL=21, TEXT=22, ADD=23, SUB=24, MUL=25, 
		DIV=26, MOD=27, EQ=28, NE=29, LT=30, LE=31, GT=32, GE=33, AND=34, OR=35, 
		COLON=36, ASSIGN=37, ARROW=38, ELLIPSIS=39, WILDCARD=40, WS=41, COMMENT=42;
	public static final int
		RULE_unitItem = 0, RULE_modItem = 1, RULE_defItem = 2, RULE_valItem = 3, 
		RULE_useItem = 4, RULE_takesBlock = 5, RULE_whereBlock = 6, RULE_returnsBlock = 7, 
		RULE_suiteBlock = 8, RULE_suite = 9, RULE_statement = 10, RULE_valStatement = 11, 
		RULE_pattern = 12, RULE_tuplePattern = 13, RULE_tuplePatternElement = 14, 
		RULE_expression = 15, RULE_juxtapositionExpr = 16, RULE_logicalExpr = 17, 
		RULE_logicalOp = 18, RULE_comparisonExpr = 19, RULE_addition = 20, RULE_product = 21, 
		RULE_postfix = 22, RULE_primaryExpr = 23, RULE_wildcard = 24, RULE_ellipsis = 25, 
		RULE_spread = 26, RULE_tuple = 27, RULE_shape = 28, RULE_tupleElement = 29, 
		RULE_lambda = 30, RULE_semicolon = 31, RULE_lambdaParams = 32, RULE_lambdaParam = 33, 
		RULE_argument = 34, RULE_identifier = 35, RULE_literal = 36, RULE_text = 37, 
		RULE_decimal = 38;
	private static String[] makeRuleNames() {
		return new String[] {
			"unitItem", "modItem", "defItem", "valItem", "useItem", "takesBlock", 
			"whereBlock", "returnsBlock", "suiteBlock", "suite", "statement", "valStatement", 
			"pattern", "tuplePattern", "tuplePatternElement", "expression", "juxtapositionExpr", 
			"logicalExpr", "logicalOp", "comparisonExpr", "addition", "product", 
			"postfix", "primaryExpr", "wildcard", "ellipsis", "spread", "tuple", 
			"shape", "tupleElement", "lambda", "semicolon", "lambdaParams", "lambdaParam", 
			"argument", "identifier", "literal", "text", "decimal"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'unit'", "'mod'", "'def'", "'val'", "';'", "'use'", "'takes'", 
			"'where'", "'returns'", "'suite'", "'('", "','", "')'", "'.'", "'::'", 
			"'['", "']'", "'{'", "'}'", null, null, null, "'+'", "'-'", "'*'", "'/'", 
			"'%'", "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", "'&&'", "'||'", 
			"':'", "'='", "'->'", "'..'", "'_'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, "ID", "DECIMAL", "TEXT", 
			"ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", 
			"AND", "OR", "COLON", "ASSIGN", "ARROW", "ELLIPSIS", "WILDCARD", "WS", 
			"COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Axis.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public AxisParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@SuppressWarnings("CheckReturnValue")
	public static class UnitItemContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public UnitItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_unitItem; }
	}

	public final UnitItemContext unitItem() throws RecognitionException {
		UnitItemContext _localctx = new UnitItemContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_unitItem);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(78);
			match(T__0);
			setState(79);
			expression();
			setState(80);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ModItemContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public ModItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_modItem; }
	}

	public final ModItemContext modItem() throws RecognitionException {
		ModItemContext _localctx = new ModItemContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_modItem);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(82);
			match(T__1);
			setState(83);
			expression();
			setState(84);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class DefItemContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public DefItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_defItem; }
	}

	public final DefItemContext defItem() throws RecognitionException {
		DefItemContext _localctx = new DefItemContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_defItem);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(86);
			match(T__2);
			setState(87);
			expression();
			setState(88);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ValItemContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TerminalNode ASSIGN() { return getToken(AxisParser.ASSIGN, 0); }
		public ValItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_valItem; }
	}

	public final ValItemContext valItem() throws RecognitionException {
		ValItemContext _localctx = new ValItemContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_valItem);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(90);
			match(T__3);
			setState(91);
			expression();
			setState(94);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==COLON) {
				{
				setState(92);
				match(COLON);
				setState(93);
				expression();
				}
			}

			setState(98);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ASSIGN) {
				{
				setState(96);
				match(ASSIGN);
				setState(97);
				expression();
				}
			}

			setState(101);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(100);
				match(T__4);
				}
			}

			setState(103);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class UseItemContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public UseItemContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_useItem; }
	}

	public final UseItemContext useItem() throws RecognitionException {
		UseItemContext _localctx = new UseItemContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_useItem);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(105);
			match(T__5);
			setState(106);
			expression();
			setState(107);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TakesBlockContext extends ParserRuleContext {
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TerminalNode ID() { return getToken(AxisParser.ID, 0); }
		public TakesBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_takesBlock; }
	}

	public final TakesBlockContext takesBlock() throws RecognitionException {
		TakesBlockContext _localctx = new TakesBlockContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_takesBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(109);
			match(T__6);
			setState(111);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(110);
				match(ID);
				}
			}

			setState(113);
			match(COLON);
			setState(114);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class WhereBlockContext extends ParserRuleContext {
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public WhereBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_whereBlock; }
	}

	public final WhereBlockContext whereBlock() throws RecognitionException {
		WhereBlockContext _localctx = new WhereBlockContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_whereBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(116);
			match(T__7);
			setState(117);
			match(COLON);
			setState(118);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ReturnsBlockContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public ReturnsBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_returnsBlock; }
	}

	public final ReturnsBlockContext returnsBlock() throws RecognitionException {
		ReturnsBlockContext _localctx = new ReturnsBlockContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_returnsBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(120);
			match(T__8);
			setState(121);
			expression();
			setState(122);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SuiteBlockContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public SuiteBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_suiteBlock; }
	}

	public final SuiteBlockContext suiteBlock() throws RecognitionException {
		SuiteBlockContext _localctx = new SuiteBlockContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_suiteBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(124);
			match(T__9);
			setState(128);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045904L) != 0)) {
				{
				{
				setState(125);
				statement();
				}
				}
				setState(130);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(131);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SuiteContext extends ParserRuleContext {
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public SuiteContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_suite; }
	}

	public final SuiteContext suite() throws RecognitionException {
		SuiteContext _localctx = new SuiteContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_suite);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(136);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045904L) != 0)) {
				{
				{
				setState(133);
				statement();
				}
				}
				setState(138);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class StatementContext extends ParserRuleContext {
		public ValStatementContext valStatement() {
			return getRuleContext(ValStatementContext.class,0);
		}
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_statement);
		try {
			setState(141);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__3:
				enterOuterAlt(_localctx, 1);
				{
				setState(139);
				valStatement();
				}
				break;
			case T__10:
			case T__17:
			case ID:
			case DECIMAL:
			case TEXT:
			case ELLIPSIS:
			case WILDCARD:
				enterOuterAlt(_localctx, 2);
				{
				setState(140);
				expression();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ValStatementContext extends ParserRuleContext {
		public PatternContext pattern() {
			return getRuleContext(PatternContext.class,0);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode ASSIGN() { return getToken(AxisParser.ASSIGN, 0); }
		public ValStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_valStatement; }
	}

	public final ValStatementContext valStatement() throws RecognitionException {
		ValStatementContext _localctx = new ValStatementContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_valStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(143);
			match(T__3);
			{
			setState(144);
			pattern();
			}
			setState(147);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==COLON) {
				{
				setState(145);
				match(COLON);
				setState(146);
				expression();
				}
			}

			setState(151);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ASSIGN) {
				{
				setState(149);
				match(ASSIGN);
				setState(150);
				expression();
				}
			}

			setState(154);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,9,_ctx) ) {
			case 1:
				{
				setState(153);
				match(T__4);
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PatternContext extends ParserRuleContext {
		public IdentifierContext identifier() {
			return getRuleContext(IdentifierContext.class,0);
		}
		public TuplePatternContext tuplePattern() {
			return getRuleContext(TuplePatternContext.class,0);
		}
		public PatternContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_pattern; }
	}

	public final PatternContext pattern() throws RecognitionException {
		PatternContext _localctx = new PatternContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_pattern);
		try {
			setState(158);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(156);
				identifier();
				}
				break;
			case T__10:
				enterOuterAlt(_localctx, 2);
				{
				setState(157);
				tuplePattern();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TuplePatternContext extends ParserRuleContext {
		public List<TuplePatternElementContext> tuplePatternElement() {
			return getRuleContexts(TuplePatternElementContext.class);
		}
		public TuplePatternElementContext tuplePatternElement(int i) {
			return getRuleContext(TuplePatternElementContext.class,i);
		}
		public TuplePatternContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tuplePattern; }
	}

	public final TuplePatternContext tuplePattern() throws RecognitionException {
		TuplePatternContext _localctx = new TuplePatternContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_tuplePattern);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(160);
			match(T__10);
			setState(169);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(161);
				tuplePatternElement();
				setState(166);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==T__11) {
					{
					{
					setState(162);
					match(T__11);
					setState(163);
					tuplePatternElement();
					}
					}
					setState(168);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
			}

			setState(171);
			match(T__12);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TuplePatternElementContext extends ParserRuleContext {
		public List<IdentifierContext> identifier() {
			return getRuleContexts(IdentifierContext.class);
		}
		public IdentifierContext identifier(int i) {
			return getRuleContext(IdentifierContext.class,i);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TuplePatternElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tuplePatternElement; }
	}

	public final TuplePatternElementContext tuplePatternElement() throws RecognitionException {
		TuplePatternElementContext _localctx = new TuplePatternElementContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_tuplePatternElement);
		try {
			setState(178);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,13,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(173);
				identifier();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(174);
				identifier();
				setState(175);
				match(COLON);
				setState(176);
				identifier();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExpressionContext extends ParserRuleContext {
		public JuxtapositionExprContext juxtapositionExpr() {
			return getRuleContext(JuxtapositionExprContext.class,0);
		}
		public ExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expression; }
	}

	public final ExpressionContext expression() throws RecognitionException {
		ExpressionContext _localctx = new ExpressionContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_expression);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(180);
			juxtapositionExpr();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class JuxtapositionExprContext extends ParserRuleContext {
		public List<LogicalExprContext> logicalExpr() {
			return getRuleContexts(LogicalExprContext.class);
		}
		public LogicalExprContext logicalExpr(int i) {
			return getRuleContext(LogicalExprContext.class,i);
		}
		public JuxtapositionExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_juxtapositionExpr; }
	}

	public final JuxtapositionExprContext juxtapositionExpr() throws RecognitionException {
		JuxtapositionExprContext _localctx = new JuxtapositionExprContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_juxtapositionExpr);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(182);
			logicalExpr();
			setState(186);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(183);
					logicalExpr();
					}
					} 
				}
				setState(188);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalExprContext extends ParserRuleContext {
		public List<ComparisonExprContext> comparisonExpr() {
			return getRuleContexts(ComparisonExprContext.class);
		}
		public ComparisonExprContext comparisonExpr(int i) {
			return getRuleContext(ComparisonExprContext.class,i);
		}
		public List<TerminalNode> AND() { return getTokens(AxisParser.AND); }
		public TerminalNode AND(int i) {
			return getToken(AxisParser.AND, i);
		}
		public List<TerminalNode> OR() { return getTokens(AxisParser.OR); }
		public TerminalNode OR(int i) {
			return getToken(AxisParser.OR, i);
		}
		public LogicalExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalExpr; }
	}

	public final LogicalExprContext logicalExpr() throws RecognitionException {
		LogicalExprContext _localctx = new LogicalExprContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_logicalExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(189);
			comparisonExpr();
			setState(194);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,15,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(190);
					_la = _input.LA(1);
					if ( !(_la==AND || _la==OR) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(191);
					comparisonExpr();
					}
					} 
				}
				setState(196);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,15,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalOpContext extends ParserRuleContext {
		public TerminalNode AND() { return getToken(AxisParser.AND, 0); }
		public TerminalNode OR() { return getToken(AxisParser.OR, 0); }
		public LogicalOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalOp; }
	}

	public final LogicalOpContext logicalOp() throws RecognitionException {
		LogicalOpContext _localctx = new LogicalOpContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_logicalOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(197);
			_la = _input.LA(1);
			if ( !(_la==AND || _la==OR) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ComparisonExprContext extends ParserRuleContext {
		public List<AdditionContext> addition() {
			return getRuleContexts(AdditionContext.class);
		}
		public AdditionContext addition(int i) {
			return getRuleContext(AdditionContext.class,i);
		}
		public List<TerminalNode> EQ() { return getTokens(AxisParser.EQ); }
		public TerminalNode EQ(int i) {
			return getToken(AxisParser.EQ, i);
		}
		public List<TerminalNode> NE() { return getTokens(AxisParser.NE); }
		public TerminalNode NE(int i) {
			return getToken(AxisParser.NE, i);
		}
		public List<TerminalNode> LT() { return getTokens(AxisParser.LT); }
		public TerminalNode LT(int i) {
			return getToken(AxisParser.LT, i);
		}
		public List<TerminalNode> LE() { return getTokens(AxisParser.LE); }
		public TerminalNode LE(int i) {
			return getToken(AxisParser.LE, i);
		}
		public List<TerminalNode> GT() { return getTokens(AxisParser.GT); }
		public TerminalNode GT(int i) {
			return getToken(AxisParser.GT, i);
		}
		public List<TerminalNode> GE() { return getTokens(AxisParser.GE); }
		public TerminalNode GE(int i) {
			return getToken(AxisParser.GE, i);
		}
		public ComparisonExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_comparisonExpr; }
	}

	public final ComparisonExprContext comparisonExpr() throws RecognitionException {
		ComparisonExprContext _localctx = new ComparisonExprContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_comparisonExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(199);
			addition();
			setState(204);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,16,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(200);
					_la = _input.LA(1);
					if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 16911433728L) != 0)) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(201);
					addition();
					}
					} 
				}
				setState(206);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,16,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AdditionContext extends ParserRuleContext {
		public List<ProductContext> product() {
			return getRuleContexts(ProductContext.class);
		}
		public ProductContext product(int i) {
			return getRuleContext(ProductContext.class,i);
		}
		public List<TerminalNode> ADD() { return getTokens(AxisParser.ADD); }
		public TerminalNode ADD(int i) {
			return getToken(AxisParser.ADD, i);
		}
		public List<TerminalNode> SUB() { return getTokens(AxisParser.SUB); }
		public TerminalNode SUB(int i) {
			return getToken(AxisParser.SUB, i);
		}
		public AdditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_addition; }
	}

	public final AdditionContext addition() throws RecognitionException {
		AdditionContext _localctx = new AdditionContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_addition);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(207);
			product();
			setState(212);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(208);
					_la = _input.LA(1);
					if ( !(_la==ADD || _la==SUB) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(209);
					product();
					}
					} 
				}
				setState(214);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProductContext extends ParserRuleContext {
		public List<PostfixContext> postfix() {
			return getRuleContexts(PostfixContext.class);
		}
		public PostfixContext postfix(int i) {
			return getRuleContext(PostfixContext.class,i);
		}
		public List<TerminalNode> MUL() { return getTokens(AxisParser.MUL); }
		public TerminalNode MUL(int i) {
			return getToken(AxisParser.MUL, i);
		}
		public List<TerminalNode> DIV() { return getTokens(AxisParser.DIV); }
		public TerminalNode DIV(int i) {
			return getToken(AxisParser.DIV, i);
		}
		public List<TerminalNode> MOD() { return getTokens(AxisParser.MOD); }
		public TerminalNode MOD(int i) {
			return getToken(AxisParser.MOD, i);
		}
		public ProductContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_product; }
	}

	public final ProductContext product() throws RecognitionException {
		ProductContext _localctx = new ProductContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_product);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(215);
			postfix(0);
			setState(220);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(216);
					_la = _input.LA(1);
					if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 234881024L) != 0)) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(217);
					postfix(0);
					}
					} 
				}
				setState(222);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PostfixContext extends ParserRuleContext {
		public PostfixContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_postfix; }
	 
		public PostfixContext() { }
		public void copyFrom(PostfixContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class CallContext extends PostfixContext {
		public PostfixContext postfix() {
			return getRuleContext(PostfixContext.class,0);
		}
		public TupleContext tuple() {
			return getRuleContext(TupleContext.class,0);
		}
		public CallContext(PostfixContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class PassContext extends PostfixContext {
		public PrimaryExprContext primaryExpr() {
			return getRuleContext(PrimaryExprContext.class,0);
		}
		public PassContext(PostfixContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class MemberAccessContext extends PostfixContext {
		public PostfixContext postfix() {
			return getRuleContext(PostfixContext.class,0);
		}
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public MemberAccessContext(PostfixContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TrailingLambdaContext extends PostfixContext {
		public PostfixContext postfix() {
			return getRuleContext(PostfixContext.class,0);
		}
		public LambdaContext lambda() {
			return getRuleContext(LambdaContext.class,0);
		}
		public TrailingLambdaContext(PostfixContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ScopeAccessContext extends PostfixContext {
		public PostfixContext postfix() {
			return getRuleContext(PostfixContext.class,0);
		}
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public ScopeAccessContext(PostfixContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class IndexContext extends PostfixContext {
		public PostfixContext postfix() {
			return getRuleContext(PostfixContext.class,0);
		}
		public ShapeContext shape() {
			return getRuleContext(ShapeContext.class,0);
		}
		public IndexContext(PostfixContext ctx) { copyFrom(ctx); }
	}

	public final PostfixContext postfix() throws RecognitionException {
		return postfix(0);
	}

	private PostfixContext postfix(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		PostfixContext _localctx = new PostfixContext(_ctx, _parentState);
		PostfixContext _prevctx = _localctx;
		int _startState = 44;
		enterRecursionRule(_localctx, 44, RULE_postfix, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			{
			_localctx = new PassContext(_localctx);
			_ctx = _localctx;
			_prevctx = _localctx;

			setState(224);
			primaryExpr();
			}
			_ctx.stop = _input.LT(-1);
			setState(248);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(246);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,21,_ctx) ) {
					case 1:
						{
						_localctx = new TrailingLambdaContext(new PostfixContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfix);
						setState(226);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(227);
						lambda();
						}
						break;
					case 2:
						{
						_localctx = new CallContext(new PostfixContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfix);
						setState(228);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(229);
						tuple();
						}
						break;
					case 3:
						{
						_localctx = new IndexContext(new PostfixContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfix);
						setState(230);
						if (!(precpred(_ctx, 3))) throw new FailedPredicateException(this, "precpred(_ctx, 3)");
						setState(231);
						shape();
						}
						break;
					case 4:
						{
						_localctx = new MemberAccessContext(new PostfixContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfix);
						setState(232);
						if (!(precpred(_ctx, 2))) throw new FailedPredicateException(this, "precpred(_ctx, 2)");
						setState(235); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(233);
								match(T__13);
								setState(234);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(237); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,19,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					case 5:
						{
						_localctx = new ScopeAccessContext(new PostfixContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfix);
						setState(239);
						if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
						setState(242); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(240);
								match(T__14);
								setState(241);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(244); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,20,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					}
					} 
				}
				setState(250);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PrimaryExprContext extends ParserRuleContext {
		public IdentifierContext identifier() {
			return getRuleContext(IdentifierContext.class,0);
		}
		public LiteralContext literal() {
			return getRuleContext(LiteralContext.class,0);
		}
		public TupleContext tuple() {
			return getRuleContext(TupleContext.class,0);
		}
		public LambdaContext lambda() {
			return getRuleContext(LambdaContext.class,0);
		}
		public SpreadContext spread() {
			return getRuleContext(SpreadContext.class,0);
		}
		public WildcardContext wildcard() {
			return getRuleContext(WildcardContext.class,0);
		}
		public EllipsisContext ellipsis() {
			return getRuleContext(EllipsisContext.class,0);
		}
		public PrimaryExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_primaryExpr; }
	}

	public final PrimaryExprContext primaryExpr() throws RecognitionException {
		PrimaryExprContext _localctx = new PrimaryExprContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_primaryExpr);
		try {
			setState(258);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,23,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(251);
				identifier();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(252);
				literal();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(253);
				tuple();
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(254);
				lambda();
				}
				break;
			case 5:
				enterOuterAlt(_localctx, 5);
				{
				setState(255);
				spread();
				}
				break;
			case 6:
				enterOuterAlt(_localctx, 6);
				{
				setState(256);
				wildcard();
				}
				break;
			case 7:
				enterOuterAlt(_localctx, 7);
				{
				setState(257);
				ellipsis();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class WildcardContext extends ParserRuleContext {
		public TerminalNode WILDCARD() { return getToken(AxisParser.WILDCARD, 0); }
		public WildcardContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_wildcard; }
	}

	public final WildcardContext wildcard() throws RecognitionException {
		WildcardContext _localctx = new WildcardContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_wildcard);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(260);
			match(WILDCARD);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class EllipsisContext extends ParserRuleContext {
		public TerminalNode ELLIPSIS() { return getToken(AxisParser.ELLIPSIS, 0); }
		public EllipsisContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ellipsis; }
	}

	public final EllipsisContext ellipsis() throws RecognitionException {
		EllipsisContext _localctx = new EllipsisContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_ellipsis);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(262);
			match(ELLIPSIS);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SpreadContext extends ParserRuleContext {
		public TerminalNode ELLIPSIS() { return getToken(AxisParser.ELLIPSIS, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public SpreadContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_spread; }
	}

	public final SpreadContext spread() throws RecognitionException {
		SpreadContext _localctx = new SpreadContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_spread);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(264);
			match(ELLIPSIS);
			setState(265);
			expression();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TupleContext extends ParserRuleContext {
		public List<TupleElementContext> tupleElement() {
			return getRuleContexts(TupleElementContext.class);
		}
		public TupleElementContext tupleElement(int i) {
			return getRuleContext(TupleElementContext.class,i);
		}
		public TupleContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tuple; }
	}

	public final TupleContext tuple() throws RecognitionException {
		TupleContext _localctx = new TupleContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_tuple);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(267);
			match(T__10);
			setState(276);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045888L) != 0)) {
				{
				setState(268);
				tupleElement();
				setState(273);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,24,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(269);
						match(T__11);
						setState(270);
						tupleElement();
						}
						} 
					}
					setState(275);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,24,_ctx);
				}
				}
			}

			setState(279);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__11) {
				{
				setState(278);
				match(T__11);
				}
			}

			setState(281);
			match(T__12);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ShapeContext extends ParserRuleContext {
		public List<TupleElementContext> tupleElement() {
			return getRuleContexts(TupleElementContext.class);
		}
		public TupleElementContext tupleElement(int i) {
			return getRuleContext(TupleElementContext.class,i);
		}
		public ShapeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_shape; }
	}

	public final ShapeContext shape() throws RecognitionException {
		ShapeContext _localctx = new ShapeContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_shape);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(283);
			match(T__15);
			setState(292);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045888L) != 0)) {
				{
				setState(284);
				tupleElement();
				setState(289);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,27,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(285);
						match(T__11);
						setState(286);
						tupleElement();
						}
						} 
					}
					setState(291);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,27,_ctx);
				}
				}
			}

			setState(295);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__11) {
				{
				setState(294);
				match(T__11);
				}
			}

			setState(297);
			match(T__16);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TupleElementContext extends ParserRuleContext {
		public TupleElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleElement; }
	 
		public TupleElementContext() { }
		public void copyFrom(TupleElementContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TupleElementSingleContext extends TupleElementContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TupleElementSingleContext(TupleElementContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TupleElementBoundedAssignationContext extends TupleElementContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TerminalNode ASSIGN() { return getToken(AxisParser.ASSIGN, 0); }
		public TupleElementBoundedAssignationContext(TupleElementContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TupleElementAssignationContext extends TupleElementContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode ASSIGN() { return getToken(AxisParser.ASSIGN, 0); }
		public TupleElementAssignationContext(TupleElementContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TupleElementBoundedContext extends TupleElementContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public TupleElementBoundedContext(TupleElementContext ctx) { copyFrom(ctx); }
	}

	public final TupleElementContext tupleElement() throws RecognitionException {
		TupleElementContext _localctx = new TupleElementContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_tupleElement);
		try {
			setState(314);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,30,_ctx) ) {
			case 1:
				_localctx = new TupleElementSingleContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(299);
				expression();
				}
				break;
			case 2:
				_localctx = new TupleElementAssignationContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(300);
				expression();
				setState(301);
				match(ASSIGN);
				setState(302);
				expression();
				}
				break;
			case 3:
				_localctx = new TupleElementBoundedContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(304);
				expression();
				setState(305);
				match(COLON);
				setState(306);
				expression();
				}
				break;
			case 4:
				_localctx = new TupleElementBoundedAssignationContext(_localctx);
				enterOuterAlt(_localctx, 4);
				{
				setState(308);
				expression();
				setState(309);
				match(COLON);
				setState(310);
				expression();
				setState(311);
				match(ASSIGN);
				setState(312);
				expression();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LambdaContext extends ParserRuleContext {
		public LambdaContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lambda; }
	 
		public LambdaContext() { }
		public void copyFrom(LambdaContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class BasicSuiteContext extends LambdaContext {
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public SemicolonContext semicolon() {
			return getRuleContext(SemicolonContext.class,0);
		}
		public BasicSuiteContext(LambdaContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LambdaSuiteContext extends LambdaContext {
		public TerminalNode ARROW() { return getToken(AxisParser.ARROW, 0); }
		public LambdaParamsContext lambdaParams() {
			return getRuleContext(LambdaParamsContext.class,0);
		}
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public LambdaSuiteContext(LambdaContext ctx) { copyFrom(ctx); }
	}

	public final LambdaContext lambda() throws RecognitionException {
		LambdaContext _localctx = new LambdaContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_lambda);
		int _la;
		try {
			int _alt;
			setState(345);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,37,_ctx) ) {
			case 1:
				_localctx = new LambdaSuiteContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(316);
				match(T__17);
				setState(318);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==ID) {
					{
					setState(317);
					lambdaParams();
					}
				}

				setState(320);
				match(ARROW);
				setState(324);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,32,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(321);
						statement();
						}
						} 
					}
					setState(326);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,32,_ctx);
				}
				setState(328);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045888L) != 0)) {
					{
					setState(327);
					expression();
					}
				}

				setState(330);
				match(T__18);
				}
				break;
			case 2:
				_localctx = new BasicSuiteContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(331);
				match(T__17);
				setState(335);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,34,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(332);
						statement();
						}
						} 
					}
					setState(337);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,34,_ctx);
				}
				setState(339);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 1649275045888L) != 0)) {
					{
					setState(338);
					expression();
					}
				}

				setState(342);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__4) {
					{
					setState(341);
					semicolon();
					}
				}

				setState(344);
				match(T__18);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SemicolonContext extends ParserRuleContext {
		public SemicolonContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_semicolon; }
	}

	public final SemicolonContext semicolon() throws RecognitionException {
		SemicolonContext _localctx = new SemicolonContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_semicolon);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(347);
			match(T__4);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LambdaParamsContext extends ParserRuleContext {
		public List<LambdaParamContext> lambdaParam() {
			return getRuleContexts(LambdaParamContext.class);
		}
		public LambdaParamContext lambdaParam(int i) {
			return getRuleContext(LambdaParamContext.class,i);
		}
		public LambdaParamsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lambdaParams; }
	}

	public final LambdaParamsContext lambdaParams() throws RecognitionException {
		LambdaParamsContext _localctx = new LambdaParamsContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_lambdaParams);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(349);
			lambdaParam();
			setState(354);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,38,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(350);
					match(T__11);
					setState(351);
					lambdaParam();
					}
					} 
				}
				setState(356);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,38,_ctx);
			}
			setState(358);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__11) {
				{
				setState(357);
				match(T__11);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LambdaParamContext extends ParserRuleContext {
		public IdentifierContext identifier() {
			return getRuleContext(IdentifierContext.class,0);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public LambdaParamContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lambdaParam; }
	}

	public final LambdaParamContext lambdaParam() throws RecognitionException {
		LambdaParamContext _localctx = new LambdaParamContext(_ctx, getState());
		enterRule(_localctx, 66, RULE_lambdaParam);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(360);
			identifier();
			setState(363);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==COLON) {
				{
				setState(361);
				match(COLON);
				setState(362);
				expression();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArgumentContext extends ParserRuleContext {
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public IdentifierContext identifier() {
			return getRuleContext(IdentifierContext.class,0);
		}
		public TerminalNode COLON() { return getToken(AxisParser.COLON, 0); }
		public ArgumentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argument; }
	}

	public final ArgumentContext argument() throws RecognitionException {
		ArgumentContext _localctx = new ArgumentContext(_ctx, getState());
		enterRule(_localctx, 68, RULE_argument);
		try {
			setState(370);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,41,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(365);
				expression();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(366);
				identifier();
				setState(367);
				match(COLON);
				setState(368);
				expression();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IdentifierContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(AxisParser.ID, 0); }
		public IdentifierContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_identifier; }
	}

	public final IdentifierContext identifier() throws RecognitionException {
		IdentifierContext _localctx = new IdentifierContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_identifier);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(372);
			match(ID);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LiteralContext extends ParserRuleContext {
		public DecimalContext decimal() {
			return getRuleContext(DecimalContext.class,0);
		}
		public TextContext text() {
			return getRuleContext(TextContext.class,0);
		}
		public LiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_literal; }
	}

	public final LiteralContext literal() throws RecognitionException {
		LiteralContext _localctx = new LiteralContext(_ctx, getState());
		enterRule(_localctx, 72, RULE_literal);
		try {
			setState(376);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case DECIMAL:
				enterOuterAlt(_localctx, 1);
				{
				setState(374);
				decimal();
				}
				break;
			case TEXT:
				enterOuterAlt(_localctx, 2);
				{
				setState(375);
				text();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TextContext extends ParserRuleContext {
		public TerminalNode TEXT() { return getToken(AxisParser.TEXT, 0); }
		public TextContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_text; }
	}

	public final TextContext text() throws RecognitionException {
		TextContext _localctx = new TextContext(_ctx, getState());
		enterRule(_localctx, 74, RULE_text);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(378);
			match(TEXT);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class DecimalContext extends ParserRuleContext {
		public TerminalNode DECIMAL() { return getToken(AxisParser.DECIMAL, 0); }
		public DecimalContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_decimal; }
	}

	public final DecimalContext decimal() throws RecognitionException {
		DecimalContext _localctx = new DecimalContext(_ctx, getState());
		enterRule(_localctx, 76, RULE_decimal);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(380);
			match(DECIMAL);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 22:
			return postfix_sempred((PostfixContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean postfix_sempred(PostfixContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 5);
		case 1:
			return precpred(_ctx, 4);
		case 2:
			return precpred(_ctx, 3);
		case 3:
			return precpred(_ctx, 2);
		case 4:
			return precpred(_ctx, 1);
		}
		return true;
	}

	public static final String _serializedATN =
		"\u0004\u0001*\u017f\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
		"\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004\u0007\u0004\u0002"+
		"\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002\u0007\u0007\u0007\u0002"+
		"\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0002\u000b\u0007\u000b\u0002"+
		"\f\u0007\f\u0002\r\u0007\r\u0002\u000e\u0007\u000e\u0002\u000f\u0007\u000f"+
		"\u0002\u0010\u0007\u0010\u0002\u0011\u0007\u0011\u0002\u0012\u0007\u0012"+
		"\u0002\u0013\u0007\u0013\u0002\u0014\u0007\u0014\u0002\u0015\u0007\u0015"+
		"\u0002\u0016\u0007\u0016\u0002\u0017\u0007\u0017\u0002\u0018\u0007\u0018"+
		"\u0002\u0019\u0007\u0019\u0002\u001a\u0007\u001a\u0002\u001b\u0007\u001b"+
		"\u0002\u001c\u0007\u001c\u0002\u001d\u0007\u001d\u0002\u001e\u0007\u001e"+
		"\u0002\u001f\u0007\u001f\u0002 \u0007 \u0002!\u0007!\u0002\"\u0007\"\u0002"+
		"#\u0007#\u0002$\u0007$\u0002%\u0007%\u0002&\u0007&\u0001\u0000\u0001\u0000"+
		"\u0001\u0000\u0001\u0000\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001"+
		"\u0001\u0002\u0001\u0002\u0001\u0002\u0001\u0002\u0001\u0003\u0001\u0003"+
		"\u0001\u0003\u0001\u0003\u0003\u0003_\b\u0003\u0001\u0003\u0001\u0003"+
		"\u0003\u0003c\b\u0003\u0001\u0003\u0003\u0003f\b\u0003\u0001\u0003\u0001"+
		"\u0003\u0001\u0004\u0001\u0004\u0001\u0004\u0001\u0004\u0001\u0005\u0001"+
		"\u0005\u0003\u0005p\b\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001"+
		"\u0006\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0007\u0001\u0007\u0001"+
		"\u0007\u0001\u0007\u0001\b\u0001\b\u0005\b\u007f\b\b\n\b\f\b\u0082\t\b"+
		"\u0001\b\u0001\b\u0001\t\u0005\t\u0087\b\t\n\t\f\t\u008a\t\t\u0001\n\u0001"+
		"\n\u0003\n\u008e\b\n\u0001\u000b\u0001\u000b\u0001\u000b\u0001\u000b\u0003"+
		"\u000b\u0094\b\u000b\u0001\u000b\u0001\u000b\u0003\u000b\u0098\b\u000b"+
		"\u0001\u000b\u0003\u000b\u009b\b\u000b\u0001\f\u0001\f\u0003\f\u009f\b"+
		"\f\u0001\r\u0001\r\u0001\r\u0001\r\u0005\r\u00a5\b\r\n\r\f\r\u00a8\t\r"+
		"\u0003\r\u00aa\b\r\u0001\r\u0001\r\u0001\u000e\u0001\u000e\u0001\u000e"+
		"\u0001\u000e\u0001\u000e\u0003\u000e\u00b3\b\u000e\u0001\u000f\u0001\u000f"+
		"\u0001\u0010\u0001\u0010\u0005\u0010\u00b9\b\u0010\n\u0010\f\u0010\u00bc"+
		"\t\u0010\u0001\u0011\u0001\u0011\u0001\u0011\u0005\u0011\u00c1\b\u0011"+
		"\n\u0011\f\u0011\u00c4\t\u0011\u0001\u0012\u0001\u0012\u0001\u0013\u0001"+
		"\u0013\u0001\u0013\u0005\u0013\u00cb\b\u0013\n\u0013\f\u0013\u00ce\t\u0013"+
		"\u0001\u0014\u0001\u0014\u0001\u0014\u0005\u0014\u00d3\b\u0014\n\u0014"+
		"\f\u0014\u00d6\t\u0014\u0001\u0015\u0001\u0015\u0001\u0015\u0005\u0015"+
		"\u00db\b\u0015\n\u0015\f\u0015\u00de\t\u0015\u0001\u0016\u0001\u0016\u0001"+
		"\u0016\u0001\u0016\u0001\u0016\u0001\u0016\u0001\u0016\u0001\u0016\u0001"+
		"\u0016\u0001\u0016\u0001\u0016\u0001\u0016\u0004\u0016\u00ec\b\u0016\u000b"+
		"\u0016\f\u0016\u00ed\u0001\u0016\u0001\u0016\u0001\u0016\u0004\u0016\u00f3"+
		"\b\u0016\u000b\u0016\f\u0016\u00f4\u0005\u0016\u00f7\b\u0016\n\u0016\f"+
		"\u0016\u00fa\t\u0016\u0001\u0017\u0001\u0017\u0001\u0017\u0001\u0017\u0001"+
		"\u0017\u0001\u0017\u0001\u0017\u0003\u0017\u0103\b\u0017\u0001\u0018\u0001"+
		"\u0018\u0001\u0019\u0001\u0019\u0001\u001a\u0001\u001a\u0001\u001a\u0001"+
		"\u001b\u0001\u001b\u0001\u001b\u0001\u001b\u0005\u001b\u0110\b\u001b\n"+
		"\u001b\f\u001b\u0113\t\u001b\u0003\u001b\u0115\b\u001b\u0001\u001b\u0003"+
		"\u001b\u0118\b\u001b\u0001\u001b\u0001\u001b\u0001\u001c\u0001\u001c\u0001"+
		"\u001c\u0001\u001c\u0005\u001c\u0120\b\u001c\n\u001c\f\u001c\u0123\t\u001c"+
		"\u0003\u001c\u0125\b\u001c\u0001\u001c\u0003\u001c\u0128\b\u001c\u0001"+
		"\u001c\u0001\u001c\u0001\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0001"+
		"\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0001"+
		"\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0001\u001d\u0003\u001d\u013b"+
		"\b\u001d\u0001\u001e\u0001\u001e\u0003\u001e\u013f\b\u001e\u0001\u001e"+
		"\u0001\u001e\u0005\u001e\u0143\b\u001e\n\u001e\f\u001e\u0146\t\u001e\u0001"+
		"\u001e\u0003\u001e\u0149\b\u001e\u0001\u001e\u0001\u001e\u0001\u001e\u0005"+
		"\u001e\u014e\b\u001e\n\u001e\f\u001e\u0151\t\u001e\u0001\u001e\u0003\u001e"+
		"\u0154\b\u001e\u0001\u001e\u0003\u001e\u0157\b\u001e\u0001\u001e\u0003"+
		"\u001e\u015a\b\u001e\u0001\u001f\u0001\u001f\u0001 \u0001 \u0001 \u0005"+
		" \u0161\b \n \f \u0164\t \u0001 \u0003 \u0167\b \u0001!\u0001!\u0001!"+
		"\u0003!\u016c\b!\u0001\"\u0001\"\u0001\"\u0001\"\u0001\"\u0003\"\u0173"+
		"\b\"\u0001#\u0001#\u0001$\u0001$\u0003$\u0179\b$\u0001%\u0001%\u0001&"+
		"\u0001&\u0001&\u0000\u0001,\'\u0000\u0002\u0004\u0006\b\n\f\u000e\u0010"+
		"\u0012\u0014\u0016\u0018\u001a\u001c\u001e \"$&(*,.02468:<>@BDFHJL\u0000"+
		"\u0004\u0001\u0000\"#\u0001\u0000\u001c!\u0001\u0000\u0017\u0018\u0001"+
		"\u0000\u0019\u001b\u018c\u0000N\u0001\u0000\u0000\u0000\u0002R\u0001\u0000"+
		"\u0000\u0000\u0004V\u0001\u0000\u0000\u0000\u0006Z\u0001\u0000\u0000\u0000"+
		"\bi\u0001\u0000\u0000\u0000\nm\u0001\u0000\u0000\u0000\ft\u0001\u0000"+
		"\u0000\u0000\u000ex\u0001\u0000\u0000\u0000\u0010|\u0001\u0000\u0000\u0000"+
		"\u0012\u0088\u0001\u0000\u0000\u0000\u0014\u008d\u0001\u0000\u0000\u0000"+
		"\u0016\u008f\u0001\u0000\u0000\u0000\u0018\u009e\u0001\u0000\u0000\u0000"+
		"\u001a\u00a0\u0001\u0000\u0000\u0000\u001c\u00b2\u0001\u0000\u0000\u0000"+
		"\u001e\u00b4\u0001\u0000\u0000\u0000 \u00b6\u0001\u0000\u0000\u0000\""+
		"\u00bd\u0001\u0000\u0000\u0000$\u00c5\u0001\u0000\u0000\u0000&\u00c7\u0001"+
		"\u0000\u0000\u0000(\u00cf\u0001\u0000\u0000\u0000*\u00d7\u0001\u0000\u0000"+
		"\u0000,\u00df\u0001\u0000\u0000\u0000.\u0102\u0001\u0000\u0000\u00000"+
		"\u0104\u0001\u0000\u0000\u00002\u0106\u0001\u0000\u0000\u00004\u0108\u0001"+
		"\u0000\u0000\u00006\u010b\u0001\u0000\u0000\u00008\u011b\u0001\u0000\u0000"+
		"\u0000:\u013a\u0001\u0000\u0000\u0000<\u0159\u0001\u0000\u0000\u0000>"+
		"\u015b\u0001\u0000\u0000\u0000@\u015d\u0001\u0000\u0000\u0000B\u0168\u0001"+
		"\u0000\u0000\u0000D\u0172\u0001\u0000\u0000\u0000F\u0174\u0001\u0000\u0000"+
		"\u0000H\u0178\u0001\u0000\u0000\u0000J\u017a\u0001\u0000\u0000\u0000L"+
		"\u017c\u0001\u0000\u0000\u0000NO\u0005\u0001\u0000\u0000OP\u0003\u001e"+
		"\u000f\u0000PQ\u0005\u0000\u0000\u0001Q\u0001\u0001\u0000\u0000\u0000"+
		"RS\u0005\u0002\u0000\u0000ST\u0003\u001e\u000f\u0000TU\u0005\u0000\u0000"+
		"\u0001U\u0003\u0001\u0000\u0000\u0000VW\u0005\u0003\u0000\u0000WX\u0003"+
		"\u001e\u000f\u0000XY\u0005\u0000\u0000\u0001Y\u0005\u0001\u0000\u0000"+
		"\u0000Z[\u0005\u0004\u0000\u0000[^\u0003\u001e\u000f\u0000\\]\u0005$\u0000"+
		"\u0000]_\u0003\u001e\u000f\u0000^\\\u0001\u0000\u0000\u0000^_\u0001\u0000"+
		"\u0000\u0000_b\u0001\u0000\u0000\u0000`a\u0005%\u0000\u0000ac\u0003\u001e"+
		"\u000f\u0000b`\u0001\u0000\u0000\u0000bc\u0001\u0000\u0000\u0000ce\u0001"+
		"\u0000\u0000\u0000df\u0005\u0005\u0000\u0000ed\u0001\u0000\u0000\u0000"+
		"ef\u0001\u0000\u0000\u0000fg\u0001\u0000\u0000\u0000gh\u0005\u0000\u0000"+
		"\u0001h\u0007\u0001\u0000\u0000\u0000ij\u0005\u0006\u0000\u0000jk\u0003"+
		"\u001e\u000f\u0000kl\u0005\u0000\u0000\u0001l\t\u0001\u0000\u0000\u0000"+
		"mo\u0005\u0007\u0000\u0000np\u0005\u0014\u0000\u0000on\u0001\u0000\u0000"+
		"\u0000op\u0001\u0000\u0000\u0000pq\u0001\u0000\u0000\u0000qr\u0005$\u0000"+
		"\u0000rs\u0005\u0000\u0000\u0001s\u000b\u0001\u0000\u0000\u0000tu\u0005"+
		"\b\u0000\u0000uv\u0005$\u0000\u0000vw\u0005\u0000\u0000\u0001w\r\u0001"+
		"\u0000\u0000\u0000xy\u0005\t\u0000\u0000yz\u0003\u001e\u000f\u0000z{\u0005"+
		"\u0000\u0000\u0001{\u000f\u0001\u0000\u0000\u0000|\u0080\u0005\n\u0000"+
		"\u0000}\u007f\u0003\u0014\n\u0000~}\u0001\u0000\u0000\u0000\u007f\u0082"+
		"\u0001\u0000\u0000\u0000\u0080~\u0001\u0000\u0000\u0000\u0080\u0081\u0001"+
		"\u0000\u0000\u0000\u0081\u0083\u0001\u0000\u0000\u0000\u0082\u0080\u0001"+
		"\u0000\u0000\u0000\u0083\u0084\u0005\u0000\u0000\u0001\u0084\u0011\u0001"+
		"\u0000\u0000\u0000\u0085\u0087\u0003\u0014\n\u0000\u0086\u0085\u0001\u0000"+
		"\u0000\u0000\u0087\u008a\u0001\u0000\u0000\u0000\u0088\u0086\u0001\u0000"+
		"\u0000\u0000\u0088\u0089\u0001\u0000\u0000\u0000\u0089\u0013\u0001\u0000"+
		"\u0000\u0000\u008a\u0088\u0001\u0000\u0000\u0000\u008b\u008e\u0003\u0016"+
		"\u000b\u0000\u008c\u008e\u0003\u001e\u000f\u0000\u008d\u008b\u0001\u0000"+
		"\u0000\u0000\u008d\u008c\u0001\u0000\u0000\u0000\u008e\u0015\u0001\u0000"+
		"\u0000\u0000\u008f\u0090\u0005\u0004\u0000\u0000\u0090\u0093\u0003\u0018"+
		"\f\u0000\u0091\u0092\u0005$\u0000\u0000\u0092\u0094\u0003\u001e\u000f"+
		"\u0000\u0093\u0091\u0001\u0000\u0000\u0000\u0093\u0094\u0001\u0000\u0000"+
		"\u0000\u0094\u0097\u0001\u0000\u0000\u0000\u0095\u0096\u0005%\u0000\u0000"+
		"\u0096\u0098\u0003\u001e\u000f\u0000\u0097\u0095\u0001\u0000\u0000\u0000"+
		"\u0097\u0098\u0001\u0000\u0000\u0000\u0098\u009a\u0001\u0000\u0000\u0000"+
		"\u0099\u009b\u0005\u0005\u0000\u0000\u009a\u0099\u0001\u0000\u0000\u0000"+
		"\u009a\u009b\u0001\u0000\u0000\u0000\u009b\u0017\u0001\u0000\u0000\u0000"+
		"\u009c\u009f\u0003F#\u0000\u009d\u009f\u0003\u001a\r\u0000\u009e\u009c"+
		"\u0001\u0000\u0000\u0000\u009e\u009d\u0001\u0000\u0000\u0000\u009f\u0019"+
		"\u0001\u0000\u0000\u0000\u00a0\u00a9\u0005\u000b\u0000\u0000\u00a1\u00a6"+
		"\u0003\u001c\u000e\u0000\u00a2\u00a3\u0005\f\u0000\u0000\u00a3\u00a5\u0003"+
		"\u001c\u000e\u0000\u00a4\u00a2\u0001\u0000\u0000\u0000\u00a5\u00a8\u0001"+
		"\u0000\u0000\u0000\u00a6\u00a4\u0001\u0000\u0000\u0000\u00a6\u00a7\u0001"+
		"\u0000\u0000\u0000\u00a7\u00aa\u0001\u0000\u0000\u0000\u00a8\u00a6\u0001"+
		"\u0000\u0000\u0000\u00a9\u00a1\u0001\u0000\u0000\u0000\u00a9\u00aa\u0001"+
		"\u0000\u0000\u0000\u00aa\u00ab\u0001\u0000\u0000\u0000\u00ab\u00ac\u0005"+
		"\r\u0000\u0000\u00ac\u001b\u0001\u0000\u0000\u0000\u00ad\u00b3\u0003F"+
		"#\u0000\u00ae\u00af\u0003F#\u0000\u00af\u00b0\u0005$\u0000\u0000\u00b0"+
		"\u00b1\u0003F#\u0000\u00b1\u00b3\u0001\u0000\u0000\u0000\u00b2\u00ad\u0001"+
		"\u0000\u0000\u0000\u00b2\u00ae\u0001\u0000\u0000\u0000\u00b3\u001d\u0001"+
		"\u0000\u0000\u0000\u00b4\u00b5\u0003 \u0010\u0000\u00b5\u001f\u0001\u0000"+
		"\u0000\u0000\u00b6\u00ba\u0003\"\u0011\u0000\u00b7\u00b9\u0003\"\u0011"+
		"\u0000\u00b8\u00b7\u0001\u0000\u0000\u0000\u00b9\u00bc\u0001\u0000\u0000"+
		"\u0000\u00ba\u00b8\u0001\u0000\u0000\u0000\u00ba\u00bb\u0001\u0000\u0000"+
		"\u0000\u00bb!\u0001\u0000\u0000\u0000\u00bc\u00ba\u0001\u0000\u0000\u0000"+
		"\u00bd\u00c2\u0003&\u0013\u0000\u00be\u00bf\u0007\u0000\u0000\u0000\u00bf"+
		"\u00c1\u0003&\u0013\u0000\u00c0\u00be\u0001\u0000\u0000\u0000\u00c1\u00c4"+
		"\u0001\u0000\u0000\u0000\u00c2\u00c0\u0001\u0000\u0000\u0000\u00c2\u00c3"+
		"\u0001\u0000\u0000\u0000\u00c3#\u0001\u0000\u0000\u0000\u00c4\u00c2\u0001"+
		"\u0000\u0000\u0000\u00c5\u00c6\u0007\u0000\u0000\u0000\u00c6%\u0001\u0000"+
		"\u0000\u0000\u00c7\u00cc\u0003(\u0014\u0000\u00c8\u00c9\u0007\u0001\u0000"+
		"\u0000\u00c9\u00cb\u0003(\u0014\u0000\u00ca\u00c8\u0001\u0000\u0000\u0000"+
		"\u00cb\u00ce\u0001\u0000\u0000\u0000\u00cc\u00ca\u0001\u0000\u0000\u0000"+
		"\u00cc\u00cd\u0001\u0000\u0000\u0000\u00cd\'\u0001\u0000\u0000\u0000\u00ce"+
		"\u00cc\u0001\u0000\u0000\u0000\u00cf\u00d4\u0003*\u0015\u0000\u00d0\u00d1"+
		"\u0007\u0002\u0000\u0000\u00d1\u00d3\u0003*\u0015\u0000\u00d2\u00d0\u0001"+
		"\u0000\u0000\u0000\u00d3\u00d6\u0001\u0000\u0000\u0000\u00d4\u00d2\u0001"+
		"\u0000\u0000\u0000\u00d4\u00d5\u0001\u0000\u0000\u0000\u00d5)\u0001\u0000"+
		"\u0000\u0000\u00d6\u00d4\u0001\u0000\u0000\u0000\u00d7\u00dc\u0003,\u0016"+
		"\u0000\u00d8\u00d9\u0007\u0003\u0000\u0000\u00d9\u00db\u0003,\u0016\u0000"+
		"\u00da\u00d8\u0001\u0000\u0000\u0000\u00db\u00de\u0001\u0000\u0000\u0000"+
		"\u00dc\u00da\u0001\u0000\u0000\u0000\u00dc\u00dd\u0001\u0000\u0000\u0000"+
		"\u00dd+\u0001\u0000\u0000\u0000\u00de\u00dc\u0001\u0000\u0000\u0000\u00df"+
		"\u00e0\u0006\u0016\uffff\uffff\u0000\u00e0\u00e1\u0003.\u0017\u0000\u00e1"+
		"\u00f8\u0001\u0000\u0000\u0000\u00e2\u00e3\n\u0005\u0000\u0000\u00e3\u00f7"+
		"\u0003<\u001e\u0000\u00e4\u00e5\n\u0004\u0000\u0000\u00e5\u00f7\u0003"+
		"6\u001b\u0000\u00e6\u00e7\n\u0003\u0000\u0000\u00e7\u00f7\u00038\u001c"+
		"\u0000\u00e8\u00eb\n\u0002\u0000\u0000\u00e9\u00ea\u0005\u000e\u0000\u0000"+
		"\u00ea\u00ec\u0005\u0014\u0000\u0000\u00eb\u00e9\u0001\u0000\u0000\u0000"+
		"\u00ec\u00ed\u0001\u0000\u0000\u0000\u00ed\u00eb\u0001\u0000\u0000\u0000"+
		"\u00ed\u00ee\u0001\u0000\u0000\u0000\u00ee\u00f7\u0001\u0000\u0000\u0000"+
		"\u00ef\u00f2\n\u0001\u0000\u0000\u00f0\u00f1\u0005\u000f\u0000\u0000\u00f1"+
		"\u00f3\u0005\u0014\u0000\u0000\u00f2\u00f0\u0001\u0000\u0000\u0000\u00f3"+
		"\u00f4\u0001\u0000\u0000\u0000\u00f4\u00f2\u0001\u0000\u0000\u0000\u00f4"+
		"\u00f5\u0001\u0000\u0000\u0000\u00f5\u00f7\u0001\u0000\u0000\u0000\u00f6"+
		"\u00e2\u0001\u0000\u0000\u0000\u00f6\u00e4\u0001\u0000\u0000\u0000\u00f6"+
		"\u00e6\u0001\u0000\u0000\u0000\u00f6\u00e8\u0001\u0000\u0000\u0000\u00f6"+
		"\u00ef\u0001\u0000\u0000\u0000\u00f7\u00fa\u0001\u0000\u0000\u0000\u00f8"+
		"\u00f6\u0001\u0000\u0000\u0000\u00f8\u00f9\u0001\u0000\u0000\u0000\u00f9"+
		"-\u0001\u0000\u0000\u0000\u00fa\u00f8\u0001\u0000\u0000\u0000\u00fb\u0103"+
		"\u0003F#\u0000\u00fc\u0103\u0003H$\u0000\u00fd\u0103\u00036\u001b\u0000"+
		"\u00fe\u0103\u0003<\u001e\u0000\u00ff\u0103\u00034\u001a\u0000\u0100\u0103"+
		"\u00030\u0018\u0000\u0101\u0103\u00032\u0019\u0000\u0102\u00fb\u0001\u0000"+
		"\u0000\u0000\u0102\u00fc\u0001\u0000\u0000\u0000\u0102\u00fd\u0001\u0000"+
		"\u0000\u0000\u0102\u00fe\u0001\u0000\u0000\u0000\u0102\u00ff\u0001\u0000"+
		"\u0000\u0000\u0102\u0100\u0001\u0000\u0000\u0000\u0102\u0101\u0001\u0000"+
		"\u0000\u0000\u0103/\u0001\u0000\u0000\u0000\u0104\u0105\u0005(\u0000\u0000"+
		"\u01051\u0001\u0000\u0000\u0000\u0106\u0107\u0005\'\u0000\u0000\u0107"+
		"3\u0001\u0000\u0000\u0000\u0108\u0109\u0005\'\u0000\u0000\u0109\u010a"+
		"\u0003\u001e\u000f\u0000\u010a5\u0001\u0000\u0000\u0000\u010b\u0114\u0005"+
		"\u000b\u0000\u0000\u010c\u0111\u0003:\u001d\u0000\u010d\u010e\u0005\f"+
		"\u0000\u0000\u010e\u0110\u0003:\u001d\u0000\u010f\u010d\u0001\u0000\u0000"+
		"\u0000\u0110\u0113\u0001\u0000\u0000\u0000\u0111\u010f\u0001\u0000\u0000"+
		"\u0000\u0111\u0112\u0001\u0000\u0000\u0000\u0112\u0115\u0001\u0000\u0000"+
		"\u0000\u0113\u0111\u0001\u0000\u0000\u0000\u0114\u010c\u0001\u0000\u0000"+
		"\u0000\u0114\u0115\u0001\u0000\u0000\u0000\u0115\u0117\u0001\u0000\u0000"+
		"\u0000\u0116\u0118\u0005\f\u0000\u0000\u0117\u0116\u0001\u0000\u0000\u0000"+
		"\u0117\u0118\u0001\u0000\u0000\u0000\u0118\u0119\u0001\u0000\u0000\u0000"+
		"\u0119\u011a\u0005\r\u0000\u0000\u011a7\u0001\u0000\u0000\u0000\u011b"+
		"\u0124\u0005\u0010\u0000\u0000\u011c\u0121\u0003:\u001d\u0000\u011d\u011e"+
		"\u0005\f\u0000\u0000\u011e\u0120\u0003:\u001d\u0000\u011f\u011d\u0001"+
		"\u0000\u0000\u0000\u0120\u0123\u0001\u0000\u0000\u0000\u0121\u011f\u0001"+
		"\u0000\u0000\u0000\u0121\u0122\u0001\u0000\u0000\u0000\u0122\u0125\u0001"+
		"\u0000\u0000\u0000\u0123\u0121\u0001\u0000\u0000\u0000\u0124\u011c\u0001"+
		"\u0000\u0000\u0000\u0124\u0125\u0001\u0000\u0000\u0000\u0125\u0127\u0001"+
		"\u0000\u0000\u0000\u0126\u0128\u0005\f\u0000\u0000\u0127\u0126\u0001\u0000"+
		"\u0000\u0000\u0127\u0128\u0001\u0000\u0000\u0000\u0128\u0129\u0001\u0000"+
		"\u0000\u0000\u0129\u012a\u0005\u0011\u0000\u0000\u012a9\u0001\u0000\u0000"+
		"\u0000\u012b\u013b\u0003\u001e\u000f\u0000\u012c\u012d\u0003\u001e\u000f"+
		"\u0000\u012d\u012e\u0005%\u0000\u0000\u012e\u012f\u0003\u001e\u000f\u0000"+
		"\u012f\u013b\u0001\u0000\u0000\u0000\u0130\u0131\u0003\u001e\u000f\u0000"+
		"\u0131\u0132\u0005$\u0000\u0000\u0132\u0133\u0003\u001e\u000f\u0000\u0133"+
		"\u013b\u0001\u0000\u0000\u0000\u0134\u0135\u0003\u001e\u000f\u0000\u0135"+
		"\u0136\u0005$\u0000\u0000\u0136\u0137\u0003\u001e\u000f\u0000\u0137\u0138"+
		"\u0005%\u0000\u0000\u0138\u0139\u0003\u001e\u000f\u0000\u0139\u013b\u0001"+
		"\u0000\u0000\u0000\u013a\u012b\u0001\u0000\u0000\u0000\u013a\u012c\u0001"+
		"\u0000\u0000\u0000\u013a\u0130\u0001\u0000\u0000\u0000\u013a\u0134\u0001"+
		"\u0000\u0000\u0000\u013b;\u0001\u0000\u0000\u0000\u013c\u013e\u0005\u0012"+
		"\u0000\u0000\u013d\u013f\u0003@ \u0000\u013e\u013d\u0001\u0000\u0000\u0000"+
		"\u013e\u013f\u0001\u0000\u0000\u0000\u013f\u0140\u0001\u0000\u0000\u0000"+
		"\u0140\u0144\u0005&\u0000\u0000\u0141\u0143\u0003\u0014\n\u0000\u0142"+
		"\u0141\u0001\u0000\u0000\u0000\u0143\u0146\u0001\u0000\u0000\u0000\u0144"+
		"\u0142\u0001\u0000\u0000\u0000\u0144\u0145\u0001\u0000\u0000\u0000\u0145"+
		"\u0148\u0001\u0000\u0000\u0000\u0146\u0144\u0001\u0000\u0000\u0000\u0147"+
		"\u0149\u0003\u001e\u000f\u0000\u0148\u0147\u0001\u0000\u0000\u0000\u0148"+
		"\u0149\u0001\u0000\u0000\u0000\u0149\u014a\u0001\u0000\u0000\u0000\u014a"+
		"\u015a\u0005\u0013\u0000\u0000\u014b\u014f\u0005\u0012\u0000\u0000\u014c"+
		"\u014e\u0003\u0014\n\u0000\u014d\u014c\u0001\u0000\u0000\u0000\u014e\u0151"+
		"\u0001\u0000\u0000\u0000\u014f\u014d\u0001\u0000\u0000\u0000\u014f\u0150"+
		"\u0001\u0000\u0000\u0000\u0150\u0153\u0001\u0000\u0000\u0000\u0151\u014f"+
		"\u0001\u0000\u0000\u0000\u0152\u0154\u0003\u001e\u000f\u0000\u0153\u0152"+
		"\u0001\u0000\u0000\u0000\u0153\u0154\u0001\u0000\u0000\u0000\u0154\u0156"+
		"\u0001\u0000\u0000\u0000\u0155\u0157\u0003>\u001f\u0000\u0156\u0155\u0001"+
		"\u0000\u0000\u0000\u0156\u0157\u0001\u0000\u0000\u0000\u0157\u0158\u0001"+
		"\u0000\u0000\u0000\u0158\u015a\u0005\u0013\u0000\u0000\u0159\u013c\u0001"+
		"\u0000\u0000\u0000\u0159\u014b\u0001\u0000\u0000\u0000\u015a=\u0001\u0000"+
		"\u0000\u0000\u015b\u015c\u0005\u0005\u0000\u0000\u015c?\u0001\u0000\u0000"+
		"\u0000\u015d\u0162\u0003B!\u0000\u015e\u015f\u0005\f\u0000\u0000\u015f"+
		"\u0161\u0003B!\u0000\u0160\u015e\u0001\u0000\u0000\u0000\u0161\u0164\u0001"+
		"\u0000\u0000\u0000\u0162\u0160\u0001\u0000\u0000\u0000\u0162\u0163\u0001"+
		"\u0000\u0000\u0000\u0163\u0166\u0001\u0000\u0000\u0000\u0164\u0162\u0001"+
		"\u0000\u0000\u0000\u0165\u0167\u0005\f\u0000\u0000\u0166\u0165\u0001\u0000"+
		"\u0000\u0000\u0166\u0167\u0001\u0000\u0000\u0000\u0167A\u0001\u0000\u0000"+
		"\u0000\u0168\u016b\u0003F#\u0000\u0169\u016a\u0005$\u0000\u0000\u016a"+
		"\u016c\u0003\u001e\u000f\u0000\u016b\u0169\u0001\u0000\u0000\u0000\u016b"+
		"\u016c\u0001\u0000\u0000\u0000\u016cC\u0001\u0000\u0000\u0000\u016d\u0173"+
		"\u0003\u001e\u000f\u0000\u016e\u016f\u0003F#\u0000\u016f\u0170\u0005$"+
		"\u0000\u0000\u0170\u0171\u0003\u001e\u000f\u0000\u0171\u0173\u0001\u0000"+
		"\u0000\u0000\u0172\u016d\u0001\u0000\u0000\u0000\u0172\u016e\u0001\u0000"+
		"\u0000\u0000\u0173E\u0001\u0000\u0000\u0000\u0174\u0175\u0005\u0014\u0000"+
		"\u0000\u0175G\u0001\u0000\u0000\u0000\u0176\u0179\u0003L&\u0000\u0177"+
		"\u0179\u0003J%\u0000\u0178\u0176\u0001\u0000\u0000\u0000\u0178\u0177\u0001"+
		"\u0000\u0000\u0000\u0179I\u0001\u0000\u0000\u0000\u017a\u017b\u0005\u0016"+
		"\u0000\u0000\u017bK\u0001\u0000\u0000\u0000\u017c\u017d\u0005\u0015\u0000"+
		"\u0000\u017dM\u0001\u0000\u0000\u0000+^beo\u0080\u0088\u008d\u0093\u0097"+
		"\u009a\u009e\u00a6\u00a9\u00b2\u00ba\u00c2\u00cc\u00d4\u00dc\u00ed\u00f4"+
		"\u00f6\u00f8\u0102\u0111\u0114\u0117\u0121\u0124\u0127\u013a\u013e\u0144"+
		"\u0148\u014f\u0153\u0156\u0159\u0162\u0166\u016b\u0172\u0178";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}