from lang_fun.fun_ast import *
import lang_fun.fun_astAtom as atom
from common.compilerSupport import *
import common.utils as utils

type Temporaries = list[tuple[atom.Ident, atom.exp]]

class Ctx:
    def __init__(self):
        self.freshVars: dict[ident, ty] = {}
    def newVar(self, t: ty) -> ident:
        nameId = len(self.freshVars)
        x = Ident(f'tmp_{nameId}')
        self.freshVars[x] = t
        return x

def assertResultTy(t: optional[resultTy]) -> resultTy:
    match t:
        case None:
            utils.abort(f'Type still None after type checking')
        case _:
            return t

def assertTy(t: optional[resultTy]) -> ty:
    match t:
        case None:
            utils.abort(f'Type still None after type checking')
        case Void():
            utils.abort(f'Unexpected type void')
        case NotVoid(x):
            return x

def transExpAtomic(e: exp, ctx: Ctx) -> tuple[atom.atomExp, Temporaries]:
    (res, ts) = transExp(e, True, ctx)
    match res:
        case atom.AtomExp(a):
            return (a, ts)
        case _:
            utils.abort(f'transExp with needAtom=True failed to return an atomic expression: {e}')

def atomic(needAtomic: bool, e: atom.exp, tmps: Temporaries, ctx: Ctx) -> tuple[atom.exp, Temporaries]:
    if needAtomic:
        t = assertTy(e.ty)
        tmp = ctx.newVar(t)
        return (atom.AtomExp(atom.VarName(tmp, t), NotVoid(t)), tmps + [(tmp, e)])
    else:
        return (e, tmps)

def callTarget(e: exp, ctx: Ctx) -> tuple[atom.callTarget, Temporaries]:
    match e.ty:
        case NotVoid(Fun(paramTys, resultTy)):
            pass
        case t:
            utils.abort(f'Invalid type of call target {e}: {t}')
    match e:
        case Name(x, BuiltinFun()):
            return (atom.CallTargetBuiltin(x), [])
        case Name(x, UserFun()):
            return (atom.CallTargetDirect(x), [])
        case Name(x, Var()):
            return (atom.CallTargetIndirect(x, paramTys, resultTy), [])
        case _:
            (atomTarget, tmps) = transExpAtomic(e, ctx)
            match atomTarget:
                case atom.VarName(x):
                    return (atom.CallTargetIndirect(x, paramTys, resultTy), tmps)
                case _:
                    utils.abort(f'Invalid call target after type checking: {e}')

def transExp(e: exp, needAtomic: bool, ctx: Ctx) -> tuple[atom.exp, Temporaries]:
    t = assertResultTy(e.ty)
    match e:
        case IntConst(v):
            return (atom.AtomExp(atom.IntConst(v, assertTy(t)), t), [])
        case BoolConst(v):
            return (atom.AtomExp(atom.BoolConst(v, assertTy(t)), t), [])
        case Call(target, args):
            (atomArgs, tmps) = utils.unzip([transExp(a, False, ctx) for a in args])
            (atomTarget, tmps2) = callTarget(target, ctx)
            return atomic(needAtomic, atom.Call(atomTarget, atomArgs, t),
                          utils.flatten(tmps) + tmps2, ctx)
        case UnOp(op, sub):
            (atomSub, tmps) = transExp(sub, False, ctx)
            return atomic(needAtomic, atom.UnOp(op, atomSub, t), tmps, ctx)
        case BinOp(left, op, right):
            (l, tmps1) = transExp(left, False, ctx)
            (r, tmps2) = transExp(right, False, ctx)
            return atomic(needAtomic, atom.BinOp(l, op, r, t), tmps1 + tmps2, ctx)
        case Name(x, scope):
            match scope:
                case None:
                    utils.abort(f'Scope not set on expression{e} after type checking')
                case Var():
                    name = atom.VarName(x, assertTy(t))
                case UserFun():
                    name = atom.FunName(x, assertTy(t))
                case BuiltinFun():
                    utils.abort(f'Free-standing reference to builtin function {e} found after type checking')
            return (atom.AtomExp(name, t), [])
        case ArrayInitDyn(lenExp, elemInit):
            (atomLen, tmps1) = transExpAtomic(lenExp, ctx)
            (atomElem, tmps2) = transExpAtomic(elemInit, ctx)
            return atomic(needAtomic, atom.ArrayInitDyn(atomLen, atomElem, t), tmps1 + tmps2, ctx)
        case ArrayInitStatic(initExps):
            (atomArgs, tmps) = utils.unzip([transExpAtomic(i, ctx) for i in initExps])
            return atomic(needAtomic, atom.ArrayInitStatic(atomArgs, t), utils.flatten(tmps), ctx)
        case Subscript(arrExp, indexExp):
            (atomArr, tmps1) = transExpAtomic(arrExp, ctx)
            (atomIndex, tmps2) = transExpAtomic(indexExp, ctx)
            return atomic(needAtomic, atom.Subscript(atomArr, atomIndex, t), tmps1 + tmps2, ctx)

def mkAssigns(tmps: Temporaries) -> list[atom.stmt]:
    return [atom.Assign(x, e) for (x, e) in tmps]

def transStmt(s: stmt, ctx: Ctx) -> list[atom.stmt]:
    match s:
        case StmtExp(e):
            (a, tmps) = transExp(e, False, ctx)
            return mkAssigns(tmps) + [atom.StmtExp(a)]
        case Assign(x, e):
            (a, tmps) = transExp(e, False, ctx)
            return mkAssigns(tmps) + [atom.Assign(x, a)]
        case IfStmt(cond, thenBody, elseBody):
            (a, tmps1) = transExp(cond, False, ctx)
            stmts1 = transStmts(thenBody, ctx)
            stmts2 = transStmts(elseBody, ctx)
            return mkAssigns(tmps1) + [atom.IfStmt(a, stmts1, stmts2)]
        case WhileStmt(cond, body):
            (a, tmps1) = transExp(cond, False, ctx)
            stmts = transStmts(body, ctx)
            return mkAssigns(tmps1) + [atom.WhileStmt(a, stmts)]
        case SubscriptAssign(leftExp, indexExp, rightExp):
            (l, tmps1) = transExpAtomic(leftExp, ctx)
            (i, tmps2) = transExpAtomic(indexExp, ctx)
            (r, tmps3) = transExp(rightExp, False, ctx)
            return mkAssigns(tmps1 + tmps2 + tmps3) + [atom.SubscriptAssign(l, i, r)]
        case Return(exp):
            match exp:
                case None:
                    return [atom.Return(None)]
                case _:
                    (a, tmps) = transExp(exp, False, ctx)
                    return mkAssigns(tmps) + [atom.Return(a)]

def transStmts(stmts: list[stmt], ctx: Ctx) -> list[atom.stmt]:
    result: list[atom.stmt] = []
    for s in stmts:
        result.extend(transStmt(s, ctx))
    return result

def transFun(f: FunDef, ctx: Ctx) -> atom.FunDef:
    stmts = transStmts(f.body, ctx)
    return atom.FunDef(f.name, f.params, f.result, stmts)

def transModule(m: Module, ctx: Ctx) -> atom.Module:
    """
    Translates a module from fun_ast to fun_astAtom.
    """
    funs = [transFun(f, ctx) for f in m.funs]
    stmts = transStmts(m.stmts, ctx)
    return atom.Module(funs, stmts)
