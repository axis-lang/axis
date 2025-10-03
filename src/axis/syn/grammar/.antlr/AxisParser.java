// Generated from /home/jdluque/Workspace/prodisign/axis/src/axis/syn/grammar/Axis.g4 by ANTLR 4.13.1
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
		T__17=18, T__18=19, T__19=20, T__20=21, T__21=22, T__22=23, T__23=24, 
		T__24=25, T__25=26, T__26=27, T__27=28, T__28=29, T__29=30, T__30=31, 
		T__31=32, T__32=33, T__33=34, T__34=35, T__35=36, T__36=37, T__37=38, 
		T__38=39, T__39=40, T__40=41, T__41=42, T__42=43, T__43=44, ID=45, DECIMAL=46, 
		TEXT=47, WS=48, COMMENT=49;
	public static final int
		RULE_unitItem = 0, RULE_modItem = 1, RULE_defItem = 2, RULE_valItem = 3, 
		RULE_useBlock = 4, RULE_takesBlock = 5, RULE_whereBlock = 6, RULE_returnsBlock = 7, 
		RULE_suiteBlock = 8, RULE_suite = 9, RULE_statement = 10, RULE_valStatement = 11, 
		RULE_pattern = 12, RULE_tuplePattern = 13, RULE_tuplePatternElement = 14, 
		RULE_expr = 15, RULE_compoundExpr = 16, RULE_rangeExpr = 17, RULE_rangeOp = 18, 
		RULE_logicExpr = 19, RULE_logicOp = 20, RULE_comparisonExpr = 21, RULE_comparisonOp = 22, 
		RULE_additiveExpr = 23, RULE_additiveOp = 24, RULE_productiveExpr = 25, 
		RULE_productiveOp = 26, RULE_prefixExpr = 27, RULE_signOp = 28, RULE_etcOp = 29, 
		RULE_prefixOp = 30, RULE_postfixExpr = 31, RULE_primaryExpr = 32, RULE_ellipsisExpr = 33, 
		RULE_wildcardExpr = 34, RULE_symExpr = 35, RULE_litExpr = 36, RULE_tupleExpr = 37, 
		RULE_shapeExpr = 38, RULE_tupleElement = 39, RULE_tuplePositionalElement = 40, 
		RULE_tupleNominalElement = 41, RULE_tupleSpreadElement = 42, RULE_lambda = 43, 
		RULE_semicolon = 44, RULE_lambdaParams = 45, RULE_lambdaParam = 46;
	private static String[] makeRuleNames() {
		return new String[] {
			"unitItem", "modItem", "defItem", "valItem", "useBlock", "takesBlock", 
			"whereBlock", "returnsBlock", "suiteBlock", "suite", "statement", "valStatement", 
			"pattern", "tuplePattern", "tuplePatternElement", "expr", "compoundExpr", 
			"rangeExpr", "rangeOp", "logicExpr", "logicOp", "comparisonExpr", "comparisonOp", 
			"additiveExpr", "additiveOp", "productiveExpr", "productiveOp", "prefixExpr", 
			"signOp", "etcOp", "prefixOp", "postfixExpr", "primaryExpr", "ellipsisExpr", 
			"wildcardExpr", "symExpr", "litExpr", "tupleExpr", "shapeExpr", "tupleElement", 
			"tuplePositionalElement", "tupleNominalElement", "tupleSpreadElement", 
			"lambda", "semicolon", "lambdaParams", "lambdaParam"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'unit'", "'mod'", "'def'", "'val'", "':'", "'='", "';'", "'use'", 
			"'takes'", "'where'", "'returns'", "'suite'", "'('", "','", "')'", "'..='", 
			"'..<'", "'&&'", "'||'", "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", 
			"'+'", "'-'", "'*'", "'/'", "'%'", "'\\u00B7'", "'~'", "'!'", "'..'", 
			"'.'", "'::'", "'...'", "'_'", "'@'", "'['", "']'", "'{'", "'->'", "'}'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, "ID", "DECIMAL", 
			"TEXT", "WS", "COMMENT"
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
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
			setState(94);
			match(T__0);
			setState(95);
			expr();
			setState(96);
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
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
			setState(98);
			match(T__1);
			setState(99);
			expr();
			setState(100);
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
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
			setState(102);
			match(T__2);
			setState(103);
			expr();
			setState(104);
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
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
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
			setState(106);
			match(T__3);
			setState(107);
			expr();
			setState(110);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(108);
				match(T__4);
				setState(109);
				expr();
				}
			}

			setState(114);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(112);
				match(T__5);
				setState(113);
				expr();
				}
			}

			setState(117);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__6) {
				{
				setState(116);
				match(T__6);
				}
			}

			setState(119);
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
	public static class UseBlockContext extends ParserRuleContext {
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public UseBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_useBlock; }
	}

	public final UseBlockContext useBlock() throws RecognitionException {
		UseBlockContext _localctx = new UseBlockContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_useBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(121);
			match(T__7);
			setState(122);
			expr();
			setState(123);
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
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
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
			setState(125);
			match(T__8);
			setState(127);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
				{
				setState(126);
				expr();
				}
			}

			setState(129);
			match(T__4);
			setState(130);
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
			setState(132);
			match(T__9);
			setState(133);
			match(T__4);
			setState(134);
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
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
			setState(136);
			match(T__10);
			setState(137);
			expr();
			setState(138);
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
			setState(140);
			match(T__11);
			setState(144);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099216L) != 0)) {
				{
				{
				setState(141);
				statement();
				}
				}
				setState(146);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(147);
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
			setState(152);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099216L) != 0)) {
				{
				{
				setState(149);
				statement();
				}
				}
				setState(154);
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
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
			setState(157);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__3:
				enterOuterAlt(_localctx, 1);
				{
				setState(155);
				valStatement();
				}
				break;
			case T__12:
			case T__25:
			case T__26:
			case T__31:
			case T__32:
			case T__33:
			case T__36:
			case T__37:
			case T__41:
			case ID:
			case DECIMAL:
			case TEXT:
				enterOuterAlt(_localctx, 2);
				{
				setState(156);
				expr();
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
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
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
			setState(159);
			match(T__3);
			{
			setState(160);
			pattern();
			}
			setState(163);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(161);
				match(T__4);
				setState(162);
				expr();
				}
			}

			setState(167);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(165);
				match(T__5);
				setState(166);
				expr();
				}
			}

			setState(170);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,9,_ctx) ) {
			case 1:
				{
				setState(169);
				match(T__6);
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
		public TerminalNode ID() { return getToken(AxisParser.ID, 0); }
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
			setState(174);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(172);
				match(ID);
				}
				break;
			case T__12:
				enterOuterAlt(_localctx, 2);
				{
				setState(173);
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
			setState(176);
			match(T__12);
			setState(185);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(177);
				tuplePatternElement();
				setState(182);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==T__13) {
					{
					{
					setState(178);
					match(T__13);
					setState(179);
					tuplePatternElement();
					}
					}
					setState(184);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
			}

			setState(187);
			match(T__14);
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
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public TuplePatternElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tuplePatternElement; }
	}

	public final TuplePatternElementContext tuplePatternElement() throws RecognitionException {
		TuplePatternElementContext _localctx = new TuplePatternElementContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_tuplePatternElement);
		try {
			setState(193);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,13,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(189);
				match(ID);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(190);
				match(ID);
				setState(191);
				match(T__4);
				setState(192);
				match(ID);
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
	public static class ExprContext extends ParserRuleContext {
		public CompoundExprContext compoundExpr() {
			return getRuleContext(CompoundExprContext.class,0);
		}
		public ExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expr; }
	}

	public final ExprContext expr() throws RecognitionException {
		ExprContext _localctx = new ExprContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_expr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(195);
			compoundExpr();
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
	public static class CompoundExprContext extends ParserRuleContext {
		public List<RangeExprContext> rangeExpr() {
			return getRuleContexts(RangeExprContext.class);
		}
		public RangeExprContext rangeExpr(int i) {
			return getRuleContext(RangeExprContext.class,i);
		}
		public CompoundExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_compoundExpr; }
	}

	public final CompoundExprContext compoundExpr() throws RecognitionException {
		CompoundExprContext _localctx = new CompoundExprContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_compoundExpr);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(197);
			rangeExpr();
			setState(201);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(198);
					rangeExpr();
					}
					} 
				}
				setState(203);
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
	public static class RangeExprContext extends ParserRuleContext {
		public List<LogicExprContext> logicExpr() {
			return getRuleContexts(LogicExprContext.class);
		}
		public LogicExprContext logicExpr(int i) {
			return getRuleContext(LogicExprContext.class,i);
		}
		public RangeOpContext rangeOp() {
			return getRuleContext(RangeOpContext.class,0);
		}
		public RangeExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_rangeExpr; }
	}

	public final RangeExprContext rangeExpr() throws RecognitionException {
		RangeExprContext _localctx = new RangeExprContext(_ctx, getState());
		enterRule(_localctx, 34, RULE_rangeExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(204);
			logicExpr();
			setState(208);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__15 || _la==T__16) {
				{
				setState(205);
				rangeOp();
				setState(206);
				logicExpr();
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
	public static class RangeOpContext extends ParserRuleContext {
		public RangeOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_rangeOp; }
	}

	public final RangeOpContext rangeOp() throws RecognitionException {
		RangeOpContext _localctx = new RangeOpContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_rangeOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(210);
			_la = _input.LA(1);
			if ( !(_la==T__15 || _la==T__16) ) {
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
	public static class LogicExprContext extends ParserRuleContext {
		public List<ComparisonExprContext> comparisonExpr() {
			return getRuleContexts(ComparisonExprContext.class);
		}
		public ComparisonExprContext comparisonExpr(int i) {
			return getRuleContext(ComparisonExprContext.class,i);
		}
		public List<LogicOpContext> logicOp() {
			return getRuleContexts(LogicOpContext.class);
		}
		public LogicOpContext logicOp(int i) {
			return getRuleContext(LogicOpContext.class,i);
		}
		public LogicExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicExpr; }
	}

	public final LogicExprContext logicExpr() throws RecognitionException {
		LogicExprContext _localctx = new LogicExprContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_logicExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(212);
			comparisonExpr();
			setState(218);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__17 || _la==T__18) {
				{
				{
				setState(213);
				logicOp();
				setState(214);
				comparisonExpr();
				}
				}
				setState(220);
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
	public static class LogicOpContext extends ParserRuleContext {
		public LogicOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicOp; }
	}

	public final LogicOpContext logicOp() throws RecognitionException {
		LogicOpContext _localctx = new LogicOpContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_logicOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(221);
			_la = _input.LA(1);
			if ( !(_la==T__17 || _la==T__18) ) {
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
		public List<AdditiveExprContext> additiveExpr() {
			return getRuleContexts(AdditiveExprContext.class);
		}
		public AdditiveExprContext additiveExpr(int i) {
			return getRuleContext(AdditiveExprContext.class,i);
		}
		public List<ComparisonOpContext> comparisonOp() {
			return getRuleContexts(ComparisonOpContext.class);
		}
		public ComparisonOpContext comparisonOp(int i) {
			return getRuleContext(ComparisonOpContext.class,i);
		}
		public ComparisonExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_comparisonExpr; }
	}

	public final ComparisonExprContext comparisonExpr() throws RecognitionException {
		ComparisonExprContext _localctx = new ComparisonExprContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_comparisonExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(223);
			additiveExpr();
			setState(229);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 66060288L) != 0)) {
				{
				{
				setState(224);
				comparisonOp();
				setState(225);
				additiveExpr();
				}
				}
				setState(231);
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
	public static class ComparisonOpContext extends ParserRuleContext {
		public ComparisonOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_comparisonOp; }
	}

	public final ComparisonOpContext comparisonOp() throws RecognitionException {
		ComparisonOpContext _localctx = new ComparisonOpContext(_ctx, getState());
		enterRule(_localctx, 44, RULE_comparisonOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(232);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 66060288L) != 0)) ) {
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
	public static class AdditiveExprContext extends ParserRuleContext {
		public List<ProductiveExprContext> productiveExpr() {
			return getRuleContexts(ProductiveExprContext.class);
		}
		public ProductiveExprContext productiveExpr(int i) {
			return getRuleContext(ProductiveExprContext.class,i);
		}
		public List<AdditiveOpContext> additiveOp() {
			return getRuleContexts(AdditiveOpContext.class);
		}
		public AdditiveOpContext additiveOp(int i) {
			return getRuleContext(AdditiveOpContext.class,i);
		}
		public AdditiveExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_additiveExpr; }
	}

	public final AdditiveExprContext additiveExpr() throws RecognitionException {
		AdditiveExprContext _localctx = new AdditiveExprContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_additiveExpr);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(234);
			productiveExpr();
			setState(240);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(235);
					additiveOp();
					setState(236);
					productiveExpr();
					}
					} 
				}
				setState(242);
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
	public static class AdditiveOpContext extends ParserRuleContext {
		public AdditiveOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_additiveOp; }
	}

	public final AdditiveOpContext additiveOp() throws RecognitionException {
		AdditiveOpContext _localctx = new AdditiveOpContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_additiveOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(243);
			_la = _input.LA(1);
			if ( !(_la==T__25 || _la==T__26) ) {
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
	public static class ProductiveExprContext extends ParserRuleContext {
		public List<PrefixExprContext> prefixExpr() {
			return getRuleContexts(PrefixExprContext.class);
		}
		public PrefixExprContext prefixExpr(int i) {
			return getRuleContext(PrefixExprContext.class,i);
		}
		public List<ProductiveOpContext> productiveOp() {
			return getRuleContexts(ProductiveOpContext.class);
		}
		public ProductiveOpContext productiveOp(int i) {
			return getRuleContext(ProductiveOpContext.class,i);
		}
		public ProductiveExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_productiveExpr; }
	}

	public final ProductiveExprContext productiveExpr() throws RecognitionException {
		ProductiveExprContext _localctx = new ProductiveExprContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_productiveExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(245);
			prefixExpr();
			setState(251);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 4026531840L) != 0)) {
				{
				{
				setState(246);
				productiveOp();
				setState(247);
				prefixExpr();
				}
				}
				setState(253);
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
	public static class ProductiveOpContext extends ParserRuleContext {
		public ProductiveOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_productiveOp; }
	}

	public final ProductiveOpContext productiveOp() throws RecognitionException {
		ProductiveOpContext _localctx = new ProductiveOpContext(_ctx, getState());
		enterRule(_localctx, 52, RULE_productiveOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(254);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 4026531840L) != 0)) ) {
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
	public static class PrefixExprContext extends ParserRuleContext {
		public PrefixExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_prefixExpr; }
	 
		public PrefixExprContext() { }
		public void copyFrom(PrefixExprContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class SignExprContext extends PrefixExprContext {
		public SignOpContext signOp() {
			return getRuleContext(SignOpContext.class,0);
		}
		public PrefixExprContext prefixExpr() {
			return getRuleContext(PrefixExprContext.class,0);
		}
		public SignExprContext(PrefixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class EtcExprContext extends PrefixExprContext {
		public EtcOpContext etcOp() {
			return getRuleContext(EtcOpContext.class,0);
		}
		public PrefixExprContext prefixExpr() {
			return getRuleContext(PrefixExprContext.class,0);
		}
		public EtcExprContext(PrefixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class PrefixPassContext extends PrefixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public PrefixPassContext(PrefixExprContext ctx) { copyFrom(ctx); }
	}

	public final PrefixExprContext prefixExpr() throws RecognitionException {
		PrefixExprContext _localctx = new PrefixExprContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_prefixExpr);
		try {
			setState(263);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__12:
			case T__36:
			case T__37:
			case T__41:
			case ID:
			case DECIMAL:
			case TEXT:
				_localctx = new PrefixPassContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(256);
				postfixExpr(0);
				}
				break;
			case T__33:
				_localctx = new EtcExprContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(257);
				etcOp();
				setState(258);
				prefixExpr();
				}
				break;
			case T__25:
			case T__26:
			case T__31:
			case T__32:
				_localctx = new SignExprContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(260);
				signOp();
				setState(261);
				prefixExpr();
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
	public static class SignOpContext extends ParserRuleContext {
		public SignOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_signOp; }
	}

	public final SignOpContext signOp() throws RecognitionException {
		SignOpContext _localctx = new SignOpContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_signOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(265);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 13086228480L) != 0)) ) {
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
	public static class EtcOpContext extends ParserRuleContext {
		public EtcOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_etcOp; }
	}

	public final EtcOpContext etcOp() throws RecognitionException {
		EtcOpContext _localctx = new EtcOpContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_etcOp);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(267);
			match(T__33);
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
	public static class PrefixOpContext extends ParserRuleContext {
		public PrefixOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_prefixOp; }
	}

	public final PrefixOpContext prefixOp() throws RecognitionException {
		PrefixOpContext _localctx = new PrefixOpContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_prefixOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(269);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 30266097664L) != 0)) ) {
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
	public static class PostfixExprContext extends ParserRuleContext {
		public PostfixExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_postfixExpr; }
	 
		public PostfixExprContext() { }
		public void copyFrom(PostfixExprContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ApplyExprContext extends PostfixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public TupleExprContext tupleExpr() {
			return getRuleContext(TupleExprContext.class,0);
		}
		public ApplyExprContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class MemberExprContext extends PostfixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public MemberExprContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class PostfixPassContext extends PostfixExprContext {
		public PrimaryExprContext primaryExpr() {
			return getRuleContext(PrimaryExprContext.class,0);
		}
		public PostfixPassContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TrailExprContext extends PostfixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public LambdaContext lambda() {
			return getRuleContext(LambdaContext.class,0);
		}
		public TrailExprContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class IndexExprContext extends PostfixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public ShapeExprContext shapeExpr() {
			return getRuleContext(ShapeExprContext.class,0);
		}
		public IndexExprContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ScopeExprContext extends PostfixExprContext {
		public PostfixExprContext postfixExpr() {
			return getRuleContext(PostfixExprContext.class,0);
		}
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public ScopeExprContext(PostfixExprContext ctx) { copyFrom(ctx); }
	}

	public final PostfixExprContext postfixExpr() throws RecognitionException {
		return postfixExpr(0);
	}

	private PostfixExprContext postfixExpr(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		PostfixExprContext _localctx = new PostfixExprContext(_ctx, _parentState);
		PostfixExprContext _prevctx = _localctx;
		int _startState = 62;
		enterRecursionRule(_localctx, 62, RULE_postfixExpr, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			{
			_localctx = new PostfixPassContext(_localctx);
			_ctx = _localctx;
			_prevctx = _localctx;

			setState(272);
			primaryExpr();
			}
			_ctx.stop = _input.LT(-1);
			setState(296);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,24,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(294);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,23,_ctx) ) {
					case 1:
						{
						_localctx = new TrailExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(274);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(275);
						lambda();
						}
						break;
					case 2:
						{
						_localctx = new ApplyExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(276);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(277);
						tupleExpr();
						}
						break;
					case 3:
						{
						_localctx = new IndexExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(278);
						if (!(precpred(_ctx, 3))) throw new FailedPredicateException(this, "precpred(_ctx, 3)");
						setState(279);
						shapeExpr();
						}
						break;
					case 4:
						{
						_localctx = new MemberExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(280);
						if (!(precpred(_ctx, 2))) throw new FailedPredicateException(this, "precpred(_ctx, 2)");
						setState(283); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(281);
								match(T__34);
								setState(282);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(285); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,21,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					case 5:
						{
						_localctx = new ScopeExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(287);
						if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
						setState(290); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(288);
								match(T__35);
								setState(289);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(292); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					}
					} 
				}
				setState(298);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,24,_ctx);
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
		public WildcardExprContext wildcardExpr() {
			return getRuleContext(WildcardExprContext.class,0);
		}
		public EllipsisExprContext ellipsisExpr() {
			return getRuleContext(EllipsisExprContext.class,0);
		}
		public SymExprContext symExpr() {
			return getRuleContext(SymExprContext.class,0);
		}
		public LitExprContext litExpr() {
			return getRuleContext(LitExprContext.class,0);
		}
		public TupleExprContext tupleExpr() {
			return getRuleContext(TupleExprContext.class,0);
		}
		public LambdaContext lambda() {
			return getRuleContext(LambdaContext.class,0);
		}
		public PrimaryExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_primaryExpr; }
	}

	public final PrimaryExprContext primaryExpr() throws RecognitionException {
		PrimaryExprContext _localctx = new PrimaryExprContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_primaryExpr);
		try {
			setState(305);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__37:
				enterOuterAlt(_localctx, 1);
				{
				setState(299);
				wildcardExpr();
				}
				break;
			case T__36:
				enterOuterAlt(_localctx, 2);
				{
				setState(300);
				ellipsisExpr();
				}
				break;
			case ID:
				enterOuterAlt(_localctx, 3);
				{
				setState(301);
				symExpr();
				}
				break;
			case DECIMAL:
			case TEXT:
				enterOuterAlt(_localctx, 4);
				{
				setState(302);
				litExpr();
				}
				break;
			case T__12:
				enterOuterAlt(_localctx, 5);
				{
				setState(303);
				tupleExpr();
				}
				break;
			case T__41:
				enterOuterAlt(_localctx, 6);
				{
				setState(304);
				lambda();
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
	public static class EllipsisExprContext extends ParserRuleContext {
		public EllipsisExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ellipsisExpr; }
	}

	public final EllipsisExprContext ellipsisExpr() throws RecognitionException {
		EllipsisExprContext _localctx = new EllipsisExprContext(_ctx, getState());
		enterRule(_localctx, 66, RULE_ellipsisExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(307);
			match(T__36);
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
	public static class WildcardExprContext extends ParserRuleContext {
		public WildcardExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_wildcardExpr; }
	}

	public final WildcardExprContext wildcardExpr() throws RecognitionException {
		WildcardExprContext _localctx = new WildcardExprContext(_ctx, getState());
		enterRule(_localctx, 68, RULE_wildcardExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(309);
			match(T__37);
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
	public static class SymExprContext extends ParserRuleContext {
		public List<TerminalNode> ID() { return getTokens(AxisParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(AxisParser.ID, i);
		}
		public SymExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_symExpr; }
	}

	public final SymExprContext symExpr() throws RecognitionException {
		SymExprContext _localctx = new SymExprContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_symExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(311);
			match(ID);
			setState(314);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,26,_ctx) ) {
			case 1:
				{
				setState(312);
				match(T__38);
				setState(313);
				match(ID);
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
	public static class LitExprContext extends ParserRuleContext {
		public TerminalNode DECIMAL() { return getToken(AxisParser.DECIMAL, 0); }
		public TerminalNode TEXT() { return getToken(AxisParser.TEXT, 0); }
		public LitExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_litExpr; }
	}

	public final LitExprContext litExpr() throws RecognitionException {
		LitExprContext _localctx = new LitExprContext(_ctx, getState());
		enterRule(_localctx, 72, RULE_litExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(316);
			_la = _input.LA(1);
			if ( !(_la==DECIMAL || _la==TEXT) ) {
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
	public static class TupleExprContext extends ParserRuleContext {
		public List<TupleElementContext> tupleElement() {
			return getRuleContexts(TupleElementContext.class);
		}
		public TupleElementContext tupleElement(int i) {
			return getRuleContext(TupleElementContext.class,i);
		}
		public TupleExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleExpr; }
	}

	public final TupleExprContext tupleExpr() throws RecognitionException {
		TupleExprContext _localctx = new TupleExprContext(_ctx, getState());
		enterRule(_localctx, 74, RULE_tupleExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(318);
			match(T__12);
			setState(327);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
				{
				setState(319);
				tupleElement();
				setState(324);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,27,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(320);
						match(T__13);
						setState(321);
						tupleElement();
						}
						} 
					}
					setState(326);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,27,_ctx);
				}
				}
			}

			setState(330);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__13) {
				{
				setState(329);
				match(T__13);
				}
			}

			setState(332);
			match(T__14);
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
	public static class ShapeExprContext extends ParserRuleContext {
		public List<TupleElementContext> tupleElement() {
			return getRuleContexts(TupleElementContext.class);
		}
		public TupleElementContext tupleElement(int i) {
			return getRuleContext(TupleElementContext.class,i);
		}
		public ShapeExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_shapeExpr; }
	}

	public final ShapeExprContext shapeExpr() throws RecognitionException {
		ShapeExprContext _localctx = new ShapeExprContext(_ctx, getState());
		enterRule(_localctx, 76, RULE_shapeExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(334);
			match(T__39);
			setState(343);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
				{
				setState(335);
				tupleElement();
				setState(340);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,30,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(336);
						match(T__13);
						setState(337);
						tupleElement();
						}
						} 
					}
					setState(342);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,30,_ctx);
				}
				}
			}

			setState(346);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__13) {
				{
				setState(345);
				match(T__13);
				}
			}

			setState(348);
			match(T__40);
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
		public TuplePositionalElementContext tuplePositionalElement() {
			return getRuleContext(TuplePositionalElementContext.class,0);
		}
		public TupleNominalElementContext tupleNominalElement() {
			return getRuleContext(TupleNominalElementContext.class,0);
		}
		public TupleElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleElement; }
	}

	public final TupleElementContext tupleElement() throws RecognitionException {
		TupleElementContext _localctx = new TupleElementContext(_ctx, getState());
		enterRule(_localctx, 78, RULE_tupleElement);
		try {
			setState(352);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,33,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(350);
				tuplePositionalElement();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(351);
				tupleNominalElement();
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
	public static class TuplePositionalElementContext extends ParserRuleContext {
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TuplePositionalElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tuplePositionalElement; }
	}

	public final TuplePositionalElementContext tuplePositionalElement() throws RecognitionException {
		TuplePositionalElementContext _localctx = new TuplePositionalElementContext(_ctx, getState());
		enterRule(_localctx, 80, RULE_tuplePositionalElement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(354);
			expr();
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
	public static class TupleNominalElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TupleNominalElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleNominalElement; }
	}

	public final TupleNominalElementContext tupleNominalElement() throws RecognitionException {
		TupleNominalElementContext _localctx = new TupleNominalElementContext(_ctx, getState());
		enterRule(_localctx, 82, RULE_tupleNominalElement);
		try {
			setState(370);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,34,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(356);
				expr();
				setState(357);
				match(T__4);
				setState(358);
				expr();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(360);
				expr();
				setState(361);
				match(T__5);
				setState(362);
				expr();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(364);
				expr();
				setState(365);
				match(T__4);
				setState(366);
				expr();
				setState(367);
				match(T__5);
				setState(368);
				expr();
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
	public static class TupleSpreadElementContext extends ParserRuleContext {
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TupleSpreadElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleSpreadElement; }
	}

	public final TupleSpreadElementContext tupleSpreadElement() throws RecognitionException {
		TupleSpreadElementContext _localctx = new TupleSpreadElementContext(_ctx, getState());
		enterRule(_localctx, 84, RULE_tupleSpreadElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(372);
			match(T__33);
			setState(374);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
				{
				setState(373);
				expr();
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
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public SemicolonContext semicolon() {
			return getRuleContext(SemicolonContext.class,0);
		}
		public BasicSuiteContext(LambdaContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LambdaSuiteContext extends LambdaContext {
		public LambdaParamsContext lambdaParams() {
			return getRuleContext(LambdaParamsContext.class,0);
		}
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public LambdaSuiteContext(LambdaContext ctx) { copyFrom(ctx); }
	}

	public final LambdaContext lambda() throws RecognitionException {
		LambdaContext _localctx = new LambdaContext(_ctx, getState());
		enterRule(_localctx, 86, RULE_lambda);
		int _la;
		try {
			int _alt;
			setState(405);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,42,_ctx) ) {
			case 1:
				_localctx = new LambdaSuiteContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(376);
				match(T__41);
				setState(378);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==ID) {
					{
					setState(377);
					lambdaParams();
					}
				}

				setState(380);
				match(T__42);
				setState(384);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,37,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(381);
						statement();
						}
						} 
					}
					setState(386);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,37,_ctx);
				}
				setState(388);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
					{
					setState(387);
					expr();
					}
				}

				setState(390);
				match(T__43);
				}
				break;
			case 2:
				_localctx = new BasicSuiteContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(391);
				match(T__41);
				setState(395);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,39,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(392);
						statement();
						}
						} 
					}
					setState(397);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,39,_ctx);
				}
				setState(399);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 251131234099200L) != 0)) {
					{
					setState(398);
					expr();
					}
				}

				setState(402);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__6) {
					{
					setState(401);
					semicolon();
					}
				}

				setState(404);
				match(T__43);
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
		enterRule(_localctx, 88, RULE_semicolon);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(407);
			match(T__6);
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
		enterRule(_localctx, 90, RULE_lambdaParams);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(409);
			lambdaParam();
			setState(414);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,43,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(410);
					match(T__13);
					setState(411);
					lambdaParam();
					}
					} 
				}
				setState(416);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,43,_ctx);
			}
			setState(418);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__13) {
				{
				setState(417);
				match(T__13);
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
		public TerminalNode ID() { return getToken(AxisParser.ID, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public LambdaParamContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lambdaParam; }
	}

	public final LambdaParamContext lambdaParam() throws RecognitionException {
		LambdaParamContext _localctx = new LambdaParamContext(_ctx, getState());
		enterRule(_localctx, 92, RULE_lambdaParam);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(420);
			match(ID);
			setState(423);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(421);
				match(T__4);
				setState(422);
				expr();
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

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 31:
			return postfixExpr_sempred((PostfixExprContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean postfixExpr_sempred(PostfixExprContext _localctx, int predIndex) {
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
		"\u0004\u00011\u01aa\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
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
		"#\u0007#\u0002$\u0007$\u0002%\u0007%\u0002&\u0007&\u0002\'\u0007\'\u0002"+
		"(\u0007(\u0002)\u0007)\u0002*\u0007*\u0002+\u0007+\u0002,\u0007,\u0002"+
		"-\u0007-\u0002.\u0007.\u0001\u0000\u0001\u0000\u0001\u0000\u0001\u0000"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0002\u0001\u0002"+
		"\u0001\u0002\u0001\u0002\u0001\u0003\u0001\u0003\u0001\u0003\u0001\u0003"+
		"\u0003\u0003o\b\u0003\u0001\u0003\u0001\u0003\u0003\u0003s\b\u0003\u0001"+
		"\u0003\u0003\u0003v\b\u0003\u0001\u0003\u0001\u0003\u0001\u0004\u0001"+
		"\u0004\u0001\u0004\u0001\u0004\u0001\u0005\u0001\u0005\u0003\u0005\u0080"+
		"\b\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0006\u0001\u0006\u0001"+
		"\u0006\u0001\u0006\u0001\u0007\u0001\u0007\u0001\u0007\u0001\u0007\u0001"+
		"\b\u0001\b\u0005\b\u008f\b\b\n\b\f\b\u0092\t\b\u0001\b\u0001\b\u0001\t"+
		"\u0005\t\u0097\b\t\n\t\f\t\u009a\t\t\u0001\n\u0001\n\u0003\n\u009e\b\n"+
		"\u0001\u000b\u0001\u000b\u0001\u000b\u0001\u000b\u0003\u000b\u00a4\b\u000b"+
		"\u0001\u000b\u0001\u000b\u0003\u000b\u00a8\b\u000b\u0001\u000b\u0003\u000b"+
		"\u00ab\b\u000b\u0001\f\u0001\f\u0003\f\u00af\b\f\u0001\r\u0001\r\u0001"+
		"\r\u0001\r\u0005\r\u00b5\b\r\n\r\f\r\u00b8\t\r\u0003\r\u00ba\b\r\u0001"+
		"\r\u0001\r\u0001\u000e\u0001\u000e\u0001\u000e\u0001\u000e\u0003\u000e"+
		"\u00c2\b\u000e\u0001\u000f\u0001\u000f\u0001\u0010\u0001\u0010\u0005\u0010"+
		"\u00c8\b\u0010\n\u0010\f\u0010\u00cb\t\u0010\u0001\u0011\u0001\u0011\u0001"+
		"\u0011\u0001\u0011\u0003\u0011\u00d1\b\u0011\u0001\u0012\u0001\u0012\u0001"+
		"\u0013\u0001\u0013\u0001\u0013\u0001\u0013\u0005\u0013\u00d9\b\u0013\n"+
		"\u0013\f\u0013\u00dc\t\u0013\u0001\u0014\u0001\u0014\u0001\u0015\u0001"+
		"\u0015\u0001\u0015\u0001\u0015\u0005\u0015\u00e4\b\u0015\n\u0015\f\u0015"+
		"\u00e7\t\u0015\u0001\u0016\u0001\u0016\u0001\u0017\u0001\u0017\u0001\u0017"+
		"\u0001\u0017\u0005\u0017\u00ef\b\u0017\n\u0017\f\u0017\u00f2\t\u0017\u0001"+
		"\u0018\u0001\u0018\u0001\u0019\u0001\u0019\u0001\u0019\u0001\u0019\u0005"+
		"\u0019\u00fa\b\u0019\n\u0019\f\u0019\u00fd\t\u0019\u0001\u001a\u0001\u001a"+
		"\u0001\u001b\u0001\u001b\u0001\u001b\u0001\u001b\u0001\u001b\u0001\u001b"+
		"\u0001\u001b\u0003\u001b\u0108\b\u001b\u0001\u001c\u0001\u001c\u0001\u001d"+
		"\u0001\u001d\u0001\u001e\u0001\u001e\u0001\u001f\u0001\u001f\u0001\u001f"+
		"\u0001\u001f\u0001\u001f\u0001\u001f\u0001\u001f\u0001\u001f\u0001\u001f"+
		"\u0001\u001f\u0001\u001f\u0001\u001f\u0004\u001f\u011c\b\u001f\u000b\u001f"+
		"\f\u001f\u011d\u0001\u001f\u0001\u001f\u0001\u001f\u0004\u001f\u0123\b"+
		"\u001f\u000b\u001f\f\u001f\u0124\u0005\u001f\u0127\b\u001f\n\u001f\f\u001f"+
		"\u012a\t\u001f\u0001 \u0001 \u0001 \u0001 \u0001 \u0001 \u0003 \u0132"+
		"\b \u0001!\u0001!\u0001\"\u0001\"\u0001#\u0001#\u0001#\u0003#\u013b\b"+
		"#\u0001$\u0001$\u0001%\u0001%\u0001%\u0001%\u0005%\u0143\b%\n%\f%\u0146"+
		"\t%\u0003%\u0148\b%\u0001%\u0003%\u014b\b%\u0001%\u0001%\u0001&\u0001"+
		"&\u0001&\u0001&\u0005&\u0153\b&\n&\f&\u0156\t&\u0003&\u0158\b&\u0001&"+
		"\u0003&\u015b\b&\u0001&\u0001&\u0001\'\u0001\'\u0003\'\u0161\b\'\u0001"+
		"(\u0001(\u0001)\u0001)\u0001)\u0001)\u0001)\u0001)\u0001)\u0001)\u0001"+
		")\u0001)\u0001)\u0001)\u0001)\u0001)\u0003)\u0173\b)\u0001*\u0001*\u0003"+
		"*\u0177\b*\u0001+\u0001+\u0003+\u017b\b+\u0001+\u0001+\u0005+\u017f\b"+
		"+\n+\f+\u0182\t+\u0001+\u0003+\u0185\b+\u0001+\u0001+\u0001+\u0005+\u018a"+
		"\b+\n+\f+\u018d\t+\u0001+\u0003+\u0190\b+\u0001+\u0003+\u0193\b+\u0001"+
		"+\u0003+\u0196\b+\u0001,\u0001,\u0001-\u0001-\u0001-\u0005-\u019d\b-\n"+
		"-\f-\u01a0\t-\u0001-\u0003-\u01a3\b-\u0001.\u0001.\u0001.\u0003.\u01a8"+
		"\b.\u0001.\u0000\u0001>/\u0000\u0002\u0004\u0006\b\n\f\u000e\u0010\u0012"+
		"\u0014\u0016\u0018\u001a\u001c\u001e \"$&(*,.02468:<>@BDFHJLNPRTVXZ\\"+
		"\u0000\b\u0001\u0000\u0010\u0011\u0001\u0000\u0012\u0013\u0001\u0000\u0014"+
		"\u0019\u0001\u0000\u001a\u001b\u0001\u0000\u001c\u001f\u0002\u0000\u001a"+
		"\u001b !\u0002\u0000\u001a\u001b \"\u0001\u0000./\u01b1\u0000^\u0001\u0000"+
		"\u0000\u0000\u0002b\u0001\u0000\u0000\u0000\u0004f\u0001\u0000\u0000\u0000"+
		"\u0006j\u0001\u0000\u0000\u0000\by\u0001\u0000\u0000\u0000\n}\u0001\u0000"+
		"\u0000\u0000\f\u0084\u0001\u0000\u0000\u0000\u000e\u0088\u0001\u0000\u0000"+
		"\u0000\u0010\u008c\u0001\u0000\u0000\u0000\u0012\u0098\u0001\u0000\u0000"+
		"\u0000\u0014\u009d\u0001\u0000\u0000\u0000\u0016\u009f\u0001\u0000\u0000"+
		"\u0000\u0018\u00ae\u0001\u0000\u0000\u0000\u001a\u00b0\u0001\u0000\u0000"+
		"\u0000\u001c\u00c1\u0001\u0000\u0000\u0000\u001e\u00c3\u0001\u0000\u0000"+
		"\u0000 \u00c5\u0001\u0000\u0000\u0000\"\u00cc\u0001\u0000\u0000\u0000"+
		"$\u00d2\u0001\u0000\u0000\u0000&\u00d4\u0001\u0000\u0000\u0000(\u00dd"+
		"\u0001\u0000\u0000\u0000*\u00df\u0001\u0000\u0000\u0000,\u00e8\u0001\u0000"+
		"\u0000\u0000.\u00ea\u0001\u0000\u0000\u00000\u00f3\u0001\u0000\u0000\u0000"+
		"2\u00f5\u0001\u0000\u0000\u00004\u00fe\u0001\u0000\u0000\u00006\u0107"+
		"\u0001\u0000\u0000\u00008\u0109\u0001\u0000\u0000\u0000:\u010b\u0001\u0000"+
		"\u0000\u0000<\u010d\u0001\u0000\u0000\u0000>\u010f\u0001\u0000\u0000\u0000"+
		"@\u0131\u0001\u0000\u0000\u0000B\u0133\u0001\u0000\u0000\u0000D\u0135"+
		"\u0001\u0000\u0000\u0000F\u0137\u0001\u0000\u0000\u0000H\u013c\u0001\u0000"+
		"\u0000\u0000J\u013e\u0001\u0000\u0000\u0000L\u014e\u0001\u0000\u0000\u0000"+
		"N\u0160\u0001\u0000\u0000\u0000P\u0162\u0001\u0000\u0000\u0000R\u0172"+
		"\u0001\u0000\u0000\u0000T\u0174\u0001\u0000\u0000\u0000V\u0195\u0001\u0000"+
		"\u0000\u0000X\u0197\u0001\u0000\u0000\u0000Z\u0199\u0001\u0000\u0000\u0000"+
		"\\\u01a4\u0001\u0000\u0000\u0000^_\u0005\u0001\u0000\u0000_`\u0003\u001e"+
		"\u000f\u0000`a\u0005\u0000\u0000\u0001a\u0001\u0001\u0000\u0000\u0000"+
		"bc\u0005\u0002\u0000\u0000cd\u0003\u001e\u000f\u0000de\u0005\u0000\u0000"+
		"\u0001e\u0003\u0001\u0000\u0000\u0000fg\u0005\u0003\u0000\u0000gh\u0003"+
		"\u001e\u000f\u0000hi\u0005\u0000\u0000\u0001i\u0005\u0001\u0000\u0000"+
		"\u0000jk\u0005\u0004\u0000\u0000kn\u0003\u001e\u000f\u0000lm\u0005\u0005"+
		"\u0000\u0000mo\u0003\u001e\u000f\u0000nl\u0001\u0000\u0000\u0000no\u0001"+
		"\u0000\u0000\u0000or\u0001\u0000\u0000\u0000pq\u0005\u0006\u0000\u0000"+
		"qs\u0003\u001e\u000f\u0000rp\u0001\u0000\u0000\u0000rs\u0001\u0000\u0000"+
		"\u0000su\u0001\u0000\u0000\u0000tv\u0005\u0007\u0000\u0000ut\u0001\u0000"+
		"\u0000\u0000uv\u0001\u0000\u0000\u0000vw\u0001\u0000\u0000\u0000wx\u0005"+
		"\u0000\u0000\u0001x\u0007\u0001\u0000\u0000\u0000yz\u0005\b\u0000\u0000"+
		"z{\u0003\u001e\u000f\u0000{|\u0005\u0000\u0000\u0001|\t\u0001\u0000\u0000"+
		"\u0000}\u007f\u0005\t\u0000\u0000~\u0080\u0003\u001e\u000f\u0000\u007f"+
		"~\u0001\u0000\u0000\u0000\u007f\u0080\u0001\u0000\u0000\u0000\u0080\u0081"+
		"\u0001\u0000\u0000\u0000\u0081\u0082\u0005\u0005\u0000\u0000\u0082\u0083"+
		"\u0005\u0000\u0000\u0001\u0083\u000b\u0001\u0000\u0000\u0000\u0084\u0085"+
		"\u0005\n\u0000\u0000\u0085\u0086\u0005\u0005\u0000\u0000\u0086\u0087\u0005"+
		"\u0000\u0000\u0001\u0087\r\u0001\u0000\u0000\u0000\u0088\u0089\u0005\u000b"+
		"\u0000\u0000\u0089\u008a\u0003\u001e\u000f\u0000\u008a\u008b\u0005\u0000"+
		"\u0000\u0001\u008b\u000f\u0001\u0000\u0000\u0000\u008c\u0090\u0005\f\u0000"+
		"\u0000\u008d\u008f\u0003\u0014\n\u0000\u008e\u008d\u0001\u0000\u0000\u0000"+
		"\u008f\u0092\u0001\u0000\u0000\u0000\u0090\u008e\u0001\u0000\u0000\u0000"+
		"\u0090\u0091\u0001\u0000\u0000\u0000\u0091\u0093\u0001\u0000\u0000\u0000"+
		"\u0092\u0090\u0001\u0000\u0000\u0000\u0093\u0094\u0005\u0000\u0000\u0001"+
		"\u0094\u0011\u0001\u0000\u0000\u0000\u0095\u0097\u0003\u0014\n\u0000\u0096"+
		"\u0095\u0001\u0000\u0000\u0000\u0097\u009a\u0001\u0000\u0000\u0000\u0098"+
		"\u0096\u0001\u0000\u0000\u0000\u0098\u0099\u0001\u0000\u0000\u0000\u0099"+
		"\u0013\u0001\u0000\u0000\u0000\u009a\u0098\u0001\u0000\u0000\u0000\u009b"+
		"\u009e\u0003\u0016\u000b\u0000\u009c\u009e\u0003\u001e\u000f\u0000\u009d"+
		"\u009b\u0001\u0000\u0000\u0000\u009d\u009c\u0001\u0000\u0000\u0000\u009e"+
		"\u0015\u0001\u0000\u0000\u0000\u009f\u00a0\u0005\u0004\u0000\u0000\u00a0"+
		"\u00a3\u0003\u0018\f\u0000\u00a1\u00a2\u0005\u0005\u0000\u0000\u00a2\u00a4"+
		"\u0003\u001e\u000f\u0000\u00a3\u00a1\u0001\u0000\u0000\u0000\u00a3\u00a4"+
		"\u0001\u0000\u0000\u0000\u00a4\u00a7\u0001\u0000\u0000\u0000\u00a5\u00a6"+
		"\u0005\u0006\u0000\u0000\u00a6\u00a8\u0003\u001e\u000f\u0000\u00a7\u00a5"+
		"\u0001\u0000\u0000\u0000\u00a7\u00a8\u0001\u0000\u0000\u0000\u00a8\u00aa"+
		"\u0001\u0000\u0000\u0000\u00a9\u00ab\u0005\u0007\u0000\u0000\u00aa\u00a9"+
		"\u0001\u0000\u0000\u0000\u00aa\u00ab\u0001\u0000\u0000\u0000\u00ab\u0017"+
		"\u0001\u0000\u0000\u0000\u00ac\u00af\u0005-\u0000\u0000\u00ad\u00af\u0003"+
		"\u001a\r\u0000\u00ae\u00ac\u0001\u0000\u0000\u0000\u00ae\u00ad\u0001\u0000"+
		"\u0000\u0000\u00af\u0019\u0001\u0000\u0000\u0000\u00b0\u00b9\u0005\r\u0000"+
		"\u0000\u00b1\u00b6\u0003\u001c\u000e\u0000\u00b2\u00b3\u0005\u000e\u0000"+
		"\u0000\u00b3\u00b5\u0003\u001c\u000e\u0000\u00b4\u00b2\u0001\u0000\u0000"+
		"\u0000\u00b5\u00b8\u0001\u0000\u0000\u0000\u00b6\u00b4\u0001\u0000\u0000"+
		"\u0000\u00b6\u00b7\u0001\u0000\u0000\u0000\u00b7\u00ba\u0001\u0000\u0000"+
		"\u0000\u00b8\u00b6\u0001\u0000\u0000\u0000\u00b9\u00b1\u0001\u0000\u0000"+
		"\u0000\u00b9\u00ba\u0001\u0000\u0000\u0000\u00ba\u00bb\u0001\u0000\u0000"+
		"\u0000\u00bb\u00bc\u0005\u000f\u0000\u0000\u00bc\u001b\u0001\u0000\u0000"+
		"\u0000\u00bd\u00c2\u0005-\u0000\u0000\u00be\u00bf\u0005-\u0000\u0000\u00bf"+
		"\u00c0\u0005\u0005\u0000\u0000\u00c0\u00c2\u0005-\u0000\u0000\u00c1\u00bd"+
		"\u0001\u0000\u0000\u0000\u00c1\u00be\u0001\u0000\u0000\u0000\u00c2\u001d"+
		"\u0001\u0000\u0000\u0000\u00c3\u00c4\u0003 \u0010\u0000\u00c4\u001f\u0001"+
		"\u0000\u0000\u0000\u00c5\u00c9\u0003\"\u0011\u0000\u00c6\u00c8\u0003\""+
		"\u0011\u0000\u00c7\u00c6\u0001\u0000\u0000\u0000\u00c8\u00cb\u0001\u0000"+
		"\u0000\u0000\u00c9\u00c7\u0001\u0000\u0000\u0000\u00c9\u00ca\u0001\u0000"+
		"\u0000\u0000\u00ca!\u0001\u0000\u0000\u0000\u00cb\u00c9\u0001\u0000\u0000"+
		"\u0000\u00cc\u00d0\u0003&\u0013\u0000\u00cd\u00ce\u0003$\u0012\u0000\u00ce"+
		"\u00cf\u0003&\u0013\u0000\u00cf\u00d1\u0001\u0000\u0000\u0000\u00d0\u00cd"+
		"\u0001\u0000\u0000\u0000\u00d0\u00d1\u0001\u0000\u0000\u0000\u00d1#\u0001"+
		"\u0000\u0000\u0000\u00d2\u00d3\u0007\u0000\u0000\u0000\u00d3%\u0001\u0000"+
		"\u0000\u0000\u00d4\u00da\u0003*\u0015\u0000\u00d5\u00d6\u0003(\u0014\u0000"+
		"\u00d6\u00d7\u0003*\u0015\u0000\u00d7\u00d9\u0001\u0000\u0000\u0000\u00d8"+
		"\u00d5\u0001\u0000\u0000\u0000\u00d9\u00dc\u0001\u0000\u0000\u0000\u00da"+
		"\u00d8\u0001\u0000\u0000\u0000\u00da\u00db\u0001\u0000\u0000\u0000\u00db"+
		"\'\u0001\u0000\u0000\u0000\u00dc\u00da\u0001\u0000\u0000\u0000\u00dd\u00de"+
		"\u0007\u0001\u0000\u0000\u00de)\u0001\u0000\u0000\u0000\u00df\u00e5\u0003"+
		".\u0017\u0000\u00e0\u00e1\u0003,\u0016\u0000\u00e1\u00e2\u0003.\u0017"+
		"\u0000\u00e2\u00e4\u0001\u0000\u0000\u0000\u00e3\u00e0\u0001\u0000\u0000"+
		"\u0000\u00e4\u00e7\u0001\u0000\u0000\u0000\u00e5\u00e3\u0001\u0000\u0000"+
		"\u0000\u00e5\u00e6\u0001\u0000\u0000\u0000\u00e6+\u0001\u0000\u0000\u0000"+
		"\u00e7\u00e5\u0001\u0000\u0000\u0000\u00e8\u00e9\u0007\u0002\u0000\u0000"+
		"\u00e9-\u0001\u0000\u0000\u0000\u00ea\u00f0\u00032\u0019\u0000\u00eb\u00ec"+
		"\u00030\u0018\u0000\u00ec\u00ed\u00032\u0019\u0000\u00ed\u00ef\u0001\u0000"+
		"\u0000\u0000\u00ee\u00eb\u0001\u0000\u0000\u0000\u00ef\u00f2\u0001\u0000"+
		"\u0000\u0000\u00f0\u00ee\u0001\u0000\u0000\u0000\u00f0\u00f1\u0001\u0000"+
		"\u0000\u0000\u00f1/\u0001\u0000\u0000\u0000\u00f2\u00f0\u0001\u0000\u0000"+
		"\u0000\u00f3\u00f4\u0007\u0003\u0000\u0000\u00f41\u0001\u0000\u0000\u0000"+
		"\u00f5\u00fb\u00036\u001b\u0000\u00f6\u00f7\u00034\u001a\u0000\u00f7\u00f8"+
		"\u00036\u001b\u0000\u00f8\u00fa\u0001\u0000\u0000\u0000\u00f9\u00f6\u0001"+
		"\u0000\u0000\u0000\u00fa\u00fd\u0001\u0000\u0000\u0000\u00fb\u00f9\u0001"+
		"\u0000\u0000\u0000\u00fb\u00fc\u0001\u0000\u0000\u0000\u00fc3\u0001\u0000"+
		"\u0000\u0000\u00fd\u00fb\u0001\u0000\u0000\u0000\u00fe\u00ff\u0007\u0004"+
		"\u0000\u0000\u00ff5\u0001\u0000\u0000\u0000\u0100\u0108\u0003>\u001f\u0000"+
		"\u0101\u0102\u0003:\u001d\u0000\u0102\u0103\u00036\u001b\u0000\u0103\u0108"+
		"\u0001\u0000\u0000\u0000\u0104\u0105\u00038\u001c\u0000\u0105\u0106\u0003"+
		"6\u001b\u0000\u0106\u0108\u0001\u0000\u0000\u0000\u0107\u0100\u0001\u0000"+
		"\u0000\u0000\u0107\u0101\u0001\u0000\u0000\u0000\u0107\u0104\u0001\u0000"+
		"\u0000\u0000\u01087\u0001\u0000\u0000\u0000\u0109\u010a\u0007\u0005\u0000"+
		"\u0000\u010a9\u0001\u0000\u0000\u0000\u010b\u010c\u0005\"\u0000\u0000"+
		"\u010c;\u0001\u0000\u0000\u0000\u010d\u010e\u0007\u0006\u0000\u0000\u010e"+
		"=\u0001\u0000\u0000\u0000\u010f\u0110\u0006\u001f\uffff\uffff\u0000\u0110"+
		"\u0111\u0003@ \u0000\u0111\u0128\u0001\u0000\u0000\u0000\u0112\u0113\n"+
		"\u0005\u0000\u0000\u0113\u0127\u0003V+\u0000\u0114\u0115\n\u0004\u0000"+
		"\u0000\u0115\u0127\u0003J%\u0000\u0116\u0117\n\u0003\u0000\u0000\u0117"+
		"\u0127\u0003L&\u0000\u0118\u011b\n\u0002\u0000\u0000\u0119\u011a\u0005"+
		"#\u0000\u0000\u011a\u011c\u0005-\u0000\u0000\u011b\u0119\u0001\u0000\u0000"+
		"\u0000\u011c\u011d\u0001\u0000\u0000\u0000\u011d\u011b\u0001\u0000\u0000"+
		"\u0000\u011d\u011e\u0001\u0000\u0000\u0000\u011e\u0127\u0001\u0000\u0000"+
		"\u0000\u011f\u0122\n\u0001\u0000\u0000\u0120\u0121\u0005$\u0000\u0000"+
		"\u0121\u0123\u0005-\u0000\u0000\u0122\u0120\u0001\u0000\u0000\u0000\u0123"+
		"\u0124\u0001\u0000\u0000\u0000\u0124\u0122\u0001\u0000\u0000\u0000\u0124"+
		"\u0125\u0001\u0000\u0000\u0000\u0125\u0127\u0001\u0000\u0000\u0000\u0126"+
		"\u0112\u0001\u0000\u0000\u0000\u0126\u0114\u0001\u0000\u0000\u0000\u0126"+
		"\u0116\u0001\u0000\u0000\u0000\u0126\u0118\u0001\u0000\u0000\u0000\u0126"+
		"\u011f\u0001\u0000\u0000\u0000\u0127\u012a\u0001\u0000\u0000\u0000\u0128"+
		"\u0126\u0001\u0000\u0000\u0000\u0128\u0129\u0001\u0000\u0000\u0000\u0129"+
		"?\u0001\u0000\u0000\u0000\u012a\u0128\u0001\u0000\u0000\u0000\u012b\u0132"+
		"\u0003D\"\u0000\u012c\u0132\u0003B!\u0000\u012d\u0132\u0003F#\u0000\u012e"+
		"\u0132\u0003H$\u0000\u012f\u0132\u0003J%\u0000\u0130\u0132\u0003V+\u0000"+
		"\u0131\u012b\u0001\u0000\u0000\u0000\u0131\u012c\u0001\u0000\u0000\u0000"+
		"\u0131\u012d\u0001\u0000\u0000\u0000\u0131\u012e\u0001\u0000\u0000\u0000"+
		"\u0131\u012f\u0001\u0000\u0000\u0000\u0131\u0130\u0001\u0000\u0000\u0000"+
		"\u0132A\u0001\u0000\u0000\u0000\u0133\u0134\u0005%\u0000\u0000\u0134C"+
		"\u0001\u0000\u0000\u0000\u0135\u0136\u0005&\u0000\u0000\u0136E\u0001\u0000"+
		"\u0000\u0000\u0137\u013a\u0005-\u0000\u0000\u0138\u0139\u0005\'\u0000"+
		"\u0000\u0139\u013b\u0005-\u0000\u0000\u013a\u0138\u0001\u0000\u0000\u0000"+
		"\u013a\u013b\u0001\u0000\u0000\u0000\u013bG\u0001\u0000\u0000\u0000\u013c"+
		"\u013d\u0007\u0007\u0000\u0000\u013dI\u0001\u0000\u0000\u0000\u013e\u0147"+
		"\u0005\r\u0000\u0000\u013f\u0144\u0003N\'\u0000\u0140\u0141\u0005\u000e"+
		"\u0000\u0000\u0141\u0143\u0003N\'\u0000\u0142\u0140\u0001\u0000\u0000"+
		"\u0000\u0143\u0146\u0001\u0000\u0000\u0000\u0144\u0142\u0001\u0000\u0000"+
		"\u0000\u0144\u0145\u0001\u0000\u0000\u0000\u0145\u0148\u0001\u0000\u0000"+
		"\u0000\u0146\u0144\u0001\u0000\u0000\u0000\u0147\u013f\u0001\u0000\u0000"+
		"\u0000\u0147\u0148\u0001\u0000\u0000\u0000\u0148\u014a\u0001\u0000\u0000"+
		"\u0000\u0149\u014b\u0005\u000e\u0000\u0000\u014a\u0149\u0001\u0000\u0000"+
		"\u0000\u014a\u014b\u0001\u0000\u0000\u0000\u014b\u014c\u0001\u0000\u0000"+
		"\u0000\u014c\u014d\u0005\u000f\u0000\u0000\u014dK\u0001\u0000\u0000\u0000"+
		"\u014e\u0157\u0005(\u0000\u0000\u014f\u0154\u0003N\'\u0000\u0150\u0151"+
		"\u0005\u000e\u0000\u0000\u0151\u0153\u0003N\'\u0000\u0152\u0150\u0001"+
		"\u0000\u0000\u0000\u0153\u0156\u0001\u0000\u0000\u0000\u0154\u0152\u0001"+
		"\u0000\u0000\u0000\u0154\u0155\u0001\u0000\u0000\u0000\u0155\u0158\u0001"+
		"\u0000\u0000\u0000\u0156\u0154\u0001\u0000\u0000\u0000\u0157\u014f\u0001"+
		"\u0000\u0000\u0000\u0157\u0158\u0001\u0000\u0000\u0000\u0158\u015a\u0001"+
		"\u0000\u0000\u0000\u0159\u015b\u0005\u000e\u0000\u0000\u015a\u0159\u0001"+
		"\u0000\u0000\u0000\u015a\u015b\u0001\u0000\u0000\u0000\u015b\u015c\u0001"+
		"\u0000\u0000\u0000\u015c\u015d\u0005)\u0000\u0000\u015dM\u0001\u0000\u0000"+
		"\u0000\u015e\u0161\u0003P(\u0000\u015f\u0161\u0003R)\u0000\u0160\u015e"+
		"\u0001\u0000\u0000\u0000\u0160\u015f\u0001\u0000\u0000\u0000\u0161O\u0001"+
		"\u0000\u0000\u0000\u0162\u0163\u0003\u001e\u000f\u0000\u0163Q\u0001\u0000"+
		"\u0000\u0000\u0164\u0165\u0003\u001e\u000f\u0000\u0165\u0166\u0005\u0005"+
		"\u0000\u0000\u0166\u0167\u0003\u001e\u000f\u0000\u0167\u0173\u0001\u0000"+
		"\u0000\u0000\u0168\u0169\u0003\u001e\u000f\u0000\u0169\u016a\u0005\u0006"+
		"\u0000\u0000\u016a\u016b\u0003\u001e\u000f\u0000\u016b\u0173\u0001\u0000"+
		"\u0000\u0000\u016c\u016d\u0003\u001e\u000f\u0000\u016d\u016e\u0005\u0005"+
		"\u0000\u0000\u016e\u016f\u0003\u001e\u000f\u0000\u016f\u0170\u0005\u0006"+
		"\u0000\u0000\u0170\u0171\u0003\u001e\u000f\u0000\u0171\u0173\u0001\u0000"+
		"\u0000\u0000\u0172\u0164\u0001\u0000\u0000\u0000\u0172\u0168\u0001\u0000"+
		"\u0000\u0000\u0172\u016c\u0001\u0000\u0000\u0000\u0173S\u0001\u0000\u0000"+
		"\u0000\u0174\u0176\u0005\"\u0000\u0000\u0175\u0177\u0003\u001e\u000f\u0000"+
		"\u0176\u0175\u0001\u0000\u0000\u0000\u0176\u0177\u0001\u0000\u0000\u0000"+
		"\u0177U\u0001\u0000\u0000\u0000\u0178\u017a\u0005*\u0000\u0000\u0179\u017b"+
		"\u0003Z-\u0000\u017a\u0179\u0001\u0000\u0000\u0000\u017a\u017b\u0001\u0000"+
		"\u0000\u0000\u017b\u017c\u0001\u0000\u0000\u0000\u017c\u0180\u0005+\u0000"+
		"\u0000\u017d\u017f\u0003\u0014\n\u0000\u017e\u017d\u0001\u0000\u0000\u0000"+
		"\u017f\u0182\u0001\u0000\u0000\u0000\u0180\u017e\u0001\u0000\u0000\u0000"+
		"\u0180\u0181\u0001\u0000\u0000\u0000\u0181\u0184\u0001\u0000\u0000\u0000"+
		"\u0182\u0180\u0001\u0000\u0000\u0000\u0183\u0185\u0003\u001e\u000f\u0000"+
		"\u0184\u0183\u0001\u0000\u0000\u0000\u0184\u0185\u0001\u0000\u0000\u0000"+
		"\u0185\u0186\u0001\u0000\u0000\u0000\u0186\u0196\u0005,\u0000\u0000\u0187"+
		"\u018b\u0005*\u0000\u0000\u0188\u018a\u0003\u0014\n\u0000\u0189\u0188"+
		"\u0001\u0000\u0000\u0000\u018a\u018d\u0001\u0000\u0000\u0000\u018b\u0189"+
		"\u0001\u0000\u0000\u0000\u018b\u018c\u0001\u0000\u0000\u0000\u018c\u018f"+
		"\u0001\u0000\u0000\u0000\u018d\u018b\u0001\u0000\u0000\u0000\u018e\u0190"+
		"\u0003\u001e\u000f\u0000\u018f\u018e\u0001\u0000\u0000\u0000\u018f\u0190"+
		"\u0001\u0000\u0000\u0000\u0190\u0192\u0001\u0000\u0000\u0000\u0191\u0193"+
		"\u0003X,\u0000\u0192\u0191\u0001\u0000\u0000\u0000\u0192\u0193\u0001\u0000"+
		"\u0000\u0000\u0193\u0194\u0001\u0000\u0000\u0000\u0194\u0196\u0005,\u0000"+
		"\u0000\u0195\u0178\u0001\u0000\u0000\u0000\u0195\u0187\u0001\u0000\u0000"+
		"\u0000\u0196W\u0001\u0000\u0000\u0000\u0197\u0198\u0005\u0007\u0000\u0000"+
		"\u0198Y\u0001\u0000\u0000\u0000\u0199\u019e\u0003\\.\u0000\u019a\u019b"+
		"\u0005\u000e\u0000\u0000\u019b\u019d\u0003\\.\u0000\u019c\u019a\u0001"+
		"\u0000\u0000\u0000\u019d\u01a0\u0001\u0000\u0000\u0000\u019e\u019c\u0001"+
		"\u0000\u0000\u0000\u019e\u019f\u0001\u0000\u0000\u0000\u019f\u01a2\u0001"+
		"\u0000\u0000\u0000\u01a0\u019e\u0001\u0000\u0000\u0000\u01a1\u01a3\u0005"+
		"\u000e\u0000\u0000\u01a2\u01a1\u0001\u0000\u0000\u0000\u01a2\u01a3\u0001"+
		"\u0000\u0000\u0000\u01a3[\u0001\u0000\u0000\u0000\u01a4\u01a7\u0005-\u0000"+
		"\u0000\u01a5\u01a6\u0005\u0005\u0000\u0000\u01a6\u01a8\u0003\u001e\u000f"+
		"\u0000\u01a7\u01a5\u0001\u0000\u0000\u0000\u01a7\u01a8\u0001\u0000\u0000"+
		"\u0000\u01a8]\u0001\u0000\u0000\u0000.nru\u007f\u0090\u0098\u009d\u00a3"+
		"\u00a7\u00aa\u00ae\u00b6\u00b9\u00c1\u00c9\u00d0\u00da\u00e5\u00f0\u00fb"+
		"\u0107\u011d\u0124\u0126\u0128\u0131\u013a\u0144\u0147\u014a\u0154\u0157"+
		"\u015a\u0160\u0172\u0176\u017a\u0180\u0184\u018b\u018f\u0192\u0195\u019e"+
		"\u01a2\u01a7";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}