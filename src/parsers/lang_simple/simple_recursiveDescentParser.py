from parsers.common import *
from parsers.lang_simple.simple_ast import *
import common.log as log

# A hand-written recursive ascent parser for the following grammar:
# exp:    exp_1 expA
# expA:   "+" exp_1 expA   | /* empty */
# exp_1:  exp_2 exp_1A
# exp_1A: "*" exp_2 exp_1A | /* empty */
# exp_2:  INT              | "(" exp ")"
# This parser is equivalent to the one in simple_parser.py.

grammarPath = "./src/parsers/lang_simple/"

def parse(code: str):
    grammarFile = grammarPath + f"simple_grammar.lark"
    parser = mkParser('earley', grammarFile, 'exp') # only need the lexer
    lexed = parser.lex(code)
    toks = TokenStream(lexed)
    ast = ruleExp(toks)
    toks.ensureEof(code)
    log.debug(f'AST: {ast}')
    return ast

# exp: exp_1 expA
def ruleExp(toks: TokenStream) -> exp:
    e = ruleExp1(toks)
    return ruleExpA(e, toks)

# expA: "+" exp_1 expA | /* empty */
def ruleExpA(e1: exp, toks: TokenStream) -> exp:
    t = toks.lookahead()
    if t.type == 'PLUS':
        toks.next() # consume PLUS
        e2 = ruleExp1(toks)
        return ruleExpA(BinOp(e1, Add(), e2), toks)
    else:
        return e1

# exp_1:  exp_2 exp_1A
def ruleExp1(toks: TokenStream) -> exp:
    e = ruleExp2(toks)
    return ruleExp1A(e, toks)

# exp_1A: "*" exp_2 exp_1A | /* empty */
def ruleExp1A(e1: exp, toks: TokenStream) -> exp:
    t = toks.lookahead()
    if t.type == 'STAR':
        toks.next() # consume STAR
        e2 = ruleExp2(toks)
        return ruleExp1A(BinOp(e1, Mul(), e2), toks)
    else:
        return e1

# exp_2:  INT | "(" exp ")"
def ruleExp2(toks: TokenStream) -> exp:
    t = toks.next()
    match t.type:
        case 'INT':
            return IntConst(int(t.value))
        case 'LPAR':
            e = ruleExp(toks)
            t2 = toks.next()
            if t2.type != 'RPAR':
                raise ParseError(f'Expected ")" not {t2}')
            return e
        case _:
            raise ParseError(f'Expected INT or "(" not {t}')
