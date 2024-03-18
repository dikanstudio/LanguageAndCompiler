# AUTOMATICALLY GENERATED (2024-03-01 17:42:38)
from __future__ import annotations
from dataclasses import dataclass

from lang_array.array_astCommon import *

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
    var: ident
    ty: optional[resultTy] = None

@dataclass
class Call:
    var: ident
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

@dataclass
class ArrayInitDyn:
    len: exp
    elemInit: exp
    ty: optional[resultTy] = None

@dataclass
class ArrayInitStatic:
    elemInit: list[exp]
    ty: optional[resultTy] = None

@dataclass
class Subscript:
    array: exp
    index: exp
    ty: optional[resultTy] = None

type exp = IntConst | BoolConst | Name | Call | UnOp | BinOp | ArrayInitDyn | ArrayInitStatic | Subscript

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

@dataclass
class SubscriptAssign:
    left: exp
    index: exp
    right: exp

type stmt = StmtExp | Assign | IfStmt | WhileStmt | SubscriptAssign

@dataclass
class Module:
    stmts: list[stmt]

type mod = Module