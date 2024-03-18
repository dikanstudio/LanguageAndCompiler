from lang_var.var_ast import *
from typing import *
from common.compilerSupport import *
import common.log as log

type ty = Literal['Int', 'Void']

def assertTy(expected: ty, given: ty, what: str):
    if expected != given:
        raise CompileError.typeError(f'{what} should have type {expected} but has type {given}')

def tycheckFuncall(id: ident, args: list[exp], vars: set[ident]) -> ty:
    match (id.name, args):
        case ('input_int', []):
            return 'Int'
        case ('print', [e]):
            t = tycheckExp(e, vars)
            assertTy('Int', t, str(e))
            return 'Void'
        case _:
            raise CompileError.typeError(f'Invalid function call of {id.name} with {len(args)} arguments')

def tycheckExp(e: exp, vars: set[ident]) -> ty:
    match e:
        case IntConst(v):
            if v < -2**63 or v > 2.**63 - 1:
                raise CompileError.typeError(f'int constant too large: {v}')
            return 'Int'
        case Call(id, args):
            return tycheckFuncall(id, args, vars)
        case UnOp(USub(), sub):
            assertTy('Int', tycheckExp(sub, vars), str(sub))
            return 'Int'
        case BinOp(left, _, right):
            assertTy('Int', tycheckExp(left, vars), str(left))
            assertTy('Int', tycheckExp(right, vars), str(right))
            return 'Int'
        case Name(name):
            if name in vars:
                return 'Int'
            else:
                raise CompileError.typeError(f'Undefined variable {name}')
    raise Exception(f'No match for expression {e}')

def tycheckStmt(s: stmt, vars: set[ident]) -> set[ident]:
    match s:
        case StmtExp(e):
            t = tycheckExp(e, vars)
            match t:
                case 'Int':
                    raise CompileError.typeError(f'Statement {s} has type int but ignores the result')
                case 'Void':
                    return set()
        case Assign(x, e):
            assertTy('Int', tycheckExp(e, vars), str(e))
            return set([x])
    raise Exception(f'No match for statement {s}')

def tycheckModule(m: mod) -> set[ident]:
    """
    Typechecks the given module, returns the set of variables used.
    These variables all have type int.
    Typechecking the var language differs only between two types: int and None.
    """
    log.info(f'Typechecking var program')
    result: set[ident] = set()
    for s in m.stmts:
        result = result.union(tycheckStmt(s, result))
    log.debug(f'Set of variables after typechecking: {result}')
    return result
