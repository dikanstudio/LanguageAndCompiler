from __future__ import annotations
from lang_fun.fun_ast import *
from typing import *
from common.compilerSupport import *
import common.log as log
import common.symtab as symtab
import common.utils as utils
import pprint

type Symtab = symtab.Symtab[ident, ty]

def isBaseTy(given: Optional[ty]):
    return given in [Int(), Bool()]

def isArrayTy(given: Optional[ty]):
    match given:
        case Array(_): return True
        case _: return False

def assertSomeTy(given: Optional[ty], what: str) -> ty:
    if given is None:
        raise CompileError.typeError(f'{what} should yield a value but does not')
    else:
        return given

def assertTy(expected: ty, given: Optional[ty], what: str):
    if expected != given:
        raise CompileError.typeError(f'{what} should have type {expected} but has type {given}')

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

builtinFunNames = ['input_int', 'print', 'len']

def tycheckBuiltinFuncall(target: exp, args: list[exp], st: Symtab) -> optional[ty]:
    """
    Return the *function* type for a call of a builtin function. Our type language cannot
    express the types of all builtin functions in general because print and len are overloaded.
    Hence, we have to type check to arguments to get the function type.
    """
    match (target, args):
        case (Name(Ident('input_int')), []):
            return Fun([], NotVoid(Int()))
        case (Name(Ident('print')), [e]):
            t = tycheckExpNotVoid(e, st)
            if t not in [Int(), Bool()]:
                raise CompileError.typeError(f'{e} should have type int or bool but has type {t}')
            return Fun([t], Void())
        case (Name(Ident('len')), [e]):
            t = tycheckExpNotVoid(e, st)
            assertArrayTy(t, str(e))
            return Fun([t], NotVoid(Int()))
        case _:
            return None

def tycheckUserDefinedFuncall(tfun: ty|None, args: list[exp], st: Symtab) -> resultTy:
    match tfun:
        case Fun(params, result):
            if len(params) != len(args):
                raise CompileError.typeError(f'Function expects {len(params)} '\
                    f'arguments, but called with {len(args)}')
            for i, (e, expectedTy) in enumerate(zip(args, params)):
                ty = tycheckExpNotVoid(e, st)
                if ty != expectedTy:
                    raise CompileError.typeError(f'Function expects type '\
                        f'{expectedTy} as argument {i+1}, but given type {ty}')
            return result
        case _:
            raise CompileError.typeError(f'Not a function: {tfun}')

def tycheckFuncall(target: exp, args: list[exp], st: Symtab) -> resultTy:
    match tycheckBuiltinFuncall(target, args, st):
        case None:
            funTy = tycheckExpNotVoid(target, st)
            return tycheckUserDefinedFuncall(funTy, args, st)
        case Fun() as funTy:
            target.ty = NotVoid(funTy)
            match target:
                case Name(_):
                    target.scope = BuiltinFun()
                case _:
                    pass
            return funTy.result
        case t:
            utils.abort(f'Invalid type returned by tycheckBuiltinFuncall: {t}')


def tycheckExp(e: exp, st: Symtab) -> resultTy:
    t = _tycheckExp(e, st)
    e.ty = t
    match e:
        case Name(x):
            match st.scope(x):
                case 'var':
                    scope = Var()
                case 'fun':
                    scope = UserFun()
            e.scope = scope
        case _:
            pass
    return t

def _tycheckExp(e: exp, st: Symtab) -> resultTy:
    match e:
        case IntConst(v):
            if v < -2**63 or v > 2.**63 - 1:
                raise CompileError.typeError(f'int constant too large: {v}')
            return NotVoid(Int())
        case BoolConst(_):
            return NotVoid(Bool())
        case Call(e, args):
            return tycheckFuncall(e, args, st)
        case UnOp(op, sub):
            subTy = tycheckExpNotVoid(sub, st)
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
            if not st.hasVar(x) and x.name in builtinFunNames:
                raise CompileError.typeError(f'Invalid use of builtin function {x}')
            t = st.use(x)
            return NotVoid(t)
        case ArrayInitDyn(lenExp, initExp):
            lenTy = tycheckExpNotVoid(lenExp, st)
            assertTy(Int(), lenTy, f'Length expression {lenExp} in array initialization')
            elemTy = assertSomeTy(tycheckExpNotVoid(initExp, st),
                                  f'Element expression {initExp} in array initialization')
            return NotVoid(Array(elemTy))
        case ArrayInitStatic([]):
            raise CompileError.typeError(f'Cannot construct empty array')
        case ArrayInitStatic(es):
            elemTys: list[ty | None]= [tycheckExpNotVoid(e, st) for e in es]
            elemTy = assertSomeTy(elemTys[0],
                                  f'Element expression {es[0]} in array initialization')
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

@dataclass
class ReturnType:
    ty: resultTy
    kind: Literal['maybe', 'definite']
    def maybe(self) -> ReturnType:
        return ReturnType(self.ty, 'maybe')
    def merge(self, other: ReturnType):
        if self.ty != other.ty:
            raise CompileError.typeError(f'Conflicting return types')
        elif self.kind == 'definite' and other.kind == 'definite':
            return ReturnType(self.ty, 'definite')
        else:
            return ReturnType(self.ty, 'maybe')

def tycheckStmt(s: stmt, st: Symtab) -> ReturnType | None:
    """
    tycheckStmt returns the result type if the statement is a return statement.
    """
    match s:
        case StmtExp(e):
            t = tycheckExp(e, st)
            match t:
                case Void():
                    return None
                case NotVoid():
                    raise CompileError.typeError(
                                f'Statement {s} has type {t} but ignores the result')
        case Assign(x, e):
            match tycheckExp(e, st):
                case Void():
                    raise CompileError.typeError(f'Left-hand side of assignment {s} is void')
                case NotVoid(t):
                    st.assign(x, t)
                    return None
        case IfStmt(cond, thenBody, elseBody):
            t = tycheckExpNotVoid(cond, st)
            assertTy(Bool(), t, f'Condition {cond} of if')
            nestedThen = st.copy()
            ty1 = tycheckStmts(thenBody, nestedThen)
            nestedElse = st.copy()
            ty2 = tycheckStmts(elseBody, nestedElse)
            st.mergeBack(nestedThen, nestedElse)
            if ty1 is not None and ty2 is not None:
                return ty1.merge(ty2)
            elif ty1 is None and ty2 is None:
                return None
            elif ty1 is not None and ty2 is None:
                return ty1.maybe()
            elif ty2 is not None and ty1 is None:
                return ty2.maybe()
        case WhileStmt(cond, body):
            t = tycheckExpNotVoid(cond, st)
            assertTy(Bool(), t, f'Condition {cond} of if')
            nested = st.copy()
            ty = tycheckStmts(body, nested)
            untaken = st.copy()
            st.mergeBack(untaken, nested)
            if ty is None:
                return None
            else:
                return ty.maybe()
        case SubscriptAssign(leftExp, indexExp, rightExp):
            leftTy = tycheckExpNotVoid(leftExp, st)
            match leftTy:
                case Array(elemTy):
                    indexTy = tycheckExpNotVoid(indexExp, st)
                    assertTy(Int(), indexTy, f'Index {indexExp} of assignmet')
                    rightTy = tycheckExpNotVoid(rightExp, st)
                    assertTy(elemTy, rightTy, f'Right-hand side {rightExp} of subscript assigment')
                    return None
                case _:
                    raise CompileError.typeError(f'Left-hand side of subscript assignment must ' \
                        'be an array')
        case Return(e):
            match e:
                case None:
                    return ReturnType(Void(), 'definite')
                case _:
                    ty = tycheckExpNotVoid(e, st)
                    return ReturnType(NotVoid(ty), 'definite')

def tycheckStmts(stmts: list[stmt], st: Symtab) -> ReturnType | None:
    res: list[ReturnType] = []
    for s in stmts:
        ty = tycheckStmt(s, st)
        if ty is not None:
            res.append(ty)
    if not res:
        return None
    ty = res[0].ty
    for r in res:
        if r.ty != ty:
            raise CompileError.typeError(f'Inconsistent return types: {r.ty} and {ty}')
    for r in res:
        if r.kind == 'definite':
            return r
    return res[0]

def tycheckFunDef(f: FunDef, st: Symtab):
    if f.name.name in builtinFunNames:
        raise CompileError.typeError(f'Cannot redefine builtin function {f.name.name}')
    for p in f.params:
        st.assign(p.var, p.ty)
    res = tycheckStmts(f.body, st)
    match res:
        case None:
            if f.result != Void():
                raise CompileError.typeError(
                        f'Function {f.name} should return {f.result} but returns nothing')
        case ReturnType(ty, k):
            if ty != f.result:
                raise CompileError.typeError(
                        f'Function {f.name} should return {f.result} but returns {ty}')
            elif k == 'maybe' and f.result != Void():
                raise CompileError.typeError(
                    f'Function {f.name} does not always return a value of type {f.result}')

@dataclass(frozen=True)
class LocalVar:
    name: ident
    ty: ty

@dataclass(frozen=True)
class TycheckResult:
    funLocals: dict[ident, list[LocalVar]]
    toplevelLocals: list[LocalVar]

def localsFromSymtab(st: Symtab, params: list[funParam]) -> list[LocalVar]:
    paramNames = [p.var for p in params]
    return [LocalVar(x, t) for x, t in st.types('var') if x not in paramNames]

def tycheckModule(m: mod) -> TycheckResult:
    """
    Typechecks the given module, returns the symtab for all variables used by the module.
    """
    log.info(f'Typechecking fun program')
    st: Symtab = symtab.Symtab()
    for f in m.funs:
        ty = Fun([p.ty for p in f.params], f.result)
        st.assign(f.name, ty, 'fun')
    funLocalsDict: dict[ident, list[LocalVar]] = {}
    for f in m.funs:
        funSt = st.copy()
        tycheckFunDef(f, funSt)
        funLocalsDict[f.name] = localsFromSymtab(funSt, f.params)
    t = tycheckStmts(m.stmts, st)
    if t is not None:
        raise CompileError.typeError(f'Return is only allowed inside a function')
    log.debug(f'Symtab after typechecking: {st}')
    log.debug(f'AST after typechecking: {pprint.pformat(m)}')
    return TycheckResult(funLocalsDict, localsFromSymtab(st, []))
