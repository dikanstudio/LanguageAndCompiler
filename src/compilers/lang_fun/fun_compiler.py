from lang_fun.fun_astAtom import *
import lang_fun.fun_ast as plainAst
from common.wasm import *
import lang_fun.fun_tychecker as fun_tychecker
import compilers.lang_fun.fun_transform as fun_transform
from lang_array.array_compilerSupport import *
from common.compilerSupport import *
#import common.utils as utils
from pprint import pprint

def tyOfExp(exp: exp) -> ty:
    # type checker stores the type of the expression in the ty field assume that this attribute is not none when running the compiler
    match exp.ty:
        case Void():
            raise Exception(f'Void type for expression {exp}')
        case NotVoid(t):
            return t
        
def extractTy(result: resultTy) -> ty:
    match result:
        case NotVoid(t):
            return t
        case Void():
            raise Exception(f'Void type for expression {exp}')

def tyInArr(exp: exp) -> ty:
    match exp.ty:
        case NotVoid(t):
            match t:
                case Array(ty):
                    return ty
                case Int():
                    return Int()
                case Bool():
                    return Bool()
                case _:
                    raise Exception(f'Invalid type {t} in array')
        case _:
            raise Exception(f'Invalid type {exp.ty} in array')
        
def NameTy(name: VarName) -> ty:
    # type checker stores the type of the expression in the ty field assume that this attribute is not none when running the compiler
    match name.ty:
        case Int():
            return Int()
        case Bool():
            return Bool()
        case Array(ty):
            return Array(ty)
        case _:
            raise Exception(f'Invalid type {name.ty} in array')

def forTyRetByte(ty: ty) -> int:
    match ty:
        case Int():
            return 8
        case Bool():
            return 4
        case Array(_):
            return 4
        case Fun(_, _):
            return 4
        
# def checkInside with optional ty
def checkInside(ty: optional[ty]) -> ty:
    match ty:
        case None:
            raise Exception(f'No type for expression')
        case Int():
            return Int()
        case Bool():
            return Bool()
        case Array(ty):
            return ty
        case _:
            raise Exception(f'Invalid type {ty} in array')
        
# compile AtomExp to WasmInstr
def compileAtomExp(a: atomExp, cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmInstr]:
    match a:
        case IntConst(v):
            return [WasmInstrConst('i64', v)]
        case BoolConst(v):
            return [WasmInstrConst('i32', 1 if v else 0)]
        case VarName(var):
            # check ty of a if Fun use call
            # if isinstance(a.ty, Fun):
            #     identifier = a.ty.params
            #     temp : list[WasmValtype] = []
            #     for i in identifier:
            #         if i == Int():
            #             temp.append('i64')
            #         else:
            #             temp.append('i32')
            #     if a.ty.result == NotVoid(Int()):
            #         return [WasmInstrCallIndirect(temp, 'i64')]
            #     else:
            #         return [WasmInstrCallIndirect(temp, 'i32')]
            # else:
            #     return [WasmInstrVarLocal('get', WasmId("$" + var.name))]
            return [WasmInstrVarLocal('get', WasmId("$" + var.name))]
        case FunName(fun, _):
            if "tmp" in fun.name:
                return [WasmInstrVarLocal('get', WasmId("$" + fun.name))]
            else:
                indexOfFunction = 0
                for i, f in enumerate(funcsListing):
                    if f.id == "$%" + fun.name:
                        indexOfFunction = i
                        return [WasmInstrConst('i32', indexOfFunction)]

def compileExp(exp: exp, cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmInstr]:
    # debug info - analyze the expression
    # [,StmtExp(exp=Call(name=Ident(name='print'), args=[Name(name=Ident(name='x'))]))]
    # debug info
    match exp:
        # traslate IntConst to WasmInstrConst
        #case IntConst(v):
            #return [WasmInstrConst('i64', v)]
        # traslate Name to WasmInstrVarLocal
        #case Name(name):
            #return [WasmInstrVarLocal('get', WasmId("$" + name.name))]
        # translate Call to WasmInstrCall (and compile the arguments)
        case Call(fun, args):
            instrs : list[WasmInstr] = []
            for arg in args:
                instrs += compileExp(arg, cfg, funcsListing)
            # CallTargetBuiltin | CallTargetDirect | CallTargetIndirect
            match fun:
                case CallTargetBuiltin(var):
                    match var.name:
                        # map print to print_i64 and input_int to input_i64
                        case 'print':
                            if isinstance(args[0], Subscript):
                                if isinstance(args[0].array.ty, Array):
                                    match args[0].array.ty.elemTy:
                                        case Int():
                                            instrs.append(WasmInstrCall(WasmId('$print_i64')))
                                        case Bool():
                                            instrs.append(WasmInstrCall(WasmId('$print_bool')))
                                        case Array():
                                            instrs.append(WasmInstrCall(WasmId('$print_i32')))
                                        case _:
                                            pass
                            else:
                                if exp.ty == Void() and tyOfExp(args[0]) == Int():
                                    instrs.append(WasmInstrCall(WasmId('$print_i64')))
                                elif exp.ty == Void() and tyOfExp(args[0]) == Bool():
                                    instrs.append(WasmInstrCall(WasmId('$print_bool')))
                                else:
                                    pass
                        case 'input_int':
                            if exp.ty == NotVoid(Int()):
                                instrs.append(WasmInstrCall(WasmId('$input_i64')))
                            else:
                                instrs.append(WasmInstrCall(WasmId('$input_i32')))
                        case 'len':
                            instrs += arrayLenInstrs()
                        case _:
                            raise Exception(f'Invalid builtin function {var.name}')
                case CallTargetDirect(var):
                    instrs.append(WasmInstrCall(WasmId('$%' + var.name)))
                case CallTargetIndirect(name, params, result):
                    instrs.append(WasmInstrVarLocal('get', WasmId('$' + name.name)))
                    paramsTypes : list[WasmValtype] = []
                    for param in params:
                            p = 'i64' if isinstance(param, Int) else 'i32'
                            paramsTypes.append(p)
                    resultType = 'i64' if result == NotVoid(Int()) else 'i32'
                    instrs.append(WasmInstrCallIndirect(paramsTypes, resultType))
            return instrs
        # translate UnOp to WasmInstrConst and WasmInstrNumBinOp
        case UnOp(USub(), arg):
            instrs = compileExp(arg, cfg, funcsListing)
            typeTemp = tyOfExp(arg)
            match typeTemp:
                case Int():
                    instrs.append(WasmInstrConst('i64', -1))
                    instrs.append(WasmInstrNumBinOp('i64', 'mul'))
                case Bool():
                    instrs.append(WasmInstrConst('i32', -1))
                    instrs.append(WasmInstrNumBinOp('i32', 'sub'))
                case _:
                    pass
            return instrs
        # translate UnOp to WasmInstrIntRelOp
        case UnOp(Not(), arg):
            instrs = compileExp(arg, cfg, funcsListing)
            # 1 auf den Stapel legen (repräsentiert True)
            instrs.append(WasmInstrConst('i32', 1))
            # Wert auf dem Stapel mit arg vergleichen
            instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            # Wert auf dem Stapel mit 0 (False) vergleichen
            instrs.append(WasmInstrConst('i32', 0))
            instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Add()
        case BinOp(left, Add(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrNumBinOp('i64', 'add'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Sub()
        case BinOp(left, Sub(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrNumBinOp('i64', 'sub'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Mul()
        case BinOp(left, Mul(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Less()
        case BinOp(left, Less(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrIntRelOp('i64', 'lt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp LessEq()
        case BinOp(left, LessEq(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrIntRelOp('i64', 'le_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Greater()
        case BinOp(left, Greater(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrIntRelOp('i64', 'gt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp GreaterEq()
        case BinOp(left, GreaterEq(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrIntRelOp('i64', 'ge_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Eq()
        case BinOp(left, Eq(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            # check if 'i64' or 'i32'
            if tyOfExp(left) == Int():
                instrs.append(WasmInstrIntRelOp('i64', 'eq'))
            elif tyOfExp(left) == Bool():
                instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            else:
                print("Not checking Arrays, and not Checking Functions for equality")
                pass
            return instrs
        # translate BinOp to WasmInstrIntRelOp NotEq()
        case BinOp(left, NotEq(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            if tyOfExp(left) == Int():
                instrs.append(WasmInstrIntRelOp('i64', 'ne'))
            elif tyOfExp(left) == Bool():
                instrs.append(WasmInstrIntRelOp('i32', 'ne'))
            else:
                print("Not checking Arrays, and not Checking Functions for inequality")
                pass
            return instrs
        # translate BoolConst to WasmInstrConst
        #case BoolConst(v):
            #return [WasmInstrConst('i32', 1 if v else 0)]
        # translate BinOp to WasmInstrIf
        case BinOp(left, And(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs.append(WasmInstrIf('i32', compileExp(right, cfg, funcsListing), [WasmInstrConst('i32', 0)]))
            return instrs
        # translate BinOp to WasmInstrIf using same approach like and but returning true if first true
        case BinOp(left, Or(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs.append(WasmInstrIf('i32', [WasmInstrConst('i32', 1)], compileExp(right, cfg, funcsListing)))
            return instrs
        # create BinOp for Is operation for example to compare to arrays if they are the same
        case BinOp(left, Is(), right):
            instrs = compileExp(left, cfg, funcsListing)
            instrs += compileExp(right, cfg, funcsListing)
            instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            return instrs
        # translate AtomExp which is either IntConst, BoolConst or Name
        case AtomExp(a):
            match a:
                case IntConst(v):
                    return [WasmInstrConst('i64', v)]
                case BoolConst(v):
                    return [WasmInstrConst('i32', 1 if v else 0)]
                case VarName(var):
                # check ty of a if Fun use call
                # if isinstance(a.ty, Fun):
                #     identifier = a.ty.params
                #     temp : list[WasmValtype] = []
                #     for i in identifier:
                #         if i == Int():
                #             temp.append('i64')
                #         else:
                #             temp.append('i32')
                #     if a.ty.result == NotVoid(Int()):
                #         return [WasmInstrCallIndirect(temp, 'i64')]
                #     else:
                #         return [WasmInstrCallIndirect(temp, 'i32')]
                # else:
                #     return [WasmInstrVarLocal('get', WasmId("$" + var.name))]
                    return [WasmInstrVarLocal('get', WasmId("$" + var.name))]
                case FunName(fun, _):
                    if "tmp" in fun.name:
                        return [WasmInstrVarLocal('get', WasmId("$" + fun.name))]
                    else:
                        indexOfFunction = 0
                        for i, f in enumerate(funcsListing):
                            if f.id == "$%" + fun.name:
                                indexOfFunction = i
                                return [WasmInstrConst('i32', indexOfFunction)]
        # translate ArrayInitDyn
        case ArrayInitDyn(lenExp, elemInit):
            # this leaves the array address on top of the stack
            init_array = compileInitArray(lenExp, tyInArr(exp), cfg, funcsListing)
            # first element has offset of four and the value 
            instrs = []
            instrs.append(WasmInstrVarLocal('tee', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrVarLocal('get', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrConst('i32', 4))
            instrs.append(WasmInstrNumBinOp('i32', 'add'))
            # set tmp_i32 to the address of the first element
            instrs.append(WasmInstrVarLocal('set', WasmId('$@tmp_i32')))
            # create a block with the loop where block $loop_exit and loop $loop_start
            instrs.append(WasmInstrBlock(
                label=WasmId('$loop_exit'),
                result=None,
                body=[
                    WasmInstrLoop(
                        label=WasmId('$loop_start'),
                        body=[
                            WasmInstrVarLocal('get', WasmId('$@tmp_i32')),
                            WasmInstrVarGlobal('get', WasmId('$@free_ptr')),
                            WasmInstrIntRelOp('i32', 'lt_u'),
                            WasmInstrIf(None, [], [WasmInstrBranch(WasmId('$loop_exit'), False)]),
                            WasmInstrVarLocal('get', WasmId('$@tmp_i32')),
                            compileAtomExp(elemInit, cfg, funcsListing)[0],
                            WasmInstrMem('i64' if tyInArr(exp) == Int() else 'i32', 'store'),
                            WasmInstrVarLocal('get', WasmId('$@tmp_i32')),
                            # size of the element
                            WasmInstrConst('i32', forTyRetByte(tyInArr(exp))),
                            WasmInstrNumBinOp('i32', 'add'),
                            WasmInstrVarLocal('set', WasmId('$@tmp_i32')),
                            WasmInstrBranch(WasmId('$loop_start'), False)
                        ]
                    )
                ]
            ))
            init_array += instrs
            pprint(init_array)
            return init_array
                    
        case ArrayInitStatic(elemInit):
            # this leaves the array address on top of the stack
            init_array = compileInitArray(IntConst(len(elemInit), Int()), tyInArr(exp), cfg, funcsListing)
            # first element has offset of four and the value 
            instrs = []
            instrs.append(WasmInstrVarLocal('tee', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrVarLocal('get', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrConst('i32', 4))
            instrs.append(WasmInstrNumBinOp('i32', 'add'))
            # add first element to the array
            instrs += compileAtomExp(elemInit[0], cfg, funcsListing)
            instrs.append(WasmInstrMem('i64' if tyInArr(exp) == Int() else 'i32', 'store'))
            # if type int sotre i64 else i32
            init = 4
            offset_counter = 8 if tyInArr(exp) == Int() else 4
            # loop through the rest of the elements
            for i in range(1, len(elemInit)):
                instrs.append(WasmInstrVarLocal('tee', WasmId('$@tmp_i32')))
                instrs.append(WasmInstrVarLocal('get', WasmId('$@tmp_i32')))
                instrs.append(WasmInstrConst('i32', init + offset_counter * i))
                instrs.append(WasmInstrNumBinOp('i32', 'add'))
                instrs += compileAtomExp(elemInit[i], cfg, funcsListing)
                instrs.append(WasmInstrMem('i64' if tyInArr(exp) == Int() else 'i32', 'store'))

            init_array += instrs
            #pprint(init_array)
            return init_array
        # translate Subscript
        case Subscript(arrExp, indexExp):
            # arrayOffsetInstrs returns instructions that leave the address of a certain element on top of stack
            instrs = arrayOffsetInstrs(arrExp, indexExp, cfg, funcsListing)
            # get the index
            #instrs += compileExp(indexExp, cfg)
            instrs.append(WasmInstrMem('i64' if tyOfExp(exp) == Int() else 'i32', 'load'))
            return instrs
        # raise exception if no match
        case _:
            raise Exception(f'No match for expression {exp}')

def compileStmts(stmts: list[stmt], cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmInstr]:
    # create pattern matching stmt can be StmtExp | Assign
    # instruction list that will be returned

    # var=Ident(name='x'), 
    # right=BinOp(left=IntConst(value=1), op=Add(), right=IntConst(value=4))

    instrs : list[WasmInstr] = []
    for stmt in stmts:
        match stmt:
            case StmtExp(exp):
                instrs += compileExp(exp, cfg, funcsListing)
                pass
            case Assign(var, exp):
                instrs += compileExp(exp, cfg, funcsListing)
                instrs.append(WasmInstrVarLocal('set', WasmId("$" + var.name)))
                # print instrs
                #print(instrs)
            # create case for IfStmt(cond, thenBody, elseBody)
            case IfStmt(cond, thenBody, elseBody):
                instrs += compileExp(cond, cfg, funcsListing)
                thenB = compileStmts(thenBody, cfg, funcsListing)
                elseB = compileStmts(elseBody, cfg, funcsListing)
                instrs.append(WasmInstrIf(None, thenB, elseB))
            # create case for WhileStmt(cond, body)
            case WhileStmt(cond, body):
                # use random label
                label_exit = WasmId('$loop_exit')
                label_start = WasmId('$loop_start')

                body = compileExp(cond, cfg, funcsListing) + [WasmInstrIf(None, [], [WasmInstrBranch(label_exit, False)])] + compileStmts(body, cfg, funcsListing) + [WasmInstrBranch(label_start, False)]
                # create a WasmInstrBlock with the label
                instrs.append(
                    WasmInstrBlock(
                        label=label_exit,
                        result=None,
                        body=[WasmInstrLoop(
                            label=label_start,
                            body=body
                        )]
                    )
                )
            # create case for SubscriptAssign(leftExp, indexExp, rightExp)
            case SubscriptAssign(leftExp, indexExp, rightExp):
                # put instructions for the right-hand side, followed by a i64.store or i32.store after these instructions
                instrs += arrayOffsetInstrs(leftExp, indexExp, cfg, funcsListing)
                instrs += compileExp(rightExp, cfg, funcsListing)
                instrs.append(WasmInstrMem('i64' if tyOfExp(rightExp) == Int() else 'i32', 'store'))
            case Return(exp):
                if exp is not None:
                    # get ty of the expression
                    myty = tyOfExp(exp)
                    myty = 'i64' if myty == Int() else 'i32'
                    instrs.append(WasmInstrBlock(WasmId("$fun_exit"), myty, compileExp(exp, cfg, funcsListing) + [WasmInstrBranch(WasmId("$fun_exit"), False), WasmInstrConst('i64', 0)]))

    return instrs

# returns instructions that places the memory offset for a certain array element on top of the stack
def arrayOffsetInstrs(arrayExp: atomExp, indexExp: atomExp, cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmInstr]:
    # create bounds check
    # ====================================================================================
    # THIS CODE SEGMENT CHECKS THE LENGTH

    # check in Wasm if the length is greater than the max array size
    # instrs = [WasmInstrConst('i64', 9999999999)]
    # greater : list[WasmInstr] = compileExp(indexExp, cfg)
    greater : list[WasmInstr] = []
    greater += compileAtomExp(indexExp, cfg, funcsListing)
    # add 1 to the index to check if the index is greater than the length
    greater.append(WasmInstrConst('i64', 1))
    # perform addition of the index and 1
    greater.append(WasmInstrNumBinOp('i64', 'add'))
    greater += compileAtomExp(arrayExp, cfg, funcsListing)
    greater += arrayLenInstrs()
    greater.append(WasmInstrIntRelOp('i64', 'gt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    greater.append(WasmInstrIf(None, Errors.outputError(Errors.arrayIndexOutOfBounds) + [WasmInstrTrap()], []))
    #pprint(greater)
    # check in Wasm if the length is smaller than 0
    smaller = compileAtomExp(indexExp, cfg, funcsListing)
    smaller.append(WasmInstrConst('i64', 0))
    smaller.append(WasmInstrIntRelOp('i64', 'lt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    smaller.append(WasmInstrIf(None, Errors.outputError(Errors.arrayIndexOutOfBounds) + [WasmInstrTrap()], []))
    #pprint(smaller)
    # append smaller to greater
    greater += smaller

    # ====================================================================================

    # get the address of the array
    instrs = compileAtomExp(arrayExp, cfg, funcsListing)
    # get the index
    instrs += compileAtomExp(indexExp, cfg, funcsListing)
    # wrap the index to i32
    instrs.append(WasmInstrConvOp('i32.wrap_i64'))
    # get the size of the element
    # retrieve the inner element type of the array
    myty = arrayExp.ty
    inside = checkInside(myty)
    instrs.append(WasmInstrConst('i32', forTyRetByte(inside)))
    # multiply the index with the size of the element
    instrs.append(WasmInstrNumBinOp('i32', 'mul'))
    # add the offset of the first element
    instrs.append(WasmInstrConst('i32', 4))
    instrs.append(WasmInstrNumBinOp('i32', 'add'))
    # add the address of the array
    instrs.append(WasmInstrNumBinOp('i32', 'add'))

    greater += instrs

    return greater


# generates code that expects the array address on top of stack and puts the length on top of stack
# searches the 28 bits of the length in the memory
def arrayLenInstrs() -> list[WasmInstr]:
    instrs : list[WasmInstr] = [
        WasmInstrMem('i32', 'load'),
        WasmInstrConst('i32', 4),
        WasmInstrNumBinOp('i32', 'shr_u'),
        WasmInstrConvOp('i64.extend_i32_u')
    ]
    return instrs

# generates code to initialize an array without initializing the elements
# n * [0] :: the n is the lenExp
def compileInitArray(lenExp: atomExp, elemTy: ty, cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmInstr]:

    # ====================================================================================
    # THIS CODE SEGMENT CHECKS THE LENGTH

    # check in Wasm if the length is greater than the max array size
    # instrs = [WasmInstrConst('i64', 9999999999)]
    greater = compileAtomExp(lenExp, cfg, funcsListing)
    greater.append(WasmInstrConst('i64', int(cfg.maxArraySize / forTyRetByte(elemTy))))
    greater.append(WasmInstrIntRelOp('i64', 'gt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    greater.append(WasmInstrIf(None, Errors.outputError(Errors.arraySize) + [WasmInstrTrap()], []))
    #pprint(greater)
    # check in Wasm if the length is smaller than 0
    smaller = compileAtomExp(lenExp, cfg, funcsListing)
    smaller.append(WasmInstrConst('i64', 0))
    smaller.append(WasmInstrIntRelOp('i64', 'lt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    smaller.append(WasmInstrIf(None, Errors.outputError(Errors.arraySize) + [WasmInstrTrap()], []))
    #pprint(smaller)
    # append smaller to greater
    greater += smaller

    # ====================================================================================
    # THIS CODE CREATES THE HEADER

    header = [WasmInstrVarGlobal('get', WasmId('$@free_ptr'))]
    header += compileAtomExp(lenExp, cfg, funcsListing)
    header.append(WasmInstrConvOp('i32.wrap_i64'))
    header.append(WasmInstrConst('i32', 4))
    header.append(WasmInstrNumBinOp('i32', 'shl'))
    header.append(WasmInstrConst('i32', 1))
    header.append(WasmInstrNumBinOp('i32', 'xor'))
    header.append(WasmInstrMem('i32', 'store'))
    #pprint(header)

    # append header to greater
    greater += header

    # ====================================================================================
    # THIS CODE MOVES FREE_PTR AND RETURNS THE ARRAY ADDRESS

    move = [WasmInstrVarGlobal('get', WasmId('$@free_ptr'))]
    move += compileAtomExp(lenExp, cfg, funcsListing)
    move.append(WasmInstrConvOp('i32.wrap_i64'))
    if forTyRetByte(elemTy) == 8:
        move.append(WasmInstrConst('i32', 8))
    else:
        move.append(WasmInstrConst('i32', 4))
    move.append(WasmInstrNumBinOp('i32', 'mul'))
    move.append(WasmInstrConst('i32', 4))
    move.append(WasmInstrNumBinOp('i32', 'add'))
    move.append(WasmInstrVarGlobal('get', WasmId('$@free_ptr')))
    move.append(WasmInstrNumBinOp('i32', 'add'))
    move.append(WasmInstrVarGlobal('set', WasmId('$@free_ptr')))

    #pprint(move)

    # append move to greater
    greater += move
    return greater
    
# create function that searches the stmt recursively for "tmp.." vars and creates locals for them
def createLocals(stmts: list[stmt]) -> list[tuple[WasmId, WasmValtype]]:
    locals : list[tuple[WasmId, WasmValtype]] = []
    for stmt in stmts:
        match stmt:
            case Assign(var, right):
                if var.name.startswith('tmp'):
                    # if ArrayInitStatic or ArrayInitDyn or SubscriptAssign or Subscript
                    if isinstance(stmt.right, ArrayInitStatic) or isinstance(stmt.right, ArrayInitDyn) or isinstance(stmt.right, SubscriptAssign) or isinstance(stmt.right, Subscript):
                        locals.append((WasmId('$' + var.name), 'i32'))
                    else:
                        locals.append((WasmId('$' + var.name), 'i64'))
                else:
                    # check right is Int or anything else
                    if isinstance(right, AtomExp):
                        if isinstance(right.e, IntConst):
                            locals.append((WasmId('$' + var.name), 'i64'))
                        elif isinstance(right.e, BoolConst):
                            locals.append((WasmId('$' + var.name), 'i32'))
                        elif isinstance(right.e, VarName):
                            # check ty of VarName
                            if right.e.ty == Int():
                                locals.append((WasmId('$' + var.name), 'i64'))
                            else:
                                locals.append((WasmId('$' + var.name), 'i32'))
                        else:
                            raise Exception(f'Invalid type {stmt.right}')
                    elif isinstance(right, Call):
                        locals.append((WasmId('$' + var.name), 'i64'))
                    elif isinstance(right, FunName):
                        locals.append((WasmId('$' + var.name), 'i64'))
                    elif isinstance(right, Ident):
                        locals.append((WasmId('$' + var.name), 'i64'))
            case IfStmt(_, thenBody, elseBody):
                locals += createLocals(thenBody)
                locals += createLocals(elseBody)
            case WhileStmt(_, body):
                for stmt in body:
                    if isinstance(stmt, Assign):
                        if stmt.var.name.startswith('tmp'):
                            locals.append((WasmId('$' + stmt.var.name), 'i64'))
                    else:
                        pass

            case StmtExp(exp):
                print("StmtExp not implemented in createLocals")
                pass
            case SubscriptAssign(_, _, _):
                raise Exception("Not implemented SubscriptAssign")
            case Return(exp):
                if exp is not None:
                    locals += createLocals([StmtExp(exp)])
    return locals

def tyOfResultTy(ty: resultTy) -> optional[ty]:
    match ty:
        case Void():
            return None
        case NotVoid(t):
            return t

# compile functions
def compileFun(fun: list[fun], cfg: CompilerConfig, funcsListing: list[WasmId]) -> list[WasmFunc]:
    # create a list of functions
    funcs : list[WasmFunc] = []
    for f in fun:
        # create a list of locals
        locals : list[tuple[WasmId, WasmValtype]] = []
        # add to locals the temporary variables
        #locals.append((WasmId('$@tmp_i32'), 'i32'))
        # for assign in atomic_stmts get IDENT.NAME and create locals
        locals += createLocals(f.body)
        # create a list of instructions
        instr = compileStmts(f.body, cfg, funcsListing)
        # get params in WasmFunc --> params = list[tuple[WasmId, WasmValtype]]
        params: list[funParam] = []
        for p in f.params:
            # check that t is not None
            t = checkInside(p.ty)
            params.append(FunParam(p.var, t))
        
        mappedParams : list[tuple[WasmId, WasmValtype]] = []
        for p in params:
            mappedParams.append((WasmId('$' + p.var.name), 'i64' if p.ty == Int() else 'i32'))
                
        # result is either Notvoid(t) or Void()
        result = tyOfResultTy(f.result)
        # map result to Optional[WasmValtype]
        result = 'i64' if result == Int() else 'i32'
        # create a function
        funcs.append(WasmFunc(id=WasmId('$%' + f.name.name),
                              params=mappedParams,
                              result=result,
                              locals=locals,
                              instrs=instr))
    return funcs

def compileModule(m: plainAst.mod, cfg: CompilerConfig) -> WasmModule:
    # type check the module
    vars = fun_tychecker.tycheckModule(m)
    # create list of functions
    funcsListing : list[WasmId] = [WasmId('$%' + f.name) for f in vars.funLocals.keys()]

    # create ctx
    ctx = fun_transform.Ctx()

    atomic_module = fun_transform.transModule(m, ctx)

    atomic_stmts = atomic_module.stmts
    atomic_funs = atomic_module.funs

    instr = compileStmts(atomic_stmts, cfg, funcsListing)
    funcs = compileFun(atomic_funs, cfg, funcsListing)
    #print(instr)
    #print(vars)
    # return a wasm module that simply print(1)
    #[WasmInstrConst(ty='i64', val=4), WasmInstrVarLocal(op='set', id=WasmId(id='$x')), WasmInstrVarLocal(op='get', id=WasmId(id='$x')), WasmInstrCall(id=WasmId(id='$print'))]

    # extract the locals and map the type to the wasm type from vars
    locals: list[tuple[WasmId, WasmValtype]] = []
    for name, type in ctx.freshVars.items():
        if isinstance(type, Int):
            locals.append((WasmId('$' + name.name), 'i64'))
        else:
            locals.append((WasmId('$' + name.name), 'i32'))
    # funlocals is a dict {Ident(name='x'): [], Ident(name='y'): []}
    # locVars = vars.funLocals.values()
    # for listoflocals in locVars:
    #     for elem in listoflocals:
    #         if elem.ty == Int():
    #             locals.append((WasmId('$' + elem.name.name), 'i64'))
    #         else:
    #             locals.append((WasmId('$' + elem.name.name), 'i32'))
    for localvar in vars.toplevelLocals:
        locals.append((WasmId('$' + localvar.name.name), 'i64' if localvar.ty == Int() else 'i32'))

    #locals += createLocals(atomic_stmts)
    # add local variable "@tmp_i32" to locals
    locals.append((WasmId('$@tmp_i32'), 'i32'))
    # check for each func in funcs if the locals are in the locals list
    # for f in funcs:
    #     for local in f.locals:
    #         if local not in locals:
    #             locals.append(local)

    wasmIds : list[WasmId] = []

    # from funcs --> WasmFunc(id=...) extract the id
    for f in funcs:
        wasmIds.append(f.id)

    main = WasmFunc(id=WasmId('$main'),
                    params=[],
                    result=None,
                    locals=locals,
                    instrs=instr)
    return WasmModule(imports=wasmImports(cfg.maxMemSize),
                    exports=[WasmExport('main', WasmExportFunc(WasmId('$main')))],
                    globals=Globals.decls(),
                    data=Errors.data(),
                    funcTable=WasmFuncTable([WasmId('$print'), WasmId('$print_err'), WasmId('$print_bool'), WasmId('$print_i64'), WasmId('$print_i32'), WasmId('$input_i64'), WasmId('$input_i32')] + wasmIds),
                    funcs=[main] + funcs)