import parsers.common as p
from common.constants import *
import pytest
import common.utils as utils
import common.genericParser as genericParser
import lang_var.var_ast as var_ast
import common.testsupport as testsupport

# NOTE: tests in this module are also executed in student repos. There is another module
# test_parserVar, which contains tests not executed in the student repo. The reason for
# this setup is that the parser for lang_var is not available to students.
def importModVarParser():
    return utils.importModuleNotInStudent('parsers.lang_var.var_parser')

def runParserTest(file: str, lang: str, alg: p.ParseAlg):
    code = utils.readTextFile(file)
    args = p.ParserArgs(code, alg, None, None)
    match lang:
        case "var":
            varParser = importModVarParser()
            ast = varParser.parseModule(args)
            astViaPy = genericParser.parseFile(file, var_ast)
            assert ast == astViaPy
        case _:
            raise ValueError(f'Unsupported language for testing parsers: {lang}')

def parserTestParams(langs: list[str]) -> list[tuple[str, str, str]]:
    l = testsupport.collectTestFiles(['test_files/parser'], langs)
    algs = ['earley', 'lalr']
    return [(k, v, a) for (k, v) in l for a in algs]

@pytest.mark.parametrize("lang, srcFile, alg", parserTestParams(['var']))
def test_varParser(lang: str, srcFile: str, alg: p.ParseAlg):
    lang = asLanguage(lang)
    runParserTest(srcFile, lang, alg)

def parseModule(args: p.ParserArgs):
    varParser = importModVarParser()
    return varParser.parseModule(args)

def test_ambiguous():
    code = 'print(1-2-3)'
    args = p.ParserArgs(code, 'earley', None, 'src/parsers/lang_var/var_grammar_ambiguous.lark')
    with pytest.raises(p.ParseError) as err:
        parseModule(args)
    assert 'multiple parse trees' in str(err)

def test_shiftReduceConflict():
    code = 'print(1)'
    args = p.ParserArgs(code, 'lalr', None, 'src/parsers/lang_var/var_grammar_lalr-conflict.lark')
    with pytest.raises(p.ParseError) as err:
        parseModule(args)
    assert 'Shift/Reduce conflict for terminal NEWLINE' in str(err)

def test_parseError():
    code = 'print(1-)'
    args = p.ParserArgs(code, 'lalr', None, None)
    with pytest.raises(p.ParseError) as err:
        parseModule(args)
    assert "Unexpected token Token('RPAR', ')') at line 1, column 9" in str(err)
