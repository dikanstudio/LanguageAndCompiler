from lark import ParseTree
from parsers.lang_simple.simple_ast import *
from parsers.common import *
import common.log as log
# import mod
from lang_var.var_ast import *

grammarFile = "./src/parsers/lang_simple/simple_grammar.lark"
grammarFile2 = "./src/parsers/lang_var/var_grammar.lark"

def parse(args: ParserArgs) -> exp:
    parseTree = parseAsTree(args, grammarFile, 'exp')
    ast = parseTreeToExpAst(parseTree)
    log.debug(f'AST: {ast}')
    return ast

def parseTreeToExpAst(t: ParseTree) -> exp:
    match t.data:
        # case 'int_exp' to return IntConst
        case 'int_exp':
            return IntConst(int(asToken(t.children[0])))
        # case 'add_exp' to return BinOp with Add
        case 'add_exp':
            e1, e2 = [asTree(c) for c in t.children]
            return BinOp(parseTreeToExpAst(e1), Add(), parseTreeToExpAst(e2))
        # case 'sub_exp' to return BinOp with Sub
        case 'sub_exp':
            e1, e2 = [asTree(c) for c in t.children]
            return BinOp(parseTreeToExpAst(e1), Sub(), parseTreeToExpAst(e2))
        # case 'mul_exp' to return BinOp with Mul
        case 'mul_exp':
            e1, e2 = [asTree(c) for c in t.children]
            return BinOp(parseTreeToExpAst(e1), Mul(), parseTreeToExpAst(e2)) 
        case 'usub_exp':
            e = asTree(t.children[0])
            return UnOp(USub(), parseTreeToExpAst(e))
        case 'var_exp':
            return Name(Ident(asToken(t.children[0])))
        case 'func_exp':
            # decide if it's print or input_int
            func = asToken(t.children[0])
            if func == 'print':
                # create a call to print
                # check if argument is a ")" return empty
                if len(t.children) == 3:
                    return Call(Ident('print'), [])
                else:
                    return Call(Ident('print'), [parseTreeToExpAst(asTree(t.children[2]))])
            elif func == 'input_int':
                # create a call to input_int
                return Call(Ident('input_int'), [])
            else:
                raise Exception(f'unhandled function {func}')
        case 'paren_exp':
            return parseTreeToExpAst(asTree(t.children[1]))
        case 'line_exp':
            return parseTreeToExpAst(asTree(t.children[0])) 
        case 'exp' | 'exp_1' | 'exp_2':
            return parseTreeToExpAst(asTree(t.children[0]))
        case 'inner_exp':
            return parseTreeToExpAst(asTree(t.children[0]))
        case kind:
            raise Exception(f'unhandled parse tree of kind {kind} for exp: {t}')
        
def parseTreeToStmtAst(t: ParseTree) -> stmt:
    match t.data:
        # match two possible cases
        # like in the var file
        case 'exp_stmt':
            return StmtExp(parseTreeToExpAst(asTree(t.children[0])))
        case 'assign_stmt':
            # extract the variable and the expression
            try:
                var, exp = [c for c in t.children]
            except:
                # parse tree again
                var, exp = [c for c in asTree(t.children[0]).children]
            return Assign(Ident(asToken(var)), parseTreeToExpAst(asTree(exp)))
        case kind:
            raise Exception(f'unhandled parse tree of kind {kind} for stmt: {t}')
        
def parseTreeToStmtListAst(t: ParseTree) -> list[stmt]:
    return [parseTreeToStmtAst(asTree(c)) for c in t.children]

def parseTreeToModuleAst(t: ParseTree) -> mod:
    return Module(parseTreeToStmtListAst(asTree(t.children[0])))
        
def parseModule(args: ParserArgs) -> mod:
    parseTree = parseAsTree(args, grammarFile2, 'lvar')
    print("AHHHHHH")
    print(parseTree.pretty())
    ast = parseTreeToModuleAst(parseTree)
    log.debug(f'AST: {ast}')
    return ast
