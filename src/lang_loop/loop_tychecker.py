from __future__ import annotations
from typing import *
from lang_loop.loop_ast import *
from common.compilerSupport import *
import common.log as log
import common.symtab as symtab
import pprint

type Symtab = symtab.Symtab[ident, ty]

def assertSomeTy(given: resultTy, what: str) -> ty:
    match given:
        case Void():
            raise CompileError.typeError(f'{what} should yield a value but does not')
        case NotVoid(t):
            return t

def assertTy(expected: ty, given: resultTy, what: str):
    match given:
        case Void():
            raise CompileError.typeError(f'{what} should have type {expected} but is void')
        case NotVoid(t):
            if expected != t:
                raise CompileError.typeError(f'{what} should have type {expected} but has type {t}')

def tycheckFuncall(id: ident, args: list[exp], st: Symtab) -> resultTy:
    match (id.name, args):
        case ('input_int', []):
            return NotVoid(Int())
        case ('print', [e]):
            t = tycheckExp(e, st)
            assertSomeTy(t, 'Argument to print function')
            return Void()
        case _:
            raise CompileError.typeError(f'Invalid function call of {id.name} with {len(args)} arguments')

def tycheckExp(e: exp, st: Symtab) -> resultTy:
    t = _tycheckExp(e, st)
    e.ty = t
    return t

def _tycheckExp(e: exp, st: Symtab) -> resultTy:
    match e:
        case IntConst(v):
            if v < -2**63 or v > 2.**63 - 1:
                raise CompileError.typeError(f'int constant too large: {v}')
            return NotVoid(Int())
        case BoolConst(_):
            return NotVoid(Bool())
        case Call(id, args):
            return tycheckFuncall(id, args, st)
        case UnOp(op, sub):
            subTy = tycheckExp(sub, st)
            match op:
                case USub():
                    expectedTy = Int()
                case Not():
                    expectedTy = Bool()
            assertTy(expectedTy, subTy, f'Expression {e}')
            return NotVoid(expectedTy)
        case BinOp(left, op, right):
            leftTy = tycheckExp(left, st)
            rightTy = tycheckExp(right, st)
            match op:
                case Add() | Sub() | Mul():
                    assertTy(Int(), leftTy, f'Expression {left}')
                    assertTy(Int(), rightTy, f'Expression {right}')
                    return NotVoid(Int())
                case Less() | LessEq() | Greater() | GreaterEq():
                    assertTy(Int(), leftTy, f'Expression {left}')
                    assertTy(Int(), rightTy, f'Expression {right}')
                    return NotVoid(Bool())
                case Eq() | NotEq():
                    if leftTy == rightTy:
                        return NotVoid(Bool())
                    else:
                        raise CompileError.typeError(f'Invalid types for operands of {op}')
                case And() | Or():
                    assertTy(Bool(), leftTy, f'Expression {left}')
                    assertTy(Bool(), rightTy, f'Expression {right}')
                    return NotVoid(Bool())
        case Name(x):
            return NotVoid(st.use(x))
    raise Exception(f'No match for expression {e} ({e.__module__})')

def tycheckStmt(s: stmt, st: Symtab):
    match s:
        case StmtExp(e):
            match tycheckExp(e, st):
                case Void():
                    return
                case NotVoid(t):
                    raise CompileError.typeError(f'Statement {s} has type {t} but ignores the result')
        case Assign(x, e):
            match tycheckExp(e, st):
                case Void():
                    raise CompileError.typeError(f'Left-hand side of assignment {s} is void')
                case NotVoid(t):
                    st.assign(x, t)
        case IfStmt(cond, thenBody, elseBody):
            t = tycheckExp(cond, st)
            assertTy(Bool(), t, f'Condition {cond} of if')
            nestedThen = st.copy()
            tycheckStmts(thenBody, nestedThen)
            nestedElse = st.copy()
            tycheckStmts(elseBody, nestedElse)
            st.mergeBack(nestedThen, nestedElse)
        case WhileStmt(cond, body):
            t = tycheckExp(cond, st)
            assertTy(Bool(), t, f'Condition {cond} of if')
            nested = st.copy()
            untaken = st.copy()
            tycheckStmts(body, nested)
            st.mergeBack(nested, untaken)

def tycheckStmts(stmts: list[stmt], st: Symtab):
    for s in stmts:
        tycheckStmt(s, st)

def tycheckModule(m: mod) -> Symtab:
    """
    Typechecks the given module, returns the symtab for all variables used by the module.
    """
    log.info(f'Typechecking loop program')
    st: Symtab = symtab.Symtab()
    tycheckStmts(m.stmts, st)
    log.debug(f'Symtab after typechecking: {st}')
    log.debug(f'AST after typechecking: {pprint.pformat(m)}')
    return st
