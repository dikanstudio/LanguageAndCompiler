import assembly.tac_ast as tac
import assembly.tacSpill_ast as tacSpill
import assembly.mips_ast as mips
from typing import *
from assembly.common import *
import assembly.tacInterp as tacInterp
from assembly.mipsHelper import *
from common.compilerSupport import *

# 'ADD', 'SUB', 'MUL', 'EQ', 'NE', 'LT_S', 'GT_S', 'LE_S', 'GE_S' is the op str
# def evalOp(op : tacSpill.Op) -> mips.Op:
#     """
#     Evaluates an operator string to a MIPS operator.
#     """
#     match op.name:
#         case 'ADD':
#             return mips.Add()
#         case 'SUB':
#             return mips.Sub()
#         case 'MUL':
#             return mips.Mul()
#         case 'EQ':
#             return mips.Eq()
#         case 'NE':
#             return mips.NotEq()
#         case 'LT_S':
#             return mips.Less()
#         case 'GT_S':
#             return mips.Greater()
#         case 'LE_S':
#             return mips.LessEq()
#         case 'GE_S':
#             return mips.GreaterEq()
#         case s:
#             raise ValueError(f'Unhandled operator: {s}')

def evalPrim(p: tacSpill.prim) -> tacSpill.prim:
    """
    Evaluates a primitive expression.
    """
    match p:
        case tacSpill.Name(_):
            return p
        case tacSpill.Const(_):
            return p

def assignToMips(i: tacSpill.Assign) -> list[mips.instr]:
    """
    Translates a TACspill assignment to MIPS instructions.
    """
    from assembly.mips_ast import Op

    match i:
        case tacSpill.Assign(x, e):
            match e:
                case tacSpill.Prim(tacSpill.Const(n)):
                    return [mips.LoadI(reg(x), mips.Imm(n))]
                case tacSpill.Prim(tacSpill.Name(y)):
                    return [mips.Move(reg(x), reg(y))]
                case tacSpill.BinOp(left, op, right):
                    # Handle binary operation assignment
                    left_mips = evalPrim(left)
                    right_mips = evalPrim(right)
                    # Determine MIPS operation based on the TACspill operation
                    match op.name:
                        case 'ADD':
                            return [Op(mips.Add(), reg(x), left_mips, right_mips)]
                        case 'SUB':
                            return [Op(mips.Sub(), reg(x), left_mips, right_mips)]
                        case 'MUL':
                            return [Op(mips.Mul(), reg(x), left_mips, right_mips)]
                        case 'EQ':
                            return [Op(mips.Eq(), reg(x), left_mips, right_mips)]
                        case 'NE':
                            return [Op(mips.NotEq(), reg(x), left_mips, right_mips)]
                        case 'LT_S':
                            return [Op(mips.Less(), reg(x), left_mips, right_mips)]
                        case 'GT_S':
                            return [Op(mips.Greater(), reg(x), left_mips, right_mips)]
                        case 'LE_S':
                            return [Op(mips.LessEq(), reg(x), left_mips, right_mips)]
                        case 'GE_S':
                            return [Op(mips.GreaterEq(), reg(x), left_mips, right_mips)]
                        case s:
                            raise ValueError(f'Unhandled operator: {s}')
                
                case _:
                    raise ValueError(f'Unhandled expression in tacSpill Assign: {e}')