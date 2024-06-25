from lang_fun.fun_ast import *
import lang_fun.fun_astAtom as atom
from common.compilerSupport import *
import common.utils as utils

type Temporaries = list[tuple[atom.Ident, atom.exp]]

class Ctx:
    """
    Context for getting fresh variable names.
    """
    def __init__(self):
        self.freshVars: dict[ident, ty] = {}
    def newVar(self, t: ty) -> ident:
        """
        Get a fresh variabler of the given type.
        """
        nameId = len(self.freshVars)
        x = Ident(f'tmp_{nameId}')
        self.freshVars[x] = t
        return x

def transExpAtomic(e: exp, ctx: Ctx) -> tuple[atom.atomExp, Temporaries]:
    """
    Translates e to an atomic expression. Essentially a shortcut for transExp(e, True, ctx).
    """
    (res, ts) = transExp(e, True, ctx)
    match res:
        case atom.AtomExp(a):
            return (a, ts)
        case _:
            utils.abort(f'transExp with needAtom=True failed to return an atomic expression: {e}')

def assertExpNotVoid(e: exp | atom.exp) -> ty:
    """
    Asserts that e is an expression of a non-void type.
    """
    match e.ty:
        case None:
            raise ValueError(f'type still None after type-checking. Expression: {e}')
        case Void():
            raise ValueError(f'type of {e} is Void after type-checking.')
        case NotVoid(t):
            return t

def atomic(needAtomic: bool, e: atom.exp, tmps: Temporaries, ctx: Ctx) -> tuple[atom.exp, Temporaries]:
    """
    Converts e to an atomic expression if needAtomic is True.
    """
    if needAtomic:
        t = assertExpNotVoid(e)
        tmp = ctx.newVar(t)
        return (atom.AtomExp(atom.VarName(tmp, t), e.ty), tmps + [(tmp, e)])
    else:
        return (e, tmps)
    
def ensure_result_ty(t: optional[resultTy]) -> resultTy:
    """
    Ensures that t is not None, providing a default resultTy if it is.
    """
    if t is None:
        return Void()
    return t

def ensure_Scope(t: optional[scope]) -> scope:
    """
    Ensures that t is not None, providing a default Scope if it is.
    """
    if t is None:
        raise ValueError('Scope is None')
    return t

def transExp(e: exp, needAtomic: bool, ctx: Ctx) -> tuple[atom.exp, Temporaries]:
    """
    Translates expression e (of type array_ast.exp) to an expression of type
    array_astAtom.exp, together with a list of temporary variables used by
    the translated expression.

    If the flag needAtomic is True, then the translated expression is an atomic expression,
    that is something of the form array_astAtom.AtomExp(...).
    """
    t = e.ty
    match e:
        case IntConst(v):
            # check that t is not None
            t = ensure_result_ty(t)
            return (atom.AtomExp(atom.IntConst(v, Int()), t), [])
        case BoolConst(v):
            # check that t is not None
            t = ensure_result_ty(t)
            return (atom.AtomExp(atom.BoolConst(v, Bool()), t), [])
        case Name(x):
            xt = assertExpNotVoid(e)
            # check that t is not None
            t = ensure_result_ty(t)
            return (atom.AtomExp(atom.VarName(x, xt), t), [])
        case Call(fun, args):
            (atomFun, funTmps) = transExpAtomic(fun, ctx)
            (atomArgs, argsTmps) = utils.unzip([transExp(a, True, ctx) for a in args])
            # check that t is not None
            t = ensure_result_ty(t)
            # Determine the correct call target
            callTarget = None
            match atomFun:
                case atom.VarName(var, ty):
                    if var == Ident('print'):
                        callTarget = atom.CallTargetBuiltin(var)
                    elif var == Ident('len'):
                        callTarget = atom.CallTargetBuiltin(var)
                    elif var.name.startswith('tmp_'):
                        callTarget = atom.CallTargetIndirect(var, [a.ty for a in args], t)
                    else:
                        callTarget = atom.CallTargetDirect(var)
                case _:
                    raise ValueError(f"Unsupported function expression: {atomFun}")

            # Create the Call expression
            callExp = atom.Call(callTarget, atomArgs, t)
            return atomic(needAtomic, callExp, funTmps + utils.flatten(argsTmps), ctx)
            #tempScope = ensure_Scope(fun.scope)
            # match atomFun:
            #     case atom.VarName(var, _):
            #         if var == Ident('print'):
            #             return atomic(needAtomic, atom.Call(atom.CallTargetBuiltin(var), atomArgs, t), funTmps + utils.flatten(argsTmps), ctx)
            #         elif var == Ident('len'):
            #             return atomic(needAtomic, atom.Call(atom.CallTargetBuiltin(var), atomArgs, t), funTmps + utils.flatten(argsTmps), ctx)
            #         elif var.name.startswith('tmp_'):
            #             # CallTargetIndirect
            #             return atomic(needAtomic, atom.Call(atom.CallTargetIndirect(var, [a.ty for a in args], t), atomArgs, t), funTmps + utils.flatten(argsTmps), ctx)
            #     case atom.FunName(var, _):
            #         raise Exception('Function name not implemented')
            #     case atom.IntConst(_, _):
            #         raise Exception('IntConst not implemented')
            #     case atom.BoolConst(_, _):
            #         raise Exception('BoolConst not implemented')
        case UnOp(op, arg):
            (atomArg, tmps) = transExp(arg, False, ctx)
            # check that t is not None
            t = ensure_result_ty(t)
            return atomic(needAtomic, atom.UnOp(op, atomArg, t), tmps, ctx)
        case BinOp(left, op, right):
            (l, tmps1) = transExp(left, False, ctx)
            (r, tmps2) = transExp(right, False, ctx)
            # check that t is not None
            t = ensure_result_ty(t)
            return atomic(needAtomic, atom.BinOp(l, op, r, t), tmps1 + tmps2, ctx)
        case ArrayInitDyn(lenExp, elemInit):
            (atomLen, tmps1) = transExpAtomic(lenExp, ctx)
            (atomElem, tmps2) = transExpAtomic(elemInit, ctx)
            # check that t is not None
            t = ensure_result_ty(t)
            return atomic(needAtomic, atom.ArrayInitDyn(atomLen, atomElem, t), tmps1 + tmps2, ctx)
        case ArrayInitStatic(initExps):
            (atomArgs, tmps) = utils.unzip([transExpAtomic(i, ctx) for i in initExps])
            # check that t is not None
            t = ensure_result_ty(t)
            return atomic(needAtomic, atom.ArrayInitStatic(atomArgs, t), utils.flatten(tmps), ctx)
        case Subscript(arrExp, indexExp):
            (atomArr, tmps1) = transExpAtomic(arrExp, ctx)
            (atomIndex, tmps2) = transExpAtomic(indexExp, ctx)
            # check that t is not None
            t = ensure_result_ty(t)
            return atomic(needAtomic, atom.Subscript(atomArr, atomIndex, t), tmps1 + tmps2, ctx)

def mkAssigns(tmps: Temporaries) -> list[atom.stmt]:
    """
    Turns a list of temporary variables into a list of statements.
    """
    return [atom.Assign(x, e) for (x, e) in tmps]

def transStmt(s: stmt, ctx: Ctx) -> list[atom.stmt]:
    """
    Translates statement s (of type array_ast.stmt) to a statement of type
    array_astAtom.stmt.
    """
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
        case Return(e):
            # e could be none or optional[exp]
            if e is None:
                return [atom.Return(None)]
            else:
                (a, tmps) = transExp(e, False, ctx)
                return mkAssigns(tmps) + [atom.Return(a)]

def transStmts(stmts: list[stmt], ctx: Ctx) -> list[atom.stmt]:
    """
    Main entry point, transforming a list of statements.
    This function is called from compilers.array_compiler.compileModule.
    """
    result: list[atom.stmt] = []
    for s in stmts:
        result.extend(transStmt(s, ctx))
    return result

def transFun(f: FunDef, ctx: Ctx) -> atom.FunDef:
    """
    Translates a function definition from fun_ast to fun_astAtom.
    """
    stmts = transStmts(f.body, ctx)
    return atom.FunDef(f.name, f.params, f.result, stmts)

def transModule(m: Module, ctx: Ctx) -> atom.Module:
    """
    Translates a module from fun_ast to fun_astAtom.
    """
    funs = [transFun(f, ctx) for f in m.funs]
    stmts = transStmts(m.stmts, ctx)
    return atom.Module(funs, stmts)
