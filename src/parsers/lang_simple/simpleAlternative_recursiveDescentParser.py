from parsers.common import *
from parsers.lang_simple.simple_ast import *
import common.log as log

# A hand-written recursive ascent parser for the following grammar:
# E → F + E | F
# F → z * F | z | ( E )
#
# NOTE: this parser is not equivalent to the one in simple_parser.py because for the hand-written
# parser, operators are right-associative for simplicity.

grammarPath = "./src/parsers/lang_simple/"

def parse(code: str):
    grammarFile = grammarPath + f"simple_grammar.lark"
    parser = mkParser('earley', grammarFile, 'exp') # only need the lexer
    lexed = parser.lex(code)
    toks = TokenStream(lexed)
    ast = ruleE(toks)
    toks.ensureEof(code)
    log.debug(f'AST: {ast}')
    return ast

# E → F + E | F
def ruleE(toks: TokenStream) -> exp:
    f = ruleF(toks)
    if toks.lookahead().type == 'PLUS':
        toks.next() # consume PLUS
        e = ruleE(toks)
        return BinOp(f, Add(), e)
    else:
        return f

# F → z * F | z | ( E )
def ruleF(toks: TokenStream) -> exp:
    t = toks.next()
    match t.type:
        # distinguish between alternatives z * F and z
        case 'INT':
            i = IntConst(int(t.value))
            if toks.lookahead().type == 'STAR':
                toks.next() # consume START
                f = ruleF(toks)
                return BinOp(i, Mul(), f)
            else:
                return i
        case 'LPAR':
            e = ruleE(toks)
            t2 = toks.next()
            if t2.type != 'RPAR':
                raise ParseError(f'Expected ")" not {t2}')
            return e
        case _:
            raise ParseError(f'Expected INT or "(" not {t}')
