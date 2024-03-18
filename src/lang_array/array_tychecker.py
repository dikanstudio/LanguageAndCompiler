from __future__ import annotations
from lang_array.array_ast import *
from typing import *
from common.compilerSupport import *
import common.log as log
import common.symtab as symtab
import pprint

type Symtab = symtab.Symtab[ident, ty]

def isBaseTy(given: Optional[ty]):
    return given in [Int(), Bool()]

def isArrayTy(given: Optional[ty]):
    match given:
        case Array(_): return True
        case _: return False

def assertSomeTy(given: resultTy, what: str) -> ty:
    match given:
        case Void():
            raise CompileError.typeError(f'{what} should yield a value but does not')
        case NotVoid(t):
            return t

def assertTy(expected: ty, given: resultTy | ty, what: str):
    match given:
        case Void():
            raise CompileError.typeError(f'{what} should have type {expected} but is void')
        case NotVoid(t):
            if expected != t:
                raise CompileError.typeError(f'{what} should have type {expected} but has type {t}')
        case t:
            if expected != t:
                raise CompileError.typeError(f'{what} should have type {expected} but has type {t}')

def assertArrayTy(given: Optional[ty], what: str):
    if not isArrayTy(given):
        raise CompileError.typeError(f'{what} should have an array type but has type {given}')

def assertNotVoid(given: resultTy, what: str) -> ty:
    match given:
        case Void():
            raise CompileError.typeError(f'{what} must not be void')
        case NotVoid(t):
            return t

def tycheckExpNotVoid(e: exp, st: Symtab) -> ty:
    t = tycheckExp(e, st)
    return assertNotVoid(t, str(e))

def tycheckFuncall(id: ident, args: list[exp], st: Symtab) -> resultTy:
    match (id.name, args):
        case ('input_int', []):
            return NotVoid(Int())
        case ('print', [e]):
            t = tycheckExpNotVoid(e, st)
            if t not in [Int(), Bool()]:
                raise CompileError.typeError(f'{e} should have type int or bool but has type {t}')
            return Void()
        case ('len', [e]):
            t = tycheckExpNotVoid(e, st)
            assertArrayTy(t, str(e))
            return NotVoid(Int())
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
            leftTy = tycheckExpNotVoid(left, st)
            rightTy = tycheckExpNotVoid(right, st)
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
                    if leftTy == rightTy and isBaseTy(leftTy):
                        return NotVoid(Bool())
                    else:
                        raise CompileError.typeError(f'Invalid types for operands of {op}')
                case Is():
                    if leftTy == rightTy and isArrayTy(leftTy):
                        return NotVoid(Bool())
                    else:
                        raise CompileError.typeError(f'Invalid types for operands of {op}')
                case And() | Or():
                    assertTy(Bool(), leftTy, f'Expression {left}')
                    assertTy(Bool(), rightTy, f'Expression {right}')
                    return NotVoid(Bool())
        case Name(x):
            return NotVoid(st.use(x))
        case ArrayInitDyn(lenExp, initExp):
            lenTy = tycheckExp(lenExp, st)
            assertTy(Int(), lenTy, f'Length expression {lenExp} in array initialization')
            elemTy = assertSomeTy(tycheckExp(initExp, st),
                                  f'Element expression {initExp} in array initialization')
            return NotVoid(Array(elemTy))
        case ArrayInitStatic([]):
            raise CompileError.typeError(f'Cannot construct empty array')
        case ArrayInitStatic(es):
            elemTys: list[ty]= [tycheckExpNotVoid(e, st) for e in es]
            elemTy = elemTys[0]
            for t in elemTys[1:]:
                if t != elemTy:
                    raise CompileError.typeError(f'All array elements must have the same type: {es}')
            return NotVoid(Array(elemTy))
        case Subscript(arrayExp, indexExp):
            arrayTy = tycheckExpNotVoid(arrayExp, st)
            indexTy = tycheckExpNotVoid(indexExp, st)
            assertTy(Int(), indexTy, f'Index of subscript expression')
            match arrayTy:
                case Array(elemTy):
                    return NotVoid(elemTy)
                case _:
                    raise CompileError.typeError(f'Left-hand side {arrayExp} of subscript must be an array')
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
            tycheckStmts(body, nested)
            untaken = st.copy()
            st.mergeBack(untaken, nested)
        case SubscriptAssign(leftExp, indexExp, rightExp):
            leftTy = tycheckExp(leftExp, st)
            match leftTy:
                case NotVoid(Array(elemTy)):
                    indexTy = tycheckExp(indexExp, st)
                    assertTy(Int(), indexTy, f'Index {indexExp} of assignmet')
                    rightTy = tycheckExp(rightExp, st)
                    assertTy(elemTy, rightTy, f'Right-hand side {rightExp} of subscript assigment')
                    return elemTy
                case _:
                    raise CompileError.typeError(f'Left-hand side of subscript assignment must ' \
                        'be an array')

def tycheckStmts(stmts: list[stmt], st: Symtab):
    for s in stmts:
        tycheckStmt(s, st)

def tycheckModule(m: mod) -> Symtab:
    """
    Typechecks the given module, returns the symtab for all variables used by the module.
    """
    log.info(f'Typechecking array program')
    st: Symtab = symtab.Symtab()
    tycheckStmts(m.stmts, st)
    log.debug(f'Symtab after typechecking: {st}')
    log.debug(f'AST after typechecking: {pprint.pformat(m)}')
    return st
