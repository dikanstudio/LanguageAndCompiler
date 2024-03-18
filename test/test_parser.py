import parsers.lang_var.var_parser as varParser
import parsers.lang_simple.simple_parser as simpleParser
import parsers.lang_simple.simple_ast as ast
import parsers.lang_simple.simple_recursiveDescentParser as simpleRecDescP
import parsers.lang_simple.simpleAlternative_recursiveDescentParser as simpleAltRecDescP
import parsers.common as p
from common.constants import *
import common.utils as utils
import common.genericParser as genericParser
import lang_var.var_ast as var_ast
import pytest
import common.testsupport as testsupport
import common.log as log

def runParserTest(file: str, lang: str, alg: p.ParseAlg):
    code = utils.readTextFile(file)
    args = p.ParserArgs(code, alg, None, None)
    match lang:
        case "var":
            ast = varParser.parseModule(args)
            astViaPy = genericParser.parseFile(file, var_ast)
            assert ast == astViaPy
        case _:
            raise ValueError(f'Unsupported language for testing parsers: {lang}')

def params() -> list[tuple[str, str, str]]:
    l = testsupport.collectTestFiles(['test_files/parser'], ['var', 'simple'])
    algs = ['earley', 'lalr']
    return [(k, v, a) for (k, v) in l for a in algs]

@pytest.mark.parametrize("lang, srcFile, alg", params())
def test_parser(lang: str, srcFile: str, alg: p.ParseAlg):
    lang = asLanguage(lang)
    runParserTest(srcFile, lang, alg)

def test_ambiguous():
    code = 'print(1-2-3)'
    args = p.ParserArgs(code, 'earley', None, 'src/parsers/lang_var/var_grammar_ambiguous.lark')
    with pytest.raises(p.ParseError) as err:
        varParser.parseModule(args)
    assert 'multiple parse trees' in str(err)

def test_shiftReduceConflict():
    code = 'print(1)'
    args = p.ParserArgs(code, 'lalr', None, 'src/parsers/lang_var/var_grammar_lalr-conflict.lark')
    with pytest.raises(p.ParseError) as err:
        varParser.parseModule(args)
    assert 'Shift/Reduce conflict for terminal NEWLINE' in str(err)

def test_parseError():
    code = 'print(1-)'
    args = p.ParserArgs(code, 'lalr', None, None)
    with pytest.raises(p.ParseError) as err:
        varParser.parseModule(args)
    assert "Unexpected token Token('RPAR', ')') at line 1, column 9" in str(err)

simpleExp = '1 + 2 + 3 * 4'

def test_simpleParserManual():
    t = simpleParser.parse(p.ParserArgs(simpleExp, 'lalr', None, None))
    expected = ast.BinOp(ast.BinOp(ast.IntConst(1), ast.Add(), ast.IntConst(2)),
                         ast.Add(),
                         ast.BinOp(ast.IntConst(3), ast.Mul(), ast.IntConst(4)))
    assert t == expected

def test_simpleRecAscParserManual():
    t = simpleRecDescP.parse(simpleExp)
    expected = ast.BinOp(ast.BinOp(ast.IntConst(1), ast.Add(), ast.IntConst(2)),
                         ast.Add(),
                         ast.BinOp(ast.IntConst(3), ast.Mul(), ast.IntConst(4)))
    assert t == expected


def simpleExps():
    return [
        simpleExp,
        '1 + (2 + 3) * 4',
        '(((1+3)))',
        '3 * 4 * 5 + 1',
        '3 * 4 * (5 + 1)',
    ]

@pytest.mark.parametrize("s", simpleExps())
def test_simpleParser(s: str):
    log.debug(f'Test for parsing {repr(s)}')
    t1 = simpleParser.parse(p.ParserArgs(s, 'lalr', None, None))
    t2 = simpleRecDescP.parse(s)
    assert t1 == t2

def test_simpleAlternativeRecAscParserManual():
    t = simpleAltRecDescP.parse(simpleExp)
    expected = ast.BinOp(ast.IntConst(1),
                         ast.Add(),
                         ast.BinOp(ast.IntConst(2),
                                   ast.Add(),
                                   ast.BinOp(ast.IntConst(3), ast.Mul(), ast.IntConst(value=4))))
    assert t == expected
