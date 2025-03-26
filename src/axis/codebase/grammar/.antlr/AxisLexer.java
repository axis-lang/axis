// Generated from /home/jdluque/Workspace/prodisign/axis/src/axislang/grammar/Axis.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.misc.*;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue", "this-escape"})
public class AxisLexer extends Lexer {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, T__13=14, ID=15, DECIMAL=16, TEXT=17, 
		ADD=18, SUB=19, MUL=20, DIV=21, MOD=22, EQ=23, NE=24, LT=25, LE=26, GT=27, 
		GE=28, AND=29, OR=30, ARROW=31, WS=32, COMMENT=33;
	public static String[] channelNames = {
		"DEFAULT_TOKEN_CHANNEL", "HIDDEN"
	};

	public static String[] modeNames = {
		"DEFAULT_MODE"
	};

	private static String[] makeRuleNames() {
		return new String[] {
			"T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", "T__7", "T__8", 
			"T__9", "T__10", "T__11", "T__12", "T__13", "ID", "DECIMAL", "TEXT", 
			"ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", 
			"AND", "OR", "ARROW", "WS", "COMMENT"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'val'", "':'", "'='", "';'", "'('", "','", "')'", "'['", "']'", 
			"'.'", "'_'", "'..'", "'{'", "'}'", null, null, null, "'+'", "'-'", "'*'", 
			"'/'", "'%'", "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", "'&&'", "'||'", 
			"'->'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, null, null, null, 
			null, null, null, "ID", "DECIMAL", "TEXT", "ADD", "SUB", "MUL", "DIV", 
			"MOD", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR", "ARROW", "WS", 
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


	public AxisLexer(CharStream input) {
		super(input);
		_interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@Override
	public String getGrammarFileName() { return "Axis.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public String[] getChannelNames() { return channelNames; }

	@Override
	public String[] getModeNames() { return modeNames; }

	@Override
	public ATN getATN() { return _ATN; }

	public static final String _serializedATN =
		"\u0004\u0000!\u00b4\u0006\uffff\uffff\u0002\u0000\u0007\u0000\u0002\u0001"+
		"\u0007\u0001\u0002\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004"+
		"\u0007\u0004\u0002\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002\u0007"+
		"\u0007\u0007\u0002\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0002\u000b"+
		"\u0007\u000b\u0002\f\u0007\f\u0002\r\u0007\r\u0002\u000e\u0007\u000e\u0002"+
		"\u000f\u0007\u000f\u0002\u0010\u0007\u0010\u0002\u0011\u0007\u0011\u0002"+
		"\u0012\u0007\u0012\u0002\u0013\u0007\u0013\u0002\u0014\u0007\u0014\u0002"+
		"\u0015\u0007\u0015\u0002\u0016\u0007\u0016\u0002\u0017\u0007\u0017\u0002"+
		"\u0018\u0007\u0018\u0002\u0019\u0007\u0019\u0002\u001a\u0007\u001a\u0002"+
		"\u001b\u0007\u001b\u0002\u001c\u0007\u001c\u0002\u001d\u0007\u001d\u0002"+
		"\u001e\u0007\u001e\u0002\u001f\u0007\u001f\u0002 \u0007 \u0001\u0000\u0001"+
		"\u0000\u0001\u0000\u0001\u0000\u0001\u0001\u0001\u0001\u0001\u0002\u0001"+
		"\u0002\u0001\u0003\u0001\u0003\u0001\u0004\u0001\u0004\u0001\u0005\u0001"+
		"\u0005\u0001\u0006\u0001\u0006\u0001\u0007\u0001\u0007\u0001\b\u0001\b"+
		"\u0001\t\u0001\t\u0001\n\u0001\n\u0001\u000b\u0001\u000b\u0001\u000b\u0001"+
		"\f\u0001\f\u0001\r\u0001\r\u0001\u000e\u0001\u000e\u0005\u000ee\b\u000e"+
		"\n\u000e\f\u000eh\t\u000e\u0001\u000f\u0004\u000fk\b\u000f\u000b\u000f"+
		"\f\u000fl\u0001\u000f\u0001\u000f\u0004\u000fq\b\u000f\u000b\u000f\f\u000f"+
		"r\u0003\u000fu\b\u000f\u0001\u0010\u0001\u0010\u0001\u0010\u0001\u0010"+
		"\u0005\u0010{\b\u0010\n\u0010\f\u0010~\t\u0010\u0001\u0010\u0001\u0010"+
		"\u0001\u0011\u0001\u0011\u0001\u0012\u0001\u0012\u0001\u0013\u0001\u0013"+
		"\u0001\u0014\u0001\u0014\u0001\u0015\u0001\u0015\u0001\u0016\u0001\u0016"+
		"\u0001\u0016\u0001\u0017\u0001\u0017\u0001\u0017\u0001\u0018\u0001\u0018"+
		"\u0001\u0019\u0001\u0019\u0001\u0019\u0001\u001a\u0001\u001a\u0001\u001b"+
		"\u0001\u001b\u0001\u001b\u0001\u001c\u0001\u001c\u0001\u001c\u0001\u001d"+
		"\u0001\u001d\u0001\u001d\u0001\u001e\u0001\u001e\u0001\u001e\u0001\u001f"+
		"\u0004\u001f\u00a6\b\u001f\u000b\u001f\f\u001f\u00a7\u0001\u001f\u0001"+
		"\u001f\u0001 \u0001 \u0005 \u00ae\b \n \f \u00b1\t \u0001 \u0001 \u0000"+
		"\u0000!\u0001\u0001\u0003\u0002\u0005\u0003\u0007\u0004\t\u0005\u000b"+
		"\u0006\r\u0007\u000f\b\u0011\t\u0013\n\u0015\u000b\u0017\f\u0019\r\u001b"+
		"\u000e\u001d\u000f\u001f\u0010!\u0011#\u0012%\u0013\'\u0014)\u0015+\u0016"+
		"-\u0017/\u00181\u00193\u001a5\u001b7\u001c9\u001d;\u001e=\u001f? A!\u0001"+
		"\u0000\u0006\u0003\u0000AZ__az\u0004\u000009AZ__az\u0001\u000009\u0001"+
		"\u0000\'\'\u0003\u0000\t\n\r\r  \u0002\u0000\n\n\r\r\u00bb\u0000\u0001"+
		"\u0001\u0000\u0000\u0000\u0000\u0003\u0001\u0000\u0000\u0000\u0000\u0005"+
		"\u0001\u0000\u0000\u0000\u0000\u0007\u0001\u0000\u0000\u0000\u0000\t\u0001"+
		"\u0000\u0000\u0000\u0000\u000b\u0001\u0000\u0000\u0000\u0000\r\u0001\u0000"+
		"\u0000\u0000\u0000\u000f\u0001\u0000\u0000\u0000\u0000\u0011\u0001\u0000"+
		"\u0000\u0000\u0000\u0013\u0001\u0000\u0000\u0000\u0000\u0015\u0001\u0000"+
		"\u0000\u0000\u0000\u0017\u0001\u0000\u0000\u0000\u0000\u0019\u0001\u0000"+
		"\u0000\u0000\u0000\u001b\u0001\u0000\u0000\u0000\u0000\u001d\u0001\u0000"+
		"\u0000\u0000\u0000\u001f\u0001\u0000\u0000\u0000\u0000!\u0001\u0000\u0000"+
		"\u0000\u0000#\u0001\u0000\u0000\u0000\u0000%\u0001\u0000\u0000\u0000\u0000"+
		"\'\u0001\u0000\u0000\u0000\u0000)\u0001\u0000\u0000\u0000\u0000+\u0001"+
		"\u0000\u0000\u0000\u0000-\u0001\u0000\u0000\u0000\u0000/\u0001\u0000\u0000"+
		"\u0000\u00001\u0001\u0000\u0000\u0000\u00003\u0001\u0000\u0000\u0000\u0000"+
		"5\u0001\u0000\u0000\u0000\u00007\u0001\u0000\u0000\u0000\u00009\u0001"+
		"\u0000\u0000\u0000\u0000;\u0001\u0000\u0000\u0000\u0000=\u0001\u0000\u0000"+
		"\u0000\u0000?\u0001\u0000\u0000\u0000\u0000A\u0001\u0000\u0000\u0000\u0001"+
		"C\u0001\u0000\u0000\u0000\u0003G\u0001\u0000\u0000\u0000\u0005I\u0001"+
		"\u0000\u0000\u0000\u0007K\u0001\u0000\u0000\u0000\tM\u0001\u0000\u0000"+
		"\u0000\u000bO\u0001\u0000\u0000\u0000\rQ\u0001\u0000\u0000\u0000\u000f"+
		"S\u0001\u0000\u0000\u0000\u0011U\u0001\u0000\u0000\u0000\u0013W\u0001"+
		"\u0000\u0000\u0000\u0015Y\u0001\u0000\u0000\u0000\u0017[\u0001\u0000\u0000"+
		"\u0000\u0019^\u0001\u0000\u0000\u0000\u001b`\u0001\u0000\u0000\u0000\u001d"+
		"b\u0001\u0000\u0000\u0000\u001fj\u0001\u0000\u0000\u0000!v\u0001\u0000"+
		"\u0000\u0000#\u0081\u0001\u0000\u0000\u0000%\u0083\u0001\u0000\u0000\u0000"+
		"\'\u0085\u0001\u0000\u0000\u0000)\u0087\u0001\u0000\u0000\u0000+\u0089"+
		"\u0001\u0000\u0000\u0000-\u008b\u0001\u0000\u0000\u0000/\u008e\u0001\u0000"+
		"\u0000\u00001\u0091\u0001\u0000\u0000\u00003\u0093\u0001\u0000\u0000\u0000"+
		"5\u0096\u0001\u0000\u0000\u00007\u0098\u0001\u0000\u0000\u00009\u009b"+
		"\u0001\u0000\u0000\u0000;\u009e\u0001\u0000\u0000\u0000=\u00a1\u0001\u0000"+
		"\u0000\u0000?\u00a5\u0001\u0000\u0000\u0000A\u00ab\u0001\u0000\u0000\u0000"+
		"CD\u0005v\u0000\u0000DE\u0005a\u0000\u0000EF\u0005l\u0000\u0000F\u0002"+
		"\u0001\u0000\u0000\u0000GH\u0005:\u0000\u0000H\u0004\u0001\u0000\u0000"+
		"\u0000IJ\u0005=\u0000\u0000J\u0006\u0001\u0000\u0000\u0000KL\u0005;\u0000"+
		"\u0000L\b\u0001\u0000\u0000\u0000MN\u0005(\u0000\u0000N\n\u0001\u0000"+
		"\u0000\u0000OP\u0005,\u0000\u0000P\f\u0001\u0000\u0000\u0000QR\u0005)"+
		"\u0000\u0000R\u000e\u0001\u0000\u0000\u0000ST\u0005[\u0000\u0000T\u0010"+
		"\u0001\u0000\u0000\u0000UV\u0005]\u0000\u0000V\u0012\u0001\u0000\u0000"+
		"\u0000WX\u0005.\u0000\u0000X\u0014\u0001\u0000\u0000\u0000YZ\u0005_\u0000"+
		"\u0000Z\u0016\u0001\u0000\u0000\u0000[\\\u0005.\u0000\u0000\\]\u0005."+
		"\u0000\u0000]\u0018\u0001\u0000\u0000\u0000^_\u0005{\u0000\u0000_\u001a"+
		"\u0001\u0000\u0000\u0000`a\u0005}\u0000\u0000a\u001c\u0001\u0000\u0000"+
		"\u0000bf\u0007\u0000\u0000\u0000ce\u0007\u0001\u0000\u0000dc\u0001\u0000"+
		"\u0000\u0000eh\u0001\u0000\u0000\u0000fd\u0001\u0000\u0000\u0000fg\u0001"+
		"\u0000\u0000\u0000g\u001e\u0001\u0000\u0000\u0000hf\u0001\u0000\u0000"+
		"\u0000ik\u0007\u0002\u0000\u0000ji\u0001\u0000\u0000\u0000kl\u0001\u0000"+
		"\u0000\u0000lj\u0001\u0000\u0000\u0000lm\u0001\u0000\u0000\u0000mt\u0001"+
		"\u0000\u0000\u0000np\u0005.\u0000\u0000oq\u0007\u0002\u0000\u0000po\u0001"+
		"\u0000\u0000\u0000qr\u0001\u0000\u0000\u0000rp\u0001\u0000\u0000\u0000"+
		"rs\u0001\u0000\u0000\u0000su\u0001\u0000\u0000\u0000tn\u0001\u0000\u0000"+
		"\u0000tu\u0001\u0000\u0000\u0000u \u0001\u0000\u0000\u0000v|\u0005\'\u0000"+
		"\u0000w{\b\u0003\u0000\u0000xy\u0005\\\u0000\u0000y{\t\u0000\u0000\u0000"+
		"zw\u0001\u0000\u0000\u0000zx\u0001\u0000\u0000\u0000{~\u0001\u0000\u0000"+
		"\u0000|z\u0001\u0000\u0000\u0000|}\u0001\u0000\u0000\u0000}\u007f\u0001"+
		"\u0000\u0000\u0000~|\u0001\u0000\u0000\u0000\u007f\u0080\u0005\'\u0000"+
		"\u0000\u0080\"\u0001\u0000\u0000\u0000\u0081\u0082\u0005+\u0000\u0000"+
		"\u0082$\u0001\u0000\u0000\u0000\u0083\u0084\u0005-\u0000\u0000\u0084&"+
		"\u0001\u0000\u0000\u0000\u0085\u0086\u0005*\u0000\u0000\u0086(\u0001\u0000"+
		"\u0000\u0000\u0087\u0088\u0005/\u0000\u0000\u0088*\u0001\u0000\u0000\u0000"+
		"\u0089\u008a\u0005%\u0000\u0000\u008a,\u0001\u0000\u0000\u0000\u008b\u008c"+
		"\u0005=\u0000\u0000\u008c\u008d\u0005=\u0000\u0000\u008d.\u0001\u0000"+
		"\u0000\u0000\u008e\u008f\u0005!\u0000\u0000\u008f\u0090\u0005=\u0000\u0000"+
		"\u00900\u0001\u0000\u0000\u0000\u0091\u0092\u0005<\u0000\u0000\u00922"+
		"\u0001\u0000\u0000\u0000\u0093\u0094\u0005<\u0000\u0000\u0094\u0095\u0005"+
		"=\u0000\u0000\u00954\u0001\u0000\u0000\u0000\u0096\u0097\u0005>\u0000"+
		"\u0000\u00976\u0001\u0000\u0000\u0000\u0098\u0099\u0005>\u0000\u0000\u0099"+
		"\u009a\u0005=\u0000\u0000\u009a8\u0001\u0000\u0000\u0000\u009b\u009c\u0005"+
		"&\u0000\u0000\u009c\u009d\u0005&\u0000\u0000\u009d:\u0001\u0000\u0000"+
		"\u0000\u009e\u009f\u0005|\u0000\u0000\u009f\u00a0\u0005|\u0000\u0000\u00a0"+
		"<\u0001\u0000\u0000\u0000\u00a1\u00a2\u0005-\u0000\u0000\u00a2\u00a3\u0005"+
		">\u0000\u0000\u00a3>\u0001\u0000\u0000\u0000\u00a4\u00a6\u0007\u0004\u0000"+
		"\u0000\u00a5\u00a4\u0001\u0000\u0000\u0000\u00a6\u00a7\u0001\u0000\u0000"+
		"\u0000\u00a7\u00a5\u0001\u0000\u0000\u0000\u00a7\u00a8\u0001\u0000\u0000"+
		"\u0000\u00a8\u00a9\u0001\u0000\u0000\u0000\u00a9\u00aa\u0006\u001f\u0000"+
		"\u0000\u00aa@\u0001\u0000\u0000\u0000\u00ab\u00af\u0005#\u0000\u0000\u00ac"+
		"\u00ae\b\u0005\u0000\u0000\u00ad\u00ac\u0001\u0000\u0000\u0000\u00ae\u00b1"+
		"\u0001\u0000\u0000\u0000\u00af\u00ad\u0001\u0000\u0000\u0000\u00af\u00b0"+
		"\u0001\u0000\u0000\u0000\u00b0\u00b2\u0001\u0000\u0000\u0000\u00b1\u00af"+
		"\u0001\u0000\u0000\u0000\u00b2\u00b3\u0006 \u0000\u0000\u00b3B\u0001\u0000"+
		"\u0000\u0000\t\u0000flrtz|\u00a7\u00af\u0001\u0006\u0000\u0000";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}