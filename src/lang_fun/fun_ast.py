# AUTOMATICALLY GENERATED (2024-02-28 12:34:07)
from __future__ import annotations
from dataclasses import dataclass

from lang_fun.fun_astCommon import *

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
    scope: optional[scope] = None
    ty: optional[resultTy] = None

@dataclass
class Call:
    fun: exp
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

@dataclass
class Return:
    result: optional[exp] = None

type stmt = StmtExp | Assign | IfStmt | WhileStmt | SubscriptAssign | Return

@dataclass
class FunDef:
    name: ident
    params: list[funParam]
    result: resultTy
    body: list[stmt]

type fun = FunDef

@dataclass
class Module:
    funs: list[fun]
    stmts: list[stmt]

type mod = Module