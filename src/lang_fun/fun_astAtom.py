# AUTOMATICALLY GENERATED (2024-02-28 14:03:04)
from __future__ import annotations
from dataclasses import dataclass

from lang_fun.fun_astCommon import *

@dataclass
class IntConst:
    value: int
    ty: ty

@dataclass
class BoolConst:
    value: bool
    ty: ty

@dataclass
class VarName:
    var: ident
    ty: ty

@dataclass
class FunName:
    fun: ident
    ty: ty

type atomExp = IntConst | BoolConst | VarName | FunName

@dataclass
class CallTargetBuiltin:
    var: ident

@dataclass
class CallTargetDirect:
    var: ident

@dataclass
class CallTargetIndirect:
    var: ident
    params: list[ty]
    result: resultTy

type callTarget = CallTargetBuiltin | CallTargetDirect | CallTargetIndirect

@dataclass
class AtomExp:
    e: atomExp
    ty: resultTy

@dataclass
class Call:
    fun: callTarget
    args: list[exp]
    ty: resultTy

@dataclass
class UnOp:
    op: unaryop
    arg: exp
    ty: resultTy

@dataclass
class BinOp:
    left: exp
    op: binaryop
    right: exp
    ty: resultTy

@dataclass
class ArrayInitDyn:
    len: atomExp
    elemInit: atomExp
    ty: resultTy

@dataclass
class ArrayInitStatic:
    elemInit: list[atomExp]
    ty: resultTy

@dataclass
class Subscript:
    array: atomExp
    index: atomExp
    ty: resultTy

type exp = AtomExp | Call | UnOp | BinOp | ArrayInitDyn | ArrayInitStatic | Subscript

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
    left: atomExp
    index: atomExp
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