# AUTOMATICALLY GENERATED (2024-03-13 15:00:03)
from __future__ import annotations
from dataclasses import dataclass

type optional[T] = T | None

@dataclass(frozen=True)
class Ident:
    name: str

type ident = Ident
type string = str

@dataclass
class USub:
    pass

@dataclass
class Not:
    pass

type unaryop = USub | Not

@dataclass
class Add:
    pass

@dataclass
class Sub:
    pass

@dataclass
class Mul:
    pass

@dataclass
class Less:
    pass

@dataclass
class LessEq:
    pass

@dataclass
class Greater:
    pass

@dataclass
class GreaterEq:
    pass

@dataclass
class Eq:
    pass

@dataclass
class NotEq:
    pass

@dataclass
class And:
    pass

@dataclass
class Or:
    pass

type binaryop = Add | Sub | Mul | Less | LessEq | Greater | GreaterEq | Eq | NotEq | And | Or

@dataclass
class Int:
    pass

@dataclass
class Bool:
    pass

type ty = Int | Bool

@dataclass
class NotVoid:
    ty: ty

@dataclass
class Void:
    pass

type resultTy = NotVoid | Void

@dataclass
class IntConst:
    value: int
    ty: optional[resultTy] = None

@dataclass
class BoolConst:
    value: bool
    ty: optional[resultTy] = None

@dataclass
class Name:
    name: ident
    ty: optional[resultTy] = None

@dataclass
class Call:
    name: ident
    args: list[exp]
    ty: optional[resultTy] = None

@dataclass
class UnOp:
    op: unaryop
    arg: exp
    ty: optional[resultTy] = None

@dataclass
class BinOp:
    left: exp
    op: binaryop
    right: exp
    ty: optional[resultTy] = None

type exp = IntConst | BoolConst | Name | Call | UnOp | BinOp

@dataclass
class StmtExp:
    exp: exp

@dataclass
class Assign:
    var: ident
    right: exp

@dataclass
class IfStmt:
    cond: exp
    thenBody: list[stmt]
    elseBody: list[stmt]

@dataclass
class WhileStmt:
    cond: exp
    body: list[stmt]

type stmt = StmtExp | Assign | IfStmt | WhileStmt

@dataclass
class Module:
    stmts: list[stmt]

type mod = Module