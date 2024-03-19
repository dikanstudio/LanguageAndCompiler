# AUTOMATICALLY GENERATED (2024-03-13 15:00:05)
from __future__ import annotations
from dataclasses import dataclass

type optional[T] = T | None

@dataclass(frozen=True)
class Ident:
    name: str

type ident = Ident
type string = str

@dataclass
class Add:
    pass

@dataclass
class Mul:
    pass

type binaryop = Add | Mul

@dataclass
class IntConst:
    value: int

@dataclass
class BinOp:
    left: exp
    op: binaryop
    right: exp

type exp = IntConst | BinOp