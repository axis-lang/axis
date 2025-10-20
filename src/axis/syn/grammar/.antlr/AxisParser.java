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
		T__38=39, T__39=40, T__40=41, T__41=42, T__42=43, T__43=44, T__44=45, 
		T__45=46, T__46=47, T__47=48, ID=49, DECIMAL=50, TEXT=51, WS=52, COMMENT=53;
	public static final int
		RULE_unitItem = 0, RULE_modItem = 1, RULE_defItem = 2, RULE_valItem = 3, 
		RULE_tupleBlockValElement = 4, RULE_tupleBlockVarElement = 5, RULE_tupleBlockLetElement = 6, 
		RULE_tupleBlockDynElement = 7, RULE_tupleBlockMutElement = 8, RULE_useBlock = 9, 
		RULE_defWhereBlock = 10, RULE_defTakesBlock = 11, RULE_defReturnsBlock = 12, 
		RULE_suiteBlock = 13, RULE_suite = 14, RULE_statement = 15, RULE_valStatement = 16, 
		RULE_pattern = 17, RULE_tuplePattern = 18, RULE_tuplePatternElement = 19, 
		RULE_expr = 20, RULE_compoundExpr = 21, RULE_rangeExpr = 22, RULE_rangeOp = 23, 
		RULE_logicExpr = 24, RULE_logicOp = 25, RULE_comparisonExpr = 26, RULE_comparisonOp = 27, 
		RULE_additiveExpr = 28, RULE_additiveOp = 29, RULE_productiveExpr = 30, 
		RULE_productiveOp = 31, RULE_prefixExpr = 32, RULE_signOp = 33, RULE_etcOp = 34, 
		RULE_prefixOp = 35, RULE_postfixExpr = 36, RULE_primaryExpr = 37, RULE_ellipsisExpr = 38, 
		RULE_wildcardExpr = 39, RULE_symExpr = 40, RULE_litExpr = 41, RULE_tupleExpr = 42, 
		RULE_shapeExpr = 43, RULE_tupleElement = 44, RULE_tuplePositionalElement = 45, 
		RULE_tupleNominalElement = 46, RULE_tupleSpreadElement = 47, RULE_lambda = 48, 
		RULE_semicolon = 49, RULE_lambdaParams = 50, RULE_lambdaParam = 51;
	private static String[] makeRuleNames() {
		return new String[] {
			"unitItem", "modItem", "defItem", "valItem", "tupleBlockValElement", 
			"tupleBlockVarElement", "tupleBlockLetElement", "tupleBlockDynElement", 
			"tupleBlockMutElement", "useBlock", "defWhereBlock", "defTakesBlock", 
			"defReturnsBlock", "suiteBlock", "suite", "statement", "valStatement", 
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
			null, "'unit'", "'mod'", "'def'", "'val'", "':'", "'='", "'var'", "'let'", 
			"'dyn'", "'mut'", "'use'", "'where'", "'takes'", "'returns'", "'suite'", 
			"'('", "','", "')'", "'..='", "'..<'", "'&&'", "'||'", "'=='", "'!='", 
			"'<'", "'<='", "'>'", "'>='", "'+'", "'-'", "'*'", "'/'", "'%'", "'\\u00B7'", 
			"'~'", "'!'", "'..'", "'.'", "'::'", "'...'", "'_'", "'@'", "'['", "']'", 
			"'{'", "'->'", "'}'", "';'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, "ID", "DECIMAL", "TEXT", "WS", "COMMENT"
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
			setState(104);
			match(T__0);
			setState(105);
			expr();
			setState(106);
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
			setState(108);
			match(T__1);
			setState(109);
			expr();
			setState(110);
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
			setState(112);
			match(T__2);
			setState(113);
			expr();
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
			setState(116);
			match(T__3);
			setState(117);
			expr();
			setState(120);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(118);
				match(T__4);
				setState(119);
				expr();
				}
			}

			setState(124);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(122);
				match(T__5);
				setState(123);
				expr();
				}
			}

			setState(126);
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
	public static class TupleBlockValElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TupleBlockValElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleBlockValElement; }
	}

	public final TupleBlockValElementContext tupleBlockValElement() throws RecognitionException {
		TupleBlockValElementContext _localctx = new TupleBlockValElementContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_tupleBlockValElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(128);
			match(T__3);
			setState(129);
			expr();
			setState(132);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(130);
				match(T__4);
				setState(131);
				expr();
				}
			}

			setState(136);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(134);
				match(T__5);
				setState(135);
				expr();
				}
			}

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
	public static class TupleBlockVarElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TupleBlockVarElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleBlockVarElement; }
	}

	public final TupleBlockVarElementContext tupleBlockVarElement() throws RecognitionException {
		TupleBlockVarElementContext _localctx = new TupleBlockVarElementContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_tupleBlockVarElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(140);
			match(T__6);
			setState(141);
			expr();
			setState(144);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(142);
				match(T__4);
				setState(143);
				expr();
				}
			}

			setState(148);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(146);
				match(T__5);
				setState(147);
				expr();
				}
			}

			setState(150);
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
	public static class TupleBlockLetElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TupleBlockLetElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleBlockLetElement; }
	}

	public final TupleBlockLetElementContext tupleBlockLetElement() throws RecognitionException {
		TupleBlockLetElementContext _localctx = new TupleBlockLetElementContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_tupleBlockLetElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(152);
			match(T__7);
			setState(153);
			expr();
			setState(156);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(154);
				match(T__4);
				setState(155);
				expr();
				}
			}

			setState(160);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(158);
				match(T__5);
				setState(159);
				expr();
				}
			}

			setState(162);
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
	public static class TupleBlockDynElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TupleBlockDynElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleBlockDynElement; }
	}

	public final TupleBlockDynElementContext tupleBlockDynElement() throws RecognitionException {
		TupleBlockDynElementContext _localctx = new TupleBlockDynElementContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_tupleBlockDynElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(164);
			match(T__8);
			setState(165);
			expr();
			setState(168);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(166);
				match(T__4);
				setState(167);
				expr();
				}
			}

			setState(172);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(170);
				match(T__5);
				setState(171);
				expr();
				}
			}

			setState(174);
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
	public static class TupleBlockMutElementContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public TupleBlockMutElementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_tupleBlockMutElement; }
	}

	public final TupleBlockMutElementContext tupleBlockMutElement() throws RecognitionException {
		TupleBlockMutElementContext _localctx = new TupleBlockMutElementContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_tupleBlockMutElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(176);
			match(T__9);
			setState(177);
			expr();
			setState(180);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(178);
				match(T__4);
				setState(179);
				expr();
				}
			}

			setState(184);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(182);
				match(T__5);
				setState(183);
				expr();
				}
			}

			setState(186);
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
		enterRule(_localctx, 18, RULE_useBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(188);
			match(T__10);
			setState(189);
			expr();
			setState(190);
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
	public static class DefWhereBlockContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public DefWhereBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_defWhereBlock; }
	}

	public final DefWhereBlockContext defWhereBlock() throws RecognitionException {
		DefWhereBlockContext _localctx = new DefWhereBlockContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_defWhereBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(192);
			match(T__11);
			setState(193);
			match(T__4);
			setState(194);
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
	public static class DefTakesBlockContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public DefTakesBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_defTakesBlock; }
	}

	public final DefTakesBlockContext defTakesBlock() throws RecognitionException {
		DefTakesBlockContext _localctx = new DefTakesBlockContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_defTakesBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(196);
			match(T__12);
			setState(198);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
				{
				setState(197);
				expr();
				}
			}

			setState(200);
			match(T__4);
			setState(201);
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
	public static class DefReturnsBlockContext extends ParserRuleContext {
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TerminalNode EOF() { return getToken(AxisParser.EOF, 0); }
		public DefReturnsBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_defReturnsBlock; }
	}

	public final DefReturnsBlockContext defReturnsBlock() throws RecognitionException {
		DefReturnsBlockContext _localctx = new DefReturnsBlockContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_defReturnsBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(203);
			match(T__13);
			setState(204);
			expr();
			setState(205);
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
		enterRule(_localctx, 26, RULE_suiteBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(207);
			match(T__14);
			setState(211);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768208L) != 0)) {
				{
				{
				setState(208);
				statement();
				}
				}
				setState(213);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(214);
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
		enterRule(_localctx, 28, RULE_suite);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(219);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768208L) != 0)) {
				{
				{
				setState(216);
				statement();
				}
				}
				setState(221);
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
		enterRule(_localctx, 30, RULE_statement);
		try {
			setState(224);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__3:
				enterOuterAlt(_localctx, 1);
				{
				setState(222);
				valStatement();
				}
				break;
			case T__15:
			case T__28:
			case T__29:
			case T__34:
			case T__35:
			case T__36:
			case T__39:
			case T__40:
			case T__44:
			case ID:
			case DECIMAL:
			case TEXT:
				enterOuterAlt(_localctx, 2);
				{
				setState(223);
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
		enterRule(_localctx, 32, RULE_valStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(226);
			match(T__3);
			{
			setState(227);
			pattern();
			}
			setState(230);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(228);
				match(T__4);
				setState(229);
				expr();
				}
			}

			setState(234);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__5) {
				{
				setState(232);
				match(T__5);
				setState(233);
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
		enterRule(_localctx, 34, RULE_pattern);
		try {
			setState(238);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(236);
				match(ID);
				}
				break;
			case T__15:
				enterOuterAlt(_localctx, 2);
				{
				setState(237);
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
		enterRule(_localctx, 36, RULE_tuplePattern);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(240);
			match(T__15);
			setState(249);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(241);
				tuplePatternElement();
				setState(246);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==T__16) {
					{
					{
					setState(242);
					match(T__16);
					setState(243);
					tuplePatternElement();
					}
					}
					setState(248);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
			}

			setState(251);
			match(T__17);
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
		enterRule(_localctx, 38, RULE_tuplePatternElement);
		try {
			setState(257);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,21,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(253);
				match(ID);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(254);
				match(ID);
				setState(255);
				match(T__4);
				setState(256);
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
		enterRule(_localctx, 40, RULE_expr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(259);
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
		enterRule(_localctx, 42, RULE_compoundExpr);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(261);
			rangeExpr();
			setState(265);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,22,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(262);
					rangeExpr();
					}
					} 
				}
				setState(267);
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
		enterRule(_localctx, 44, RULE_rangeExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(268);
			logicExpr();
			setState(272);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__18 || _la==T__19) {
				{
				setState(269);
				rangeOp();
				setState(270);
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
		enterRule(_localctx, 46, RULE_rangeOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(274);
			_la = _input.LA(1);
			if ( !(_la==T__18 || _la==T__19) ) {
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
		enterRule(_localctx, 48, RULE_logicExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(276);
			comparisonExpr();
			setState(282);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==T__20 || _la==T__21) {
				{
				{
				setState(277);
				logicOp();
				setState(278);
				comparisonExpr();
				}
				}
				setState(284);
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
		enterRule(_localctx, 50, RULE_logicOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(285);
			_la = _input.LA(1);
			if ( !(_la==T__20 || _la==T__21) ) {
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
		enterRule(_localctx, 52, RULE_comparisonExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(287);
			additiveExpr();
			setState(293);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 528482304L) != 0)) {
				{
				{
				setState(288);
				comparisonOp();
				setState(289);
				additiveExpr();
				}
				}
				setState(295);
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
		enterRule(_localctx, 54, RULE_comparisonOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(296);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 528482304L) != 0)) ) {
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
		enterRule(_localctx, 56, RULE_additiveExpr);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(298);
			productiveExpr();
			setState(304);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,26,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(299);
					additiveOp();
					setState(300);
					productiveExpr();
					}
					} 
				}
				setState(306);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,26,_ctx);
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
		enterRule(_localctx, 58, RULE_additiveOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(307);
			_la = _input.LA(1);
			if ( !(_la==T__28 || _la==T__29) ) {
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
		enterRule(_localctx, 60, RULE_productiveExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(309);
			prefixExpr();
			setState(315);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 32212254720L) != 0)) {
				{
				{
				setState(310);
				productiveOp();
				setState(311);
				prefixExpr();
				}
				}
				setState(317);
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
		enterRule(_localctx, 62, RULE_productiveOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(318);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 32212254720L) != 0)) ) {
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
		enterRule(_localctx, 64, RULE_prefixExpr);
		try {
			setState(327);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__15:
			case T__39:
			case T__40:
			case T__44:
			case ID:
			case DECIMAL:
			case TEXT:
				_localctx = new PrefixPassContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(320);
				postfixExpr(0);
				}
				break;
			case T__36:
				_localctx = new EtcExprContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(321);
				etcOp();
				setState(322);
				prefixExpr();
				}
				break;
			case T__28:
			case T__29:
			case T__34:
			case T__35:
				_localctx = new SignExprContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(324);
				signOp();
				setState(325);
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
		enterRule(_localctx, 66, RULE_signOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(329);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 104689827840L) != 0)) ) {
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
		enterRule(_localctx, 68, RULE_etcOp);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(331);
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
	public static class PrefixOpContext extends ParserRuleContext {
		public PrefixOpContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_prefixOp; }
	}

	public final PrefixOpContext prefixOp() throws RecognitionException {
		PrefixOpContext _localctx = new PrefixOpContext(_ctx, getState());
		enterRule(_localctx, 70, RULE_prefixOp);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(333);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 242128781312L) != 0)) ) {
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
		int _startState = 72;
		enterRecursionRule(_localctx, 72, RULE_postfixExpr, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			{
			_localctx = new PostfixPassContext(_localctx);
			_ctx = _localctx;
			_prevctx = _localctx;

			setState(336);
			primaryExpr();
			}
			_ctx.stop = _input.LT(-1);
			setState(360);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,32,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(358);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,31,_ctx) ) {
					case 1:
						{
						_localctx = new TrailExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(338);
						if (!(precpred(_ctx, 5))) throw new FailedPredicateException(this, "precpred(_ctx, 5)");
						setState(339);
						lambda();
						}
						break;
					case 2:
						{
						_localctx = new ApplyExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(340);
						if (!(precpred(_ctx, 4))) throw new FailedPredicateException(this, "precpred(_ctx, 4)");
						setState(341);
						tupleExpr();
						}
						break;
					case 3:
						{
						_localctx = new IndexExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(342);
						if (!(precpred(_ctx, 3))) throw new FailedPredicateException(this, "precpred(_ctx, 3)");
						setState(343);
						shapeExpr();
						}
						break;
					case 4:
						{
						_localctx = new MemberExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(344);
						if (!(precpred(_ctx, 2))) throw new FailedPredicateException(this, "precpred(_ctx, 2)");
						setState(347); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(345);
								match(T__37);
								setState(346);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(349); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,29,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					case 5:
						{
						_localctx = new ScopeExprContext(new PostfixExprContext(_parentctx, _parentState));
						pushNewRecursionContext(_localctx, _startState, RULE_postfixExpr);
						setState(351);
						if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
						setState(354); 
						_errHandler.sync(this);
						_alt = 1;
						do {
							switch (_alt) {
							case 1:
								{
								{
								setState(352);
								match(T__38);
								setState(353);
								match(ID);
								}
								}
								break;
							default:
								throw new NoViableAltException(this);
							}
							setState(356); 
							_errHandler.sync(this);
							_alt = getInterpreter().adaptivePredict(_input,30,_ctx);
						} while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER );
						}
						break;
					}
					} 
				}
				setState(362);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,32,_ctx);
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
		enterRule(_localctx, 74, RULE_primaryExpr);
		try {
			setState(369);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case T__40:
				enterOuterAlt(_localctx, 1);
				{
				setState(363);
				wildcardExpr();
				}
				break;
			case T__39:
				enterOuterAlt(_localctx, 2);
				{
				setState(364);
				ellipsisExpr();
				}
				break;
			case ID:
				enterOuterAlt(_localctx, 3);
				{
				setState(365);
				symExpr();
				}
				break;
			case DECIMAL:
			case TEXT:
				enterOuterAlt(_localctx, 4);
				{
				setState(366);
				litExpr();
				}
				break;
			case T__15:
				enterOuterAlt(_localctx, 5);
				{
				setState(367);
				tupleExpr();
				}
				break;
			case T__44:
				enterOuterAlt(_localctx, 6);
				{
				setState(368);
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
		enterRule(_localctx, 76, RULE_ellipsisExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(371);
			match(T__39);
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
		enterRule(_localctx, 78, RULE_wildcardExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(373);
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
		enterRule(_localctx, 80, RULE_symExpr);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(375);
			match(ID);
			setState(378);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,34,_ctx) ) {
			case 1:
				{
				setState(376);
				match(T__41);
				setState(377);
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
		enterRule(_localctx, 82, RULE_litExpr);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(380);
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
		enterRule(_localctx, 84, RULE_tupleExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(382);
			match(T__15);
			setState(391);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
				{
				setState(383);
				tupleElement();
				setState(388);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,35,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(384);
						match(T__16);
						setState(385);
						tupleElement();
						}
						} 
					}
					setState(390);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,35,_ctx);
				}
				}
			}

			setState(394);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__16) {
				{
				setState(393);
				match(T__16);
				}
			}

			setState(396);
			match(T__17);
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
		enterRule(_localctx, 86, RULE_shapeExpr);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(398);
			match(T__42);
			setState(407);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
				{
				setState(399);
				tupleElement();
				setState(404);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,38,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(400);
						match(T__16);
						setState(401);
						tupleElement();
						}
						} 
					}
					setState(406);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,38,_ctx);
				}
				}
			}

			setState(410);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__16) {
				{
				setState(409);
				match(T__16);
				}
			}

			setState(412);
			match(T__43);
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
		enterRule(_localctx, 88, RULE_tupleElement);
		try {
			setState(416);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,41,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(414);
				tuplePositionalElement();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(415);
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
		enterRule(_localctx, 90, RULE_tuplePositionalElement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(418);
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
		enterRule(_localctx, 92, RULE_tupleNominalElement);
		try {
			setState(434);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,42,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(420);
				expr();
				setState(421);
				match(T__4);
				setState(422);
				expr();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(424);
				expr();
				setState(425);
				match(T__5);
				setState(426);
				expr();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(428);
				expr();
				setState(429);
				match(T__4);
				setState(430);
				expr();
				setState(431);
				match(T__5);
				setState(432);
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
		enterRule(_localctx, 94, RULE_tupleSpreadElement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(436);
			match(T__36);
			setState(438);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
				{
				setState(437);
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
		enterRule(_localctx, 96, RULE_lambda);
		int _la;
		try {
			int _alt;
			setState(469);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,50,_ctx) ) {
			case 1:
				_localctx = new LambdaSuiteContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(440);
				match(T__44);
				setState(442);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==ID) {
					{
					setState(441);
					lambdaParams();
					}
				}

				setState(444);
				match(T__45);
				setState(448);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,45,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(445);
						statement();
						}
						} 
					}
					setState(450);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,45,_ctx);
				}
				setState(452);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
					{
					setState(451);
					expr();
					}
				}

				setState(454);
				match(T__46);
				}
				break;
			case 2:
				_localctx = new BasicSuiteContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(455);
				match(T__44);
				setState(459);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,47,_ctx);
				while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
					if ( _alt==1 ) {
						{
						{
						setState(456);
						statement();
						}
						} 
					}
					setState(461);
					_errHandler.sync(this);
					_alt = getInterpreter().adaptivePredict(_input,47,_ctx);
				}
				setState(463);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 3979374709768192L) != 0)) {
					{
					setState(462);
					expr();
					}
				}

				setState(466);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if (_la==T__47) {
					{
					setState(465);
					semicolon();
					}
				}

				setState(468);
				match(T__46);
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
		enterRule(_localctx, 98, RULE_semicolon);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(471);
			match(T__47);
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
		enterRule(_localctx, 100, RULE_lambdaParams);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(473);
			lambdaParam();
			setState(478);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,51,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(474);
					match(T__16);
					setState(475);
					lambdaParam();
					}
					} 
				}
				setState(480);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,51,_ctx);
			}
			setState(482);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__16) {
				{
				setState(481);
				match(T__16);
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
		enterRule(_localctx, 102, RULE_lambdaParam);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(484);
			match(ID);
			setState(487);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==T__4) {
				{
				setState(485);
				match(T__4);
				setState(486);
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
		case 36:
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
		"\u0004\u00015\u01ea\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
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
		"-\u0007-\u0002.\u0007.\u0002/\u0007/\u00020\u00070\u00021\u00071\u0002"+
		"2\u00072\u00023\u00073\u0001\u0000\u0001\u0000\u0001\u0000\u0001\u0000"+
		"\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0001\u0002\u0001\u0002"+
		"\u0001\u0002\u0001\u0002\u0001\u0003\u0001\u0003\u0001\u0003\u0001\u0003"+
		"\u0003\u0003y\b\u0003\u0001\u0003\u0001\u0003\u0003\u0003}\b\u0003\u0001"+
		"\u0003\u0001\u0003\u0001\u0004\u0001\u0004\u0001\u0004\u0001\u0004\u0003"+
		"\u0004\u0085\b\u0004\u0001\u0004\u0001\u0004\u0003\u0004\u0089\b\u0004"+
		"\u0001\u0004\u0001\u0004\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005"+
		"\u0003\u0005\u0091\b\u0005\u0001\u0005\u0001\u0005\u0003\u0005\u0095\b"+
		"\u0005\u0001\u0005\u0001\u0005\u0001\u0006\u0001\u0006\u0001\u0006\u0001"+
		"\u0006\u0003\u0006\u009d\b\u0006\u0001\u0006\u0001\u0006\u0003\u0006\u00a1"+
		"\b\u0006\u0001\u0006\u0001\u0006\u0001\u0007\u0001\u0007\u0001\u0007\u0001"+
		"\u0007\u0003\u0007\u00a9\b\u0007\u0001\u0007\u0001\u0007\u0003\u0007\u00ad"+
		"\b\u0007\u0001\u0007\u0001\u0007\u0001\b\u0001\b\u0001\b\u0001\b\u0003"+
		"\b\u00b5\b\b\u0001\b\u0001\b\u0003\b\u00b9\b\b\u0001\b\u0001\b\u0001\t"+
		"\u0001\t\u0001\t\u0001\t\u0001\n\u0001\n\u0001\n\u0001\n\u0001\u000b\u0001"+
		"\u000b\u0003\u000b\u00c7\b\u000b\u0001\u000b\u0001\u000b\u0001\u000b\u0001"+
		"\f\u0001\f\u0001\f\u0001\f\u0001\r\u0001\r\u0005\r\u00d2\b\r\n\r\f\r\u00d5"+
		"\t\r\u0001\r\u0001\r\u0001\u000e\u0005\u000e\u00da\b\u000e\n\u000e\f\u000e"+
		"\u00dd\t\u000e\u0001\u000f\u0001\u000f\u0003\u000f\u00e1\b\u000f\u0001"+
		"\u0010\u0001\u0010\u0001\u0010\u0001\u0010\u0003\u0010\u00e7\b\u0010\u0001"+
		"\u0010\u0001\u0010\u0003\u0010\u00eb\b\u0010\u0001\u0011\u0001\u0011\u0003"+
		"\u0011\u00ef\b\u0011\u0001\u0012\u0001\u0012\u0001\u0012\u0001\u0012\u0005"+
		"\u0012\u00f5\b\u0012\n\u0012\f\u0012\u00f8\t\u0012\u0003\u0012\u00fa\b"+
		"\u0012\u0001\u0012\u0001\u0012\u0001\u0013\u0001\u0013\u0001\u0013\u0001"+
		"\u0013\u0003\u0013\u0102\b\u0013\u0001\u0014\u0001\u0014\u0001\u0015\u0001"+
		"\u0015\u0005\u0015\u0108\b\u0015\n\u0015\f\u0015\u010b\t\u0015\u0001\u0016"+
		"\u0001\u0016\u0001\u0016\u0001\u0016\u0003\u0016\u0111\b\u0016\u0001\u0017"+
		"\u0001\u0017\u0001\u0018\u0001\u0018\u0001\u0018\u0001\u0018\u0005\u0018"+
		"\u0119\b\u0018\n\u0018\f\u0018\u011c\t\u0018\u0001\u0019\u0001\u0019\u0001"+
		"\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0005\u001a\u0124\b\u001a\n"+
		"\u001a\f\u001a\u0127\t\u001a\u0001\u001b\u0001\u001b\u0001\u001c\u0001"+
		"\u001c\u0001\u001c\u0001\u001c\u0005\u001c\u012f\b\u001c\n\u001c\f\u001c"+
		"\u0132\t\u001c\u0001\u001d\u0001\u001d\u0001\u001e\u0001\u001e\u0001\u001e"+
		"\u0001\u001e\u0005\u001e\u013a\b\u001e\n\u001e\f\u001e\u013d\t\u001e\u0001"+
		"\u001f\u0001\u001f\u0001 \u0001 \u0001 \u0001 \u0001 \u0001 \u0001 \u0003"+
		" \u0148\b \u0001!\u0001!\u0001\"\u0001\"\u0001#\u0001#\u0001$\u0001$\u0001"+
		"$\u0001$\u0001$\u0001$\u0001$\u0001$\u0001$\u0001$\u0001$\u0001$\u0004"+
		"$\u015c\b$\u000b$\f$\u015d\u0001$\u0001$\u0001$\u0004$\u0163\b$\u000b"+
		"$\f$\u0164\u0005$\u0167\b$\n$\f$\u016a\t$\u0001%\u0001%\u0001%\u0001%"+
		"\u0001%\u0001%\u0003%\u0172\b%\u0001&\u0001&\u0001\'\u0001\'\u0001(\u0001"+
		"(\u0001(\u0003(\u017b\b(\u0001)\u0001)\u0001*\u0001*\u0001*\u0001*\u0005"+
		"*\u0183\b*\n*\f*\u0186\t*\u0003*\u0188\b*\u0001*\u0003*\u018b\b*\u0001"+
		"*\u0001*\u0001+\u0001+\u0001+\u0001+\u0005+\u0193\b+\n+\f+\u0196\t+\u0003"+
		"+\u0198\b+\u0001+\u0003+\u019b\b+\u0001+\u0001+\u0001,\u0001,\u0003,\u01a1"+
		"\b,\u0001-\u0001-\u0001.\u0001.\u0001.\u0001.\u0001.\u0001.\u0001.\u0001"+
		".\u0001.\u0001.\u0001.\u0001.\u0001.\u0001.\u0003.\u01b3\b.\u0001/\u0001"+
		"/\u0003/\u01b7\b/\u00010\u00010\u00030\u01bb\b0\u00010\u00010\u00050\u01bf"+
		"\b0\n0\f0\u01c2\t0\u00010\u00030\u01c5\b0\u00010\u00010\u00010\u00050"+
		"\u01ca\b0\n0\f0\u01cd\t0\u00010\u00030\u01d0\b0\u00010\u00030\u01d3\b"+
		"0\u00010\u00030\u01d6\b0\u00011\u00011\u00012\u00012\u00012\u00052\u01dd"+
		"\b2\n2\f2\u01e0\t2\u00012\u00032\u01e3\b2\u00013\u00013\u00013\u00033"+
		"\u01e8\b3\u00013\u0000\u0001H4\u0000\u0002\u0004\u0006\b\n\f\u000e\u0010"+
		"\u0012\u0014\u0016\u0018\u001a\u001c\u001e \"$&(*,.02468:<>@BDFHJLNPR"+
		"TVXZ\\^`bdf\u0000\b\u0001\u0000\u0013\u0014\u0001\u0000\u0015\u0016\u0001"+
		"\u0000\u0017\u001c\u0001\u0000\u001d\u001e\u0001\u0000\u001f\"\u0002\u0000"+
		"\u001d\u001e#$\u0002\u0000\u001d\u001e#%\u0001\u000023\u01f4\u0000h\u0001"+
		"\u0000\u0000\u0000\u0002l\u0001\u0000\u0000\u0000\u0004p\u0001\u0000\u0000"+
		"\u0000\u0006t\u0001\u0000\u0000\u0000\b\u0080\u0001\u0000\u0000\u0000"+
		"\n\u008c\u0001\u0000\u0000\u0000\f\u0098\u0001\u0000\u0000\u0000\u000e"+
		"\u00a4\u0001\u0000\u0000\u0000\u0010\u00b0\u0001\u0000\u0000\u0000\u0012"+
		"\u00bc\u0001\u0000\u0000\u0000\u0014\u00c0\u0001\u0000\u0000\u0000\u0016"+
		"\u00c4\u0001\u0000\u0000\u0000\u0018\u00cb\u0001\u0000\u0000\u0000\u001a"+
		"\u00cf\u0001\u0000\u0000\u0000\u001c\u00db\u0001\u0000\u0000\u0000\u001e"+
		"\u00e0\u0001\u0000\u0000\u0000 \u00e2\u0001\u0000\u0000\u0000\"\u00ee"+
		"\u0001\u0000\u0000\u0000$\u00f0\u0001\u0000\u0000\u0000&\u0101\u0001\u0000"+
		"\u0000\u0000(\u0103\u0001\u0000\u0000\u0000*\u0105\u0001\u0000\u0000\u0000"+
		",\u010c\u0001\u0000\u0000\u0000.\u0112\u0001\u0000\u0000\u00000\u0114"+
		"\u0001\u0000\u0000\u00002\u011d\u0001\u0000\u0000\u00004\u011f\u0001\u0000"+
		"\u0000\u00006\u0128\u0001\u0000\u0000\u00008\u012a\u0001\u0000\u0000\u0000"+
		":\u0133\u0001\u0000\u0000\u0000<\u0135\u0001\u0000\u0000\u0000>\u013e"+
		"\u0001\u0000\u0000\u0000@\u0147\u0001\u0000\u0000\u0000B\u0149\u0001\u0000"+
		"\u0000\u0000D\u014b\u0001\u0000\u0000\u0000F\u014d\u0001\u0000\u0000\u0000"+
		"H\u014f\u0001\u0000\u0000\u0000J\u0171\u0001\u0000\u0000\u0000L\u0173"+
		"\u0001\u0000\u0000\u0000N\u0175\u0001\u0000\u0000\u0000P\u0177\u0001\u0000"+
		"\u0000\u0000R\u017c\u0001\u0000\u0000\u0000T\u017e\u0001\u0000\u0000\u0000"+
		"V\u018e\u0001\u0000\u0000\u0000X\u01a0\u0001\u0000\u0000\u0000Z\u01a2"+
		"\u0001\u0000\u0000\u0000\\\u01b2\u0001\u0000\u0000\u0000^\u01b4\u0001"+
		"\u0000\u0000\u0000`\u01d5\u0001\u0000\u0000\u0000b\u01d7\u0001\u0000\u0000"+
		"\u0000d\u01d9\u0001\u0000\u0000\u0000f\u01e4\u0001\u0000\u0000\u0000h"+
		"i\u0005\u0001\u0000\u0000ij\u0003(\u0014\u0000jk\u0005\u0000\u0000\u0001"+
		"k\u0001\u0001\u0000\u0000\u0000lm\u0005\u0002\u0000\u0000mn\u0003(\u0014"+
		"\u0000no\u0005\u0000\u0000\u0001o\u0003\u0001\u0000\u0000\u0000pq\u0005"+
		"\u0003\u0000\u0000qr\u0003(\u0014\u0000rs\u0005\u0000\u0000\u0001s\u0005"+
		"\u0001\u0000\u0000\u0000tu\u0005\u0004\u0000\u0000ux\u0003(\u0014\u0000"+
		"vw\u0005\u0005\u0000\u0000wy\u0003(\u0014\u0000xv\u0001\u0000\u0000\u0000"+
		"xy\u0001\u0000\u0000\u0000y|\u0001\u0000\u0000\u0000z{\u0005\u0006\u0000"+
		"\u0000{}\u0003(\u0014\u0000|z\u0001\u0000\u0000\u0000|}\u0001\u0000\u0000"+
		"\u0000}~\u0001\u0000\u0000\u0000~\u007f\u0005\u0000\u0000\u0001\u007f"+
		"\u0007\u0001\u0000\u0000\u0000\u0080\u0081\u0005\u0004\u0000\u0000\u0081"+
		"\u0084\u0003(\u0014\u0000\u0082\u0083\u0005\u0005\u0000\u0000\u0083\u0085"+
		"\u0003(\u0014\u0000\u0084\u0082\u0001\u0000\u0000\u0000\u0084\u0085\u0001"+
		"\u0000\u0000\u0000\u0085\u0088\u0001\u0000\u0000\u0000\u0086\u0087\u0005"+
		"\u0006\u0000\u0000\u0087\u0089\u0003(\u0014\u0000\u0088\u0086\u0001\u0000"+
		"\u0000\u0000\u0088\u0089\u0001\u0000\u0000\u0000\u0089\u008a\u0001\u0000"+
		"\u0000\u0000\u008a\u008b\u0005\u0000\u0000\u0001\u008b\t\u0001\u0000\u0000"+
		"\u0000\u008c\u008d\u0005\u0007\u0000\u0000\u008d\u0090\u0003(\u0014\u0000"+
		"\u008e\u008f\u0005\u0005\u0000\u0000\u008f\u0091\u0003(\u0014\u0000\u0090"+
		"\u008e\u0001\u0000\u0000\u0000\u0090\u0091\u0001\u0000\u0000\u0000\u0091"+
		"\u0094\u0001\u0000\u0000\u0000\u0092\u0093\u0005\u0006\u0000\u0000\u0093"+
		"\u0095\u0003(\u0014\u0000\u0094\u0092\u0001\u0000\u0000\u0000\u0094\u0095"+
		"\u0001\u0000\u0000\u0000\u0095\u0096\u0001\u0000\u0000\u0000\u0096\u0097"+
		"\u0005\u0000\u0000\u0001\u0097\u000b\u0001\u0000\u0000\u0000\u0098\u0099"+
		"\u0005\b\u0000\u0000\u0099\u009c\u0003(\u0014\u0000\u009a\u009b\u0005"+
		"\u0005\u0000\u0000\u009b\u009d\u0003(\u0014\u0000\u009c\u009a\u0001\u0000"+
		"\u0000\u0000\u009c\u009d\u0001\u0000\u0000\u0000\u009d\u00a0\u0001\u0000"+
		"\u0000\u0000\u009e\u009f\u0005\u0006\u0000\u0000\u009f\u00a1\u0003(\u0014"+
		"\u0000\u00a0\u009e\u0001\u0000\u0000\u0000\u00a0\u00a1\u0001\u0000\u0000"+
		"\u0000\u00a1\u00a2\u0001\u0000\u0000\u0000\u00a2\u00a3\u0005\u0000\u0000"+
		"\u0001\u00a3\r\u0001\u0000\u0000\u0000\u00a4\u00a5\u0005\t\u0000\u0000"+
		"\u00a5\u00a8\u0003(\u0014\u0000\u00a6\u00a7\u0005\u0005\u0000\u0000\u00a7"+
		"\u00a9\u0003(\u0014\u0000\u00a8\u00a6\u0001\u0000\u0000\u0000\u00a8\u00a9"+
		"\u0001\u0000\u0000\u0000\u00a9\u00ac\u0001\u0000\u0000\u0000\u00aa\u00ab"+
		"\u0005\u0006\u0000\u0000\u00ab\u00ad\u0003(\u0014\u0000\u00ac\u00aa\u0001"+
		"\u0000\u0000\u0000\u00ac\u00ad\u0001\u0000\u0000\u0000\u00ad\u00ae\u0001"+
		"\u0000\u0000\u0000\u00ae\u00af\u0005\u0000\u0000\u0001\u00af\u000f\u0001"+
		"\u0000\u0000\u0000\u00b0\u00b1\u0005\n\u0000\u0000\u00b1\u00b4\u0003("+
		"\u0014\u0000\u00b2\u00b3\u0005\u0005\u0000\u0000\u00b3\u00b5\u0003(\u0014"+
		"\u0000\u00b4\u00b2\u0001\u0000\u0000\u0000\u00b4\u00b5\u0001\u0000\u0000"+
		"\u0000\u00b5\u00b8\u0001\u0000\u0000\u0000\u00b6\u00b7\u0005\u0006\u0000"+
		"\u0000\u00b7\u00b9\u0003(\u0014\u0000\u00b8\u00b6\u0001\u0000\u0000\u0000"+
		"\u00b8\u00b9\u0001\u0000\u0000\u0000\u00b9\u00ba\u0001\u0000\u0000\u0000"+
		"\u00ba\u00bb\u0005\u0000\u0000\u0001\u00bb\u0011\u0001\u0000\u0000\u0000"+
		"\u00bc\u00bd\u0005\u000b\u0000\u0000\u00bd\u00be\u0003(\u0014\u0000\u00be"+
		"\u00bf\u0005\u0000\u0000\u0001\u00bf\u0013\u0001\u0000\u0000\u0000\u00c0"+
		"\u00c1\u0005\f\u0000\u0000\u00c1\u00c2\u0005\u0005\u0000\u0000\u00c2\u00c3"+
		"\u0005\u0000\u0000\u0001\u00c3\u0015\u0001\u0000\u0000\u0000\u00c4\u00c6"+
		"\u0005\r\u0000\u0000\u00c5\u00c7\u0003(\u0014\u0000\u00c6\u00c5\u0001"+
		"\u0000\u0000\u0000\u00c6\u00c7\u0001\u0000\u0000\u0000\u00c7\u00c8\u0001"+
		"\u0000\u0000\u0000\u00c8\u00c9\u0005\u0005\u0000\u0000\u00c9\u00ca\u0005"+
		"\u0000\u0000\u0001\u00ca\u0017\u0001\u0000\u0000\u0000\u00cb\u00cc\u0005"+
		"\u000e\u0000\u0000\u00cc\u00cd\u0003(\u0014\u0000\u00cd\u00ce\u0005\u0000"+
		"\u0000\u0001\u00ce\u0019\u0001\u0000\u0000\u0000\u00cf\u00d3\u0005\u000f"+
		"\u0000\u0000\u00d0\u00d2\u0003\u001e\u000f\u0000\u00d1\u00d0\u0001\u0000"+
		"\u0000\u0000\u00d2\u00d5\u0001\u0000\u0000\u0000\u00d3\u00d1\u0001\u0000"+
		"\u0000\u0000\u00d3\u00d4\u0001\u0000\u0000\u0000\u00d4\u00d6\u0001\u0000"+
		"\u0000\u0000\u00d5\u00d3\u0001\u0000\u0000\u0000\u00d6\u00d7\u0005\u0000"+
		"\u0000\u0001\u00d7\u001b\u0001\u0000\u0000\u0000\u00d8\u00da\u0003\u001e"+
		"\u000f\u0000\u00d9\u00d8\u0001\u0000\u0000\u0000\u00da\u00dd\u0001\u0000"+
		"\u0000\u0000\u00db\u00d9\u0001\u0000\u0000\u0000\u00db\u00dc\u0001\u0000"+
		"\u0000\u0000\u00dc\u001d\u0001\u0000\u0000\u0000\u00dd\u00db\u0001\u0000"+
		"\u0000\u0000\u00de\u00e1\u0003 \u0010\u0000\u00df\u00e1\u0003(\u0014\u0000"+
		"\u00e0\u00de\u0001\u0000\u0000\u0000\u00e0\u00df\u0001\u0000\u0000\u0000"+
		"\u00e1\u001f\u0001\u0000\u0000\u0000\u00e2\u00e3\u0005\u0004\u0000\u0000"+
		"\u00e3\u00e6\u0003\"\u0011\u0000\u00e4\u00e5\u0005\u0005\u0000\u0000\u00e5"+
		"\u00e7\u0003(\u0014\u0000\u00e6\u00e4\u0001\u0000\u0000\u0000\u00e6\u00e7"+
		"\u0001\u0000\u0000\u0000\u00e7\u00ea\u0001\u0000\u0000\u0000\u00e8\u00e9"+
		"\u0005\u0006\u0000\u0000\u00e9\u00eb\u0003(\u0014\u0000\u00ea\u00e8\u0001"+
		"\u0000\u0000\u0000\u00ea\u00eb\u0001\u0000\u0000\u0000\u00eb!\u0001\u0000"+
		"\u0000\u0000\u00ec\u00ef\u00051\u0000\u0000\u00ed\u00ef\u0003$\u0012\u0000"+
		"\u00ee\u00ec\u0001\u0000\u0000\u0000\u00ee\u00ed\u0001\u0000\u0000\u0000"+
		"\u00ef#\u0001\u0000\u0000\u0000\u00f0\u00f9\u0005\u0010\u0000\u0000\u00f1"+
		"\u00f6\u0003&\u0013\u0000\u00f2\u00f3\u0005\u0011\u0000\u0000\u00f3\u00f5"+
		"\u0003&\u0013\u0000\u00f4\u00f2\u0001\u0000\u0000\u0000\u00f5\u00f8\u0001"+
		"\u0000\u0000\u0000\u00f6\u00f4\u0001\u0000\u0000\u0000\u00f6\u00f7\u0001"+
		"\u0000\u0000\u0000\u00f7\u00fa\u0001\u0000\u0000\u0000\u00f8\u00f6\u0001"+
		"\u0000\u0000\u0000\u00f9\u00f1\u0001\u0000\u0000\u0000\u00f9\u00fa\u0001"+
		"\u0000\u0000\u0000\u00fa\u00fb\u0001\u0000\u0000\u0000\u00fb\u00fc\u0005"+
		"\u0012\u0000\u0000\u00fc%\u0001\u0000\u0000\u0000\u00fd\u0102\u00051\u0000"+
		"\u0000\u00fe\u00ff\u00051\u0000\u0000\u00ff\u0100\u0005\u0005\u0000\u0000"+
		"\u0100\u0102\u00051\u0000\u0000\u0101\u00fd\u0001\u0000\u0000\u0000\u0101"+
		"\u00fe\u0001\u0000\u0000\u0000\u0102\'\u0001\u0000\u0000\u0000\u0103\u0104"+
		"\u0003*\u0015\u0000\u0104)\u0001\u0000\u0000\u0000\u0105\u0109\u0003,"+
		"\u0016\u0000\u0106\u0108\u0003,\u0016\u0000\u0107\u0106\u0001\u0000\u0000"+
		"\u0000\u0108\u010b\u0001\u0000\u0000\u0000\u0109\u0107\u0001\u0000\u0000"+
		"\u0000\u0109\u010a\u0001\u0000\u0000\u0000\u010a+\u0001\u0000\u0000\u0000"+
		"\u010b\u0109\u0001\u0000\u0000\u0000\u010c\u0110\u00030\u0018\u0000\u010d"+
		"\u010e\u0003.\u0017\u0000\u010e\u010f\u00030\u0018\u0000\u010f\u0111\u0001"+
		"\u0000\u0000\u0000\u0110\u010d\u0001\u0000\u0000\u0000\u0110\u0111\u0001"+
		"\u0000\u0000\u0000\u0111-\u0001\u0000\u0000\u0000\u0112\u0113\u0007\u0000"+
		"\u0000\u0000\u0113/\u0001\u0000\u0000\u0000\u0114\u011a\u00034\u001a\u0000"+
		"\u0115\u0116\u00032\u0019\u0000\u0116\u0117\u00034\u001a\u0000\u0117\u0119"+
		"\u0001\u0000\u0000\u0000\u0118\u0115\u0001\u0000\u0000\u0000\u0119\u011c"+
		"\u0001\u0000\u0000\u0000\u011a\u0118\u0001\u0000\u0000\u0000\u011a\u011b"+
		"\u0001\u0000\u0000\u0000\u011b1\u0001\u0000\u0000\u0000\u011c\u011a\u0001"+
		"\u0000\u0000\u0000\u011d\u011e\u0007\u0001\u0000\u0000\u011e3\u0001\u0000"+
		"\u0000\u0000\u011f\u0125\u00038\u001c\u0000\u0120\u0121\u00036\u001b\u0000"+
		"\u0121\u0122\u00038\u001c\u0000\u0122\u0124\u0001\u0000\u0000\u0000\u0123"+
		"\u0120\u0001\u0000\u0000\u0000\u0124\u0127\u0001\u0000\u0000\u0000\u0125"+
		"\u0123\u0001\u0000\u0000\u0000\u0125\u0126\u0001\u0000\u0000\u0000\u0126"+
		"5\u0001\u0000\u0000\u0000\u0127\u0125\u0001\u0000\u0000\u0000\u0128\u0129"+
		"\u0007\u0002\u0000\u0000\u01297\u0001\u0000\u0000\u0000\u012a\u0130\u0003"+
		"<\u001e\u0000\u012b\u012c\u0003:\u001d\u0000\u012c\u012d\u0003<\u001e"+
		"\u0000\u012d\u012f\u0001\u0000\u0000\u0000\u012e\u012b\u0001\u0000\u0000"+
		"\u0000\u012f\u0132\u0001\u0000\u0000\u0000\u0130\u012e\u0001\u0000\u0000"+
		"\u0000\u0130\u0131\u0001\u0000\u0000\u0000\u01319\u0001\u0000\u0000\u0000"+
		"\u0132\u0130\u0001\u0000\u0000\u0000\u0133\u0134\u0007\u0003\u0000\u0000"+
		"\u0134;\u0001\u0000\u0000\u0000\u0135\u013b\u0003@ \u0000\u0136\u0137"+
		"\u0003>\u001f\u0000\u0137\u0138\u0003@ \u0000\u0138\u013a\u0001\u0000"+
		"\u0000\u0000\u0139\u0136\u0001\u0000\u0000\u0000\u013a\u013d\u0001\u0000"+
		"\u0000\u0000\u013b\u0139\u0001\u0000\u0000\u0000\u013b\u013c\u0001\u0000"+
		"\u0000\u0000\u013c=\u0001\u0000\u0000\u0000\u013d\u013b\u0001\u0000\u0000"+
		"\u0000\u013e\u013f\u0007\u0004\u0000\u0000\u013f?\u0001\u0000\u0000\u0000"+
		"\u0140\u0148\u0003H$\u0000\u0141\u0142\u0003D\"\u0000\u0142\u0143\u0003"+
		"@ \u0000\u0143\u0148\u0001\u0000\u0000\u0000\u0144\u0145\u0003B!\u0000"+
		"\u0145\u0146\u0003@ \u0000\u0146\u0148\u0001\u0000\u0000\u0000\u0147\u0140"+
		"\u0001\u0000\u0000\u0000\u0147\u0141\u0001\u0000\u0000\u0000\u0147\u0144"+
		"\u0001\u0000\u0000\u0000\u0148A\u0001\u0000\u0000\u0000\u0149\u014a\u0007"+
		"\u0005\u0000\u0000\u014aC\u0001\u0000\u0000\u0000\u014b\u014c\u0005%\u0000"+
		"\u0000\u014cE\u0001\u0000\u0000\u0000\u014d\u014e\u0007\u0006\u0000\u0000"+
		"\u014eG\u0001\u0000\u0000\u0000\u014f\u0150\u0006$\uffff\uffff\u0000\u0150"+
		"\u0151\u0003J%\u0000\u0151\u0168\u0001\u0000\u0000\u0000\u0152\u0153\n"+
		"\u0005\u0000\u0000\u0153\u0167\u0003`0\u0000\u0154\u0155\n\u0004\u0000"+
		"\u0000\u0155\u0167\u0003T*\u0000\u0156\u0157\n\u0003\u0000\u0000\u0157"+
		"\u0167\u0003V+\u0000\u0158\u015b\n\u0002\u0000\u0000\u0159\u015a\u0005"+
		"&\u0000\u0000\u015a\u015c\u00051\u0000\u0000\u015b\u0159\u0001\u0000\u0000"+
		"\u0000\u015c\u015d\u0001\u0000\u0000\u0000\u015d\u015b\u0001\u0000\u0000"+
		"\u0000\u015d\u015e\u0001\u0000\u0000\u0000\u015e\u0167\u0001\u0000\u0000"+
		"\u0000\u015f\u0162\n\u0001\u0000\u0000\u0160\u0161\u0005\'\u0000\u0000"+
		"\u0161\u0163\u00051\u0000\u0000\u0162\u0160\u0001\u0000\u0000\u0000\u0163"+
		"\u0164\u0001\u0000\u0000\u0000\u0164\u0162\u0001\u0000\u0000\u0000\u0164"+
		"\u0165\u0001\u0000\u0000\u0000\u0165\u0167\u0001\u0000\u0000\u0000\u0166"+
		"\u0152\u0001\u0000\u0000\u0000\u0166\u0154\u0001\u0000\u0000\u0000\u0166"+
		"\u0156\u0001\u0000\u0000\u0000\u0166\u0158\u0001\u0000\u0000\u0000\u0166"+
		"\u015f\u0001\u0000\u0000\u0000\u0167\u016a\u0001\u0000\u0000\u0000\u0168"+
		"\u0166\u0001\u0000\u0000\u0000\u0168\u0169\u0001\u0000\u0000\u0000\u0169"+
		"I\u0001\u0000\u0000\u0000\u016a\u0168\u0001\u0000\u0000\u0000\u016b\u0172"+
		"\u0003N\'\u0000\u016c\u0172\u0003L&\u0000\u016d\u0172\u0003P(\u0000\u016e"+
		"\u0172\u0003R)\u0000\u016f\u0172\u0003T*\u0000\u0170\u0172\u0003`0\u0000"+
		"\u0171\u016b\u0001\u0000\u0000\u0000\u0171\u016c\u0001\u0000\u0000\u0000"+
		"\u0171\u016d\u0001\u0000\u0000\u0000\u0171\u016e\u0001\u0000\u0000\u0000"+
		"\u0171\u016f\u0001\u0000\u0000\u0000\u0171\u0170\u0001\u0000\u0000\u0000"+
		"\u0172K\u0001\u0000\u0000\u0000\u0173\u0174\u0005(\u0000\u0000\u0174M"+
		"\u0001\u0000\u0000\u0000\u0175\u0176\u0005)\u0000\u0000\u0176O\u0001\u0000"+
		"\u0000\u0000\u0177\u017a\u00051\u0000\u0000\u0178\u0179\u0005*\u0000\u0000"+
		"\u0179\u017b\u00051\u0000\u0000\u017a\u0178\u0001\u0000\u0000\u0000\u017a"+
		"\u017b\u0001\u0000\u0000\u0000\u017bQ\u0001\u0000\u0000\u0000\u017c\u017d"+
		"\u0007\u0007\u0000\u0000\u017dS\u0001\u0000\u0000\u0000\u017e\u0187\u0005"+
		"\u0010\u0000\u0000\u017f\u0184\u0003X,\u0000\u0180\u0181\u0005\u0011\u0000"+
		"\u0000\u0181\u0183\u0003X,\u0000\u0182\u0180\u0001\u0000\u0000\u0000\u0183"+
		"\u0186\u0001\u0000\u0000\u0000\u0184\u0182\u0001\u0000\u0000\u0000\u0184"+
		"\u0185\u0001\u0000\u0000\u0000\u0185\u0188\u0001\u0000\u0000\u0000\u0186"+
		"\u0184\u0001\u0000\u0000\u0000\u0187\u017f\u0001\u0000\u0000\u0000\u0187"+
		"\u0188\u0001\u0000\u0000\u0000\u0188\u018a\u0001\u0000\u0000\u0000\u0189"+
		"\u018b\u0005\u0011\u0000\u0000\u018a\u0189\u0001\u0000\u0000\u0000\u018a"+
		"\u018b\u0001\u0000\u0000\u0000\u018b\u018c\u0001\u0000\u0000\u0000\u018c"+
		"\u018d\u0005\u0012\u0000\u0000\u018dU\u0001\u0000\u0000\u0000\u018e\u0197"+
		"\u0005+\u0000\u0000\u018f\u0194\u0003X,\u0000\u0190\u0191\u0005\u0011"+
		"\u0000\u0000\u0191\u0193\u0003X,\u0000\u0192\u0190\u0001\u0000\u0000\u0000"+
		"\u0193\u0196\u0001\u0000\u0000\u0000\u0194\u0192\u0001\u0000\u0000\u0000"+
		"\u0194\u0195\u0001\u0000\u0000\u0000\u0195\u0198\u0001\u0000\u0000\u0000"+
		"\u0196\u0194\u0001\u0000\u0000\u0000\u0197\u018f\u0001\u0000\u0000\u0000"+
		"\u0197\u0198\u0001\u0000\u0000\u0000\u0198\u019a\u0001\u0000\u0000\u0000"+
		"\u0199\u019b\u0005\u0011\u0000\u0000\u019a\u0199\u0001\u0000\u0000\u0000"+
		"\u019a\u019b\u0001\u0000\u0000\u0000\u019b\u019c\u0001\u0000\u0000\u0000"+
		"\u019c\u019d\u0005,\u0000\u0000\u019dW\u0001\u0000\u0000\u0000\u019e\u01a1"+
		"\u0003Z-\u0000\u019f\u01a1\u0003\\.\u0000\u01a0\u019e\u0001\u0000\u0000"+
		"\u0000\u01a0\u019f\u0001\u0000\u0000\u0000\u01a1Y\u0001\u0000\u0000\u0000"+
		"\u01a2\u01a3\u0003(\u0014\u0000\u01a3[\u0001\u0000\u0000\u0000\u01a4\u01a5"+
		"\u0003(\u0014\u0000\u01a5\u01a6\u0005\u0005\u0000\u0000\u01a6\u01a7\u0003"+
		"(\u0014\u0000\u01a7\u01b3\u0001\u0000\u0000\u0000\u01a8\u01a9\u0003(\u0014"+
		"\u0000\u01a9\u01aa\u0005\u0006\u0000\u0000\u01aa\u01ab\u0003(\u0014\u0000"+
		"\u01ab\u01b3\u0001\u0000\u0000\u0000\u01ac\u01ad\u0003(\u0014\u0000\u01ad"+
		"\u01ae\u0005\u0005\u0000\u0000\u01ae\u01af\u0003(\u0014\u0000\u01af\u01b0"+
		"\u0005\u0006\u0000\u0000\u01b0\u01b1\u0003(\u0014\u0000\u01b1\u01b3\u0001"+
		"\u0000\u0000\u0000\u01b2\u01a4\u0001\u0000\u0000\u0000\u01b2\u01a8\u0001"+
		"\u0000\u0000\u0000\u01b2\u01ac\u0001\u0000\u0000\u0000\u01b3]\u0001\u0000"+
		"\u0000\u0000\u01b4\u01b6\u0005%\u0000\u0000\u01b5\u01b7\u0003(\u0014\u0000"+
		"\u01b6\u01b5\u0001\u0000\u0000\u0000\u01b6\u01b7\u0001\u0000\u0000\u0000"+
		"\u01b7_\u0001\u0000\u0000\u0000\u01b8\u01ba\u0005-\u0000\u0000\u01b9\u01bb"+
		"\u0003d2\u0000\u01ba\u01b9\u0001\u0000\u0000\u0000\u01ba\u01bb\u0001\u0000"+
		"\u0000\u0000\u01bb\u01bc\u0001\u0000\u0000\u0000\u01bc\u01c0\u0005.\u0000"+
		"\u0000\u01bd\u01bf\u0003\u001e\u000f\u0000\u01be\u01bd\u0001\u0000\u0000"+
		"\u0000\u01bf\u01c2\u0001\u0000\u0000\u0000\u01c0\u01be\u0001\u0000\u0000"+
		"\u0000\u01c0\u01c1\u0001\u0000\u0000\u0000\u01c1\u01c4\u0001\u0000\u0000"+
		"\u0000\u01c2\u01c0\u0001\u0000\u0000\u0000\u01c3\u01c5\u0003(\u0014\u0000"+
		"\u01c4\u01c3\u0001\u0000\u0000\u0000\u01c4\u01c5\u0001\u0000\u0000\u0000"+
		"\u01c5\u01c6\u0001\u0000\u0000\u0000\u01c6\u01d6\u0005/\u0000\u0000\u01c7"+
		"\u01cb\u0005-\u0000\u0000\u01c8\u01ca\u0003\u001e\u000f\u0000\u01c9\u01c8"+
		"\u0001\u0000\u0000\u0000\u01ca\u01cd\u0001\u0000\u0000\u0000\u01cb\u01c9"+
		"\u0001\u0000\u0000\u0000\u01cb\u01cc\u0001\u0000\u0000\u0000\u01cc\u01cf"+
		"\u0001\u0000\u0000\u0000\u01cd\u01cb\u0001\u0000\u0000\u0000\u01ce\u01d0"+
		"\u0003(\u0014\u0000\u01cf\u01ce\u0001\u0000\u0000\u0000\u01cf\u01d0\u0001"+
		"\u0000\u0000\u0000\u01d0\u01d2\u0001\u0000\u0000\u0000\u01d1\u01d3\u0003"+
		"b1\u0000\u01d2\u01d1\u0001\u0000\u0000\u0000\u01d2\u01d3\u0001\u0000\u0000"+
		"\u0000\u01d3\u01d4\u0001\u0000\u0000\u0000\u01d4\u01d6\u0005/\u0000\u0000"+
		"\u01d5\u01b8\u0001\u0000\u0000\u0000\u01d5\u01c7\u0001\u0000\u0000\u0000"+
		"\u01d6a\u0001\u0000\u0000\u0000\u01d7\u01d8\u00050\u0000\u0000\u01d8c"+
		"\u0001\u0000\u0000\u0000\u01d9\u01de\u0003f3\u0000\u01da\u01db\u0005\u0011"+
		"\u0000\u0000\u01db\u01dd\u0003f3\u0000\u01dc\u01da\u0001\u0000\u0000\u0000"+
		"\u01dd\u01e0\u0001\u0000\u0000\u0000\u01de\u01dc\u0001\u0000\u0000\u0000"+
		"\u01de\u01df\u0001\u0000\u0000\u0000\u01df\u01e2\u0001\u0000\u0000\u0000"+
		"\u01e0\u01de\u0001\u0000\u0000\u0000\u01e1\u01e3\u0005\u0011\u0000\u0000"+
		"\u01e2\u01e1\u0001\u0000\u0000\u0000\u01e2\u01e3\u0001\u0000\u0000\u0000"+
		"\u01e3e\u0001\u0000\u0000\u0000\u01e4\u01e7\u00051\u0000\u0000\u01e5\u01e6"+
		"\u0005\u0005\u0000\u0000\u01e6\u01e8\u0003(\u0014\u0000\u01e7\u01e5\u0001"+
		"\u0000\u0000\u0000\u01e7\u01e8\u0001\u0000\u0000\u0000\u01e8g\u0001\u0000"+
		"\u0000\u00006x|\u0084\u0088\u0090\u0094\u009c\u00a0\u00a8\u00ac\u00b4"+
		"\u00b8\u00c6\u00d3\u00db\u00e0\u00e6\u00ea\u00ee\u00f6\u00f9\u0101\u0109"+
		"\u0110\u011a\u0125\u0130\u013b\u0147\u015d\u0164\u0166\u0168\u0171\u017a"+
		"\u0184\u0187\u018a\u0194\u0197\u019a\u01a0\u01b2\u01b6\u01ba\u01c0\u01c4"+
		"\u01cb\u01cf\u01d2\u01d5\u01de\u01e2\u01e7";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}