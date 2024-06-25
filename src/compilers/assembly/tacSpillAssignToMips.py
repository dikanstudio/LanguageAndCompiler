import assembly.tac_ast as tac
import assembly.tacSpill_ast as tacSpill
import assembly.mips_ast as mips
from typing import *
from assembly.common import *
import assembly.tacInterp as tacInterp
from assembly.mipsHelper import *
from common.compilerSupport import *

def mipsOp(op: tacSpill.op) -> mips.op:
    match op.name:
        case 'ADD': return mips.Add()
        case 'SUB': return mips.Sub()
        case 'MUL': return mips.Mul()
        case 'EQ': return mips.Eq()
        case 'NE': return mips.NotEq()
        case 'LT_S': return mips.Less()
        case 'GT_S': return mips.Greater()
        case 'LE_S': return mips.LessEq()
        case 'GE_S': return mips.GreaterEq()
        case _:
            raise ValueError(f'Unsupported operator: {op}')

def assignToMips(i: tacSpill.Assign) -> list[mips.instr]:
    match i:
        case tacSpill.Assign(x, tacSpill.Prim(tacSpill.Const(n))):
            return [mips.LoadI(reg(x), imm(n))]
        case tacSpill.Assign(x, tacSpill.Prim(tacSpill.Name(y))):
            return [mips.Move(reg(x), reg(y))]
        case tacSpill.Assign(x, tacSpill.BinOp(tacSpill.Const(n1), op, tacSpill.Const(n2))):
            n3 = tacInterp.evalExp(tac.BinOp(tac.Const(n1), tac.Op(op.name), tac.Const(n2)), {})
            return [mips.LoadI(reg(x), imm(n3))]
        case tacSpill.Assign(x, tacSpill.BinOp(tacSpill.Name(y1), op, tacSpill.Const(n2))):
            tmp = Regs.t2
            return [mips.LoadI(tmp, imm(n2)), mips.Op(mipsOp(op), reg(x), reg(y1), tmp)]
        case tacSpill.Assign(x, tacSpill.BinOp(tacSpill.Const(n1), op, tacSpill.Name(y2))):
            tmp = Regs.t2
            return [mips.LoadI(tmp, imm(n1)), mips.Op(mipsOp(op), reg(x), tmp, reg(y2))]
        case tacSpill.Assign(x, tacSpill.BinOp(tacSpill.Name(y1), op, tacSpill.Name(y2))):
            return [mips.Op(mipsOp(op), reg(x), reg(y1), reg(y2))]
        case tacSpill.Assign(_, _):
            raise ValueError(f'Unhandled assign case: {i}')