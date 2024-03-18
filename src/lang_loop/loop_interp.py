from lang_loop.loop_ast import *
import lang_loop.loop_tychecker as loop_tychecker
import common.utils as utils
from typing import *

type Environ = dict[Ident, TyValue]
type TyValue = int | bool

def interpFuncall(id: ident, args: list[exp], env: Environ) -> Optional[TyValue]:
    match (id.name, args):
        case ('input_int', []):
            return int(utils.inputInt('Enter some int: '))
        case ('print', [e]):
            v = interpExp(e, env)
            print(v)
            return None
        case _:
            raise ValueError(f'Invalid function call of {id.name} with {len(args)} arguments')

def interpExp(e: exp, env: Environ) -> Optional[TyValue]:
    match e:
        case IntConst(value):
            return value
        case BoolConst(value):
            return value
        case Call(id, args):
            return interpFuncall(id, args, env)
        case UnOp(op, sub):
            x = interpExp(sub, env)
            match op:
                case USub(): return -x
                case Not(): return not x
        case BinOp(left, op, right):
            x: Any = interpExp(left, env)
            match op:
                case Sub(): return x - interpExp(right, env)
                case Add(): return x + interpExp(right, env)
                case Mul(): return x * interpExp(right, env)
                case Less(): return x < interpExp(right, env)
                case LessEq(): return x <= interpExp(right, env)
                case Greater(): return x > interpExp(right, env)
                case GreaterEq(): return x >= interpExp(right, env)
                case Eq(): return x == interpExp(right, env)
                case NotEq(): return x != interpExp(right, env)
                case And():
                    if x:
                        return interpExp(right, env)
                    else:
                        return False
                case Or():
                    if x:
                        return True
                    else:
                        return interpExp(right, env)
        case Name(name):
            return env[name]
    raise Exception(f'No match for expression {e}')

def interpStmt(s: stmt, env: Environ, cont: list[stmt]) -> None:
    match s:
        case StmtExp(e):
            interpExp(e, env)
            interpStmts(cont, env)
        case Assign(x, e):
            v: Any = interpExp(e, env)
            env[x] = v
            interpStmts(cont, env)
        case IfStmt(cond, thenBody, elseBody):
            v: Any = interpExp(cond, env)
            if v:
                interpStmts(thenBody + cont, env)
            else:
                interpStmts(elseBody + cont, env)
        case WhileStmt(cond, body):
            v: Any = interpExp(cond, env)
            if v:
                interpStmts(body + [s] + cont, env)
            else:
                interpStmts(cont, env)

def interpStmts(stmts: list[stmt], env: Environ) -> None:
    if len(stmts) > 0:
        interpStmt(stmts[0], env, stmts[1:])

def interpModule(m: mod):
    utils.assertType(m, Module)
    loop_tychecker.tycheckModule(m)
    interpStmts(m.stmts, {})
