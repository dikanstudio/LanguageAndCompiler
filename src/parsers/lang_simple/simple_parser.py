from lark import ParseTree
from parsers.lang_simple.simple_ast import *
from parsers.common import *
import common.log as log

grammarPath = "./src/parsers/lang_simple/"

def parse(args: ParserArgs) -> exp:
    if args.grammarFile is None:
        grammarFile = grammarPath + f"simple_grammar.lark"
    else:
        grammarFile = args.grammarFile
    parser = mkParser(args.parseAlg, grammarFile, 'exp')
    parseTree = parseAsParseTree(parser, args.code, args.parseTreePng)
    ast = parseTreeToExpAst(parseTree)
    log.debug(f'AST: {ast}')
    return ast

def parseTreeToExpAst(t: ParseTree) -> exp:
    match t.data:
        case 'int_exp':
            return IntConst(int(asToken(t.children[0])))
        case 'add_exp':
            e1, e2 = [asTree(c) for c in t.children]
            return BinOp(parseTreeToExpAst(e1), Add(), parseTreeToExpAst(e2))
        case 'mul_exp':
            e1, e2 = [asTree(c) for c in t.children]
            return BinOp(parseTreeToExpAst(e1), Mul(), parseTreeToExpAst(e2))
        case 'exp_1' | 'exp_2' | 'paren_exp':
            return parseTreeToExpAst(asTree(t.children[0]))
        case kind:
            raise Exception(f'unhandled parse tree of kind {kind} for exp: {t}')
