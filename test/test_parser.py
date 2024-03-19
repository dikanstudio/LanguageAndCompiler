import parsers.lang_simple.simple_parser as simpleParser
import parsers.lang_simple.simple_ast as ast
import parsers.lang_simple.simple_recursiveDescentParser as simpleRecDescP
import parsers.lang_simple.simpleAlternative_recursiveDescentParser as simpleAltRecDescP
import parsers.common as p
from common.constants import *
import pytest
import common.log as log

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
