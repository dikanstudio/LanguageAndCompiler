from lang_array.array_ast import *
import lang_array.array_tychecker as array_tychecker
import common.utils as utils
import common.log as log
from typing import *

@dataclass(frozen=True)
class Address:
    value: int
    def __repr__(self):
        return f'Address({self.value})'

type Env = dict[Ident, TyValue]
type TyValue = int | bool | Address
type StoreValue = list[TyValue]

class Store:
    def __init__(self):
        self.content: dict[Address, StoreValue] = {}
        self.__freshAddress = Address(0)
    def alloc(self, val: StoreValue):
        x = self.__freshAddress
        self.__freshAddress = Address(x.value + 1)
        self.content[x] = val
        return x
    def resolve(self, a: Address) -> StoreValue:
        return self.content[a]
    def storeValue(self, a: Address, i: int, v: TyValue):
        l = self.content[a]
        l[i] = v
    def __repr__(self):
        return f'Store({self.content})'

def interpFuncall(id: ident, args: list[exp], env: Env, store: Store) -> Optional[TyValue]:
    match (id.name, args):
        case ('input_int', []):
            return int(utils.inputInt('Enter some int: '))
        case ('print', [e]):
            v = asInt(interpExp(e, env, store))
            print(v)
            return None
        case ('len', [e]):
            v = asAddress(interpExp(e, env, store))
            return len(store.resolve(v))
        case _:
            raise ValueError(f'Invalid function call of {id.name} with {len(args)} arguments')

def asInt(v: Optional[TyValue]) -> int:
    assert isinstance(v, int)
    return v

def asBool(v: Optional[TyValue]) -> bool:
    assert isinstance(v, bool)
    return v

def asValue(v: Optional[TyValue]) -> TyValue:
    assert v is not None
    return v

def asAddress(v: Optional[TyValue]) -> Address:
    assert isinstance(v, Address)
    return v

def interpExp(e: exp, env: Env, store: Store) -> Optional[TyValue]:
    match e:
        case IntConst(value):
            return value
        case BoolConst(value):
            return value
        case Call(id, args):
            return interpFuncall(id, args, env, store)
        case UnOp(op, sub):
            x = interpExp(sub, env, store)
            match op:
                case USub(): return -x
                case Not(): return not x
        case BinOp(left, op, right):
            x: Any = interpExp(left, env, store)
            match op:
                case Sub(): return x - interpExp(right, env, store)
                case Add(): return x + interpExp(right, env, store)
                case Mul(): return x * interpExp(right, env, store)
                case Less(): return x < interpExp(right, env, store)
                case LessEq(): return x <= interpExp(right, env, store)
                case Greater(): return x > interpExp(right, env, store)
                case GreaterEq(): return x >= interpExp(right, env, store)
                case Eq(): return x == interpExp(right, env, store)
                case NotEq(): return x != interpExp(right, env, store)
                case Is(): return x == interpExp(right, env, store) # compare Address values by ==
                case And():
                    if x:
                        return interpExp(right, env, store)
                    else:
                        return False
                case Or():
                    if x:
                        return True
                    else:
                        return interpExp(right, env, store)
        case Name(name):
            return env[name]
        case ArrayInitDyn(lenExp, initExp):
            n = asInt(interpExp(lenExp, env, store))
            v = asValue(interpExp(initExp, env, store))
            return store.alloc(n * [v])
        case ArrayInitStatic(es):
            l = [asValue(interpExp(e, env, store)) for e in es]
            return store.alloc(l)
        case Subscript(arrayExp, indexExp):
            a = asAddress(interpExp(arrayExp, env, store))
            i = asInt(interpExp(indexExp, env, store))
            l = store.resolve(a)
            return l[i]
    raise Exception(f'No match for expression {e}')

def interpStmt(s: stmt, env: Env, store: Store, cont: list[stmt]) -> None:
    match s:
        case StmtExp(e):
            interpExp(e, env, store)
            interpStmts(cont, env, store)
        case Assign(x, e):
            v: Any = interpExp(e, env, store)
            env[x] = v
            interpStmts(cont, env, store)
        case IfStmt(cond, thenBody, elseBody):
            v = asBool(interpExp(cond, env, store))
            if v:
                interpStmts(thenBody + cont, env, store)
            else:
                interpStmts(elseBody + cont, env, store)
        case WhileStmt(cond, body):
            v = asBool(interpExp(cond, env, store))
            if v:
                interpStmts(body + [s] + cont, env, store)
            else:
                interpStmts(cont, env, store)
        case SubscriptAssign(leftExp, idxExp, rightExp):
            idx = asInt(interpExp(idxExp, env, store))
            v = interpExp(rightExp, env, store)
            a = asAddress(interpExp(leftExp, env, store))
            store.storeValue(a, idx, v)
            interpStmts(cont, env, store)

def interpStmts(stmts: list[stmt], env: Env, store: Store) -> None:
    if len(stmts) > 0:
        interpStmt(stmts[0], env, store, stmts[1:])

def interpModule(m: mod):
    utils.assertType(m, Module)
    array_tychecker.tycheckModule(m)
    env: Env = {}
    store = Store()
    interpStmts(m.stmts, env, store)
    log.debug(f'After executing program.\nEnv: {env}\nStore: {store}')
