from lang_var.var_ast import *
import lang_var.var_tychecker as var_tychecker
import common.utils as utils
from typing import *

type Env = dict[Ident, TyValue]
type TyValue = int

def interpFuncall(id: ident, args: list[exp], env: Env) -> TyValue | None:
    match (id.name, args):
        case ('input_int', []):
            return int(utils.inputInt('Enter some int: '))
        case ('print', [e]):
            v = interpExp(e, env)
            print(v)
            return None
        case _:
            raise ValueError(f'Invalid function call of {id.name} with {len(args)} arguments')

def interpExp(e: exp, env: Env) -> TyValue | None:
    match e:
        case IntConst(value):
            return value
        case Call(id, args):
            return interpFuncall(id, args, env)
        case UnOp(USub(), sub):
            x: Any = interpExp(sub, env)
            return -x
        case BinOp(left, op, right):
            x: Any = interpExp(left, env)
            y: Any = interpExp(right, env)
            match op:
                case Sub(): return x - y
                case Add(): return x + y
                case Mul(): return x * y
        case Name(name):
            return env[name]
    raise Exception(f'No match for expression {e}')

def interpStmt(s: stmt, env: Env) -> None:
    match s:
        case StmtExp(e):
            interpExp(e, env)
        case Assign(x, e):
            v: Any = interpExp(e, env)
            env[x] = v

def interpStmts(stmts: list[stmt], env: Env) -> None:
    for stmt in stmts:
        interpStmt(stmt, env)

def interpModule(m: mod):
    utils.assertType(m, Module)
    var_tychecker.tycheckModule(m)
    interpStmts(m.stmts, {})
