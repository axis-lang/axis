from textwrap import dedent
from .abstract import *
from .expr import *
from .blocks import *
from .items import *
from .parsing import * 
from axis.dom import src

OUTLINE_SPEC: src.Outline[type[Block]] = src.Outline.build(
    src.Outline.Spec(
        type=Doc,
        keyword='---',
        separators="",
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Use,
        keyword='use',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Takes,
        keyword='takes',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
            src.Outline.Child(Val, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Returns,
        keyword='returns',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
            src.Outline.Child(Val, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Where,
        keyword='where',
        children=(
            src.Outline.Child(Val, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Suite,
        keyword='suite',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Unit,
        keyword='unit',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
            src.Outline.Child(Mod, src.Outline.Identation.SAME),
            src.Outline.Child(Use, src.Outline.Identation.SAME),
            src.Outline.Child(Val, src.Outline.Identation.SAME),
            src.Outline.Child(Def, src.Outline.Identation.SAME),
        )
    ),
    src.Outline.Spec(
        type=Mod,
        keyword='mod',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
            src.Outline.Child(Mod, src.Outline.Identation.NEST),
            src.Outline.Child(Use, src.Outline.Identation.NEST),
            src.Outline.Child(Val, src.Outline.Identation.NEST),
            src.Outline.Child(Def, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Val,
        keyword='val',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
        )
    ),
    src.Outline.Spec(
        type=Def,
        keyword='def',
        children=(
            src.Outline.Child(Doc, src.Outline.Identation.NEST),
            src.Outline.Child(Use, src.Outline.Identation.SAME),
            src.Outline.Child(Takes, src.Outline.Identation.SAME),
            src.Outline.Child(Where, src.Outline.Identation.SAME),
            src.Outline.Child(Returns, src.Outline.Identation.SAME),
            src.Outline.Child(Suite, src.Outline.Identation.SAME),
        )
    ),
)

def outline_transform_fn(tree: src.Outline.Tree) -> Block:
    """
    Transform a tree into a block.

    Args:
        tree (src.Outline.Tree): The tree to transform.

    Returns:
        Block: The transformed block.
    """
    return tree.rule.type(tree)



def ast_parser_for(block_type: type[Block]):
    from antlr4 import InputStream, CommonTokenStream
    from .grammar import AxisLexer, AxisParser

    prefix = block_type.__name__.lower()
    postfix = 'Item' if issubclass(block_type, syn.Item) else 'Block'
    item = f"{prefix}{postfix}" # e.g. "unitItem" or "suiteBlock"

    def parser(source: src.Span) -> dict:
        lexer = AxisLexer(InputStream(source.content))
        parser = AxisParser(CommonTokenStream(lexer))

        item_parser = getattr(parser, item, None)
        if item_parser is None:
            raise ValueError(f"Unknown parser for item {block_type} (search for {item})")

        tree = item_parser()

        if parser.getNumberOfSyntaxErrors() > 0:
            print(source.content)

        ast_builder = AstBuilder(source)
        result = ast_builder(tree)

        return result

        #return _itertree(tree, build_ast)

    return parser

PARSERS = {
    Doc: lambda source: dict(content=dedent(source.content)),
    Use: ast_parser_for(Use),
    Takes: ast_parser_for(Takes),
    Returns: ast_parser_for(Returns),
    Where: ast_parser_for(Where),
    Suite: ast_parser_for(Suite),
    Unit: ast_parser_for(Unit),
    Mod: ast_parser_for(Mod),
    Val: ast_parser_for(Val),
    Def: ast_parser_for(Def),
}

def outline_transform_fn(tree: src.Outline.Tree, children: tuple[Block]) -> Block:
    """
    Transform a tree into a block.

    Args:
        tree (src.Outline.Tree): The tree to transform.

    Returns:
        Block: The transformed block.
    """

    parser = PARSERS.get(tree.type, None)
    if parser is None:
        raise ValueError(f"Unknown parser for item {tree.type} (search for {tree.type})")
    
    attrs = parser(tree.span)
    return tree.type(children=children, **attrs)

