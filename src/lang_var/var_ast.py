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

type unaryop = USub

@dataclass
class Add:
    pass

@dataclass
class Sub:
    pass

@dataclass
class Mul:
    pass

type binaryop = Add | Sub | Mul

@dataclass
class IntConst:
    value: int

@dataclass
class Name:
    name: ident

@dataclass
class Call:
    name: ident
    args: list[exp]

@dataclass
class UnOp:
    op: unaryop
    arg: exp

@dataclass
class BinOp:
    left: exp
    op: binaryop
    right: exp

type exp = IntConst | Name | Call | UnOp | BinOp

@dataclass
class StmtExp:
    exp: exp

@dataclass
class Assign:
    var: ident
    right: exp

type stmt = StmtExp | Assign

@dataclass
class Module:
    stmts: list[stmt]

type mod = Module