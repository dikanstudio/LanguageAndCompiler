from lang_array.array_astAtom import *
import lang_array.array_ast as plainAst
from common.wasm import *
import lang_array.array_tychecker as array_tychecker
import lang_array.array_transform as array_transform
from lang_array.array_compilerSupport import *
from common.compilerSupport import *
import common.utils as utils
from pprint import pprint

def tyOfExp(exp: exp) -> ty:
    # type checker stores the type of the expression in the ty field assume that this attribute is not none when running the compiler
    match exp.ty:
        case None:
            # raise Exception if the type is None
            raise Exception(f'No type for expression {exp}')
        case Void():
            raise Exception(f'Void type for expression {exp}')
        case NotVoid(t):
            return t

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
            raise Exception(f'Invalid type {exp.ty} in array')

def forTyRetByte(ty: ty) -> int:
    match ty:
        case Int():
            return 8
        case Bool():
            return 4
        case Array(_):
            return 4

def compileExp(exp: exp, cfg: CompilerConfig) -> list[WasmInstr]:
    # debug info - analyze the expression
    # [,StmtExp(exp=Call(name=Ident(name='print'), args=[Name(name=Ident(name='x'))]))]
    # debug info
    match exp:
        # traslate IntConst to WasmInstrConst
        case IntConst(v):
            return [WasmInstrConst('i64', v)]
        # traslate Name to WasmInstrVarLocal
        case Name(name):
            return [WasmInstrVarLocal('get', WasmId("$" + name.name))]
        # translate Call to WasmInstrCall (and compile the arguments)
        case Call(name, args):
            instrs : list[WasmInstr] = []
            for arg in args:
                instrs += compileExp(arg, cfg)
            # map print to print_i64 and input_int to input_i64
            if name.name == 'print':
                if exp.ty == Void() and tyOfExp(args[0]) == Int():
                    instrs.append(WasmInstrCall(WasmId('$print_i64')))
                else:
                    instrs.append(WasmInstrCall(WasmId('$print_i32')))
            elif name.name == 'input_int':
                if exp.ty == NotVoid(Int()):
                    instrs.append(WasmInstrCall(WasmId('$input_i64')))
                else:
                    instrs.append(WasmInstrCall(WasmId('$input_i32')))
            else:
                raise Exception(f'Invalid function call of {name.name} with {len(args)} arguments')
            return instrs
        # translate UnOp to WasmInstrConst and WasmInstrNumBinOp
        case UnOp(USub(), arg):
            instrs = compileExp(arg, cfg)
            instrs.append(WasmInstrConst('i64', -1))
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
            return instrs
        # translate UnOp to WasmInstrIntRelOp
        case UnOp(Not(), arg):
            instrs = compileExp(arg, cfg)
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
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrNumBinOp('i64', 'add'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Sub()
        case BinOp(left, Sub(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrNumBinOp('i64', 'sub'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Mul()
        case BinOp(left, Mul(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Less()
        case BinOp(left, Less(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrIntRelOp('i64', 'lt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp LessEq()
        case BinOp(left, LessEq(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrIntRelOp('i64', 'le_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Greater()
        case BinOp(left, Greater(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrIntRelOp('i64', 'gt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp GreaterEq()
        case BinOp(left, GreaterEq(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            instrs.append(WasmInstrIntRelOp('i64', 'ge_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Eq()
        case BinOp(left, Eq(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            # check if 'i64' or 'i32'
            if tyOfExp(left) == Int():
                instrs.append(WasmInstrIntRelOp('i64', 'eq'))
            else:
                instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp NotEq()
        case BinOp(left, NotEq(), right):
            instrs = compileExp(left, cfg)
            instrs += compileExp(right, cfg)
            if tyOfExp(left) == Int():
                instrs.append(WasmInstrIntRelOp('i64', 'ne'))
            else:
                instrs.append(WasmInstrIntRelOp('i32', 'ne'))
            return instrs
        # translate BoolConst to WasmInstrConst
        case BoolConst(v):
            return [WasmInstrConst('i32', 1 if v else 0)]
        # translate BinOp to WasmInstrIf
        case BinOp(left, And(), right):
            instrs = compileExp(left, cfg)
            instrs.append(WasmInstrIf('i32', compileExp(right, cfg), [WasmInstrConst('i32', 0)]))
            return instrs
        # translate BinOp to WasmInstrIf using same approach like and but returning true if first true
        case BinOp(left, Or(), right):
            instrs = compileExp(left, cfg)
            instrs.append(WasmInstrIf('i32', [WasmInstrConst('i32', 1)], compileExp(right, cfg)))
            return instrs
        # translate AtomExp which is either IntConst, BoolConst or Name
        case AtomExp(a):
            match a:
                case IntConst(v):
                    return [WasmInstrConst('i64', v)]
                case BoolConst(v):
                    return [WasmInstrConst('i32', 1 if v else 0)]
                case Name(name):
                    return [WasmInstrVarLocal('get', WasmId("$" + name.name))]
        # translate ArrayInitDyn
        case ArrayInitDyn(lenExp, elemInit):
            # this leaves the array address on top of the stack
            init_array = compileInitArray(lenExp, tyInArr(exp), cfg)
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
                            compileExp(elemInit, cfg)[0],
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
            init_array = compileInitArray(IntConst(len(elemInit)), tyInArr(exp), cfg)
            # first element has offset of four and the value 
            instrs = []
            instrs.append(WasmInstrVarLocal('tee', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrVarLocal('get', WasmId('$@tmp_i32')))
            instrs.append(WasmInstrConst('i32', 4))
            instrs.append(WasmInstrNumBinOp('i32', 'add'))
            # add first element to the array
            instrs += compileExp(elemInit[0], cfg)
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
                instrs += compileExp(elemInit[i], cfg)
                instrs.append(WasmInstrMem('i64' if tyInArr(exp) == Int() else 'i32', 'store'))

            init_array += instrs
            #pprint(init_array)
            return init_array
        # translate Subscript
        case Subscript(arrExp, indexExp):
            # arrayOffsetInstrs returns instructions that leave the address of a certain element on top of stack
            instrs = arrayOffsetInstrs(arrExp, indexExp, cfg)
            # get the index
            #instrs += compileExp(indexExp, cfg)
            instrs.append(WasmInstrMem('i64' if tyInArr(exp) == Int() else 'i32', 'load'))
            return instrs
        # raise exception if no match
        case _:
            raise Exception(f'No match for expression {exp}')

def compileStmts(stmts: list[stmt], cfg: CompilerConfig) -> list[WasmInstr]:
    # create pattern matching stmt can be StmtExp | Assign
    # instruction list that will be returned

    # var=Ident(name='x'), 
    # right=BinOp(left=IntConst(value=1), op=Add(), right=IntConst(value=4))

    instrs : list[WasmInstr] = []
    for stmt in stmts:
        match stmt:
            case StmtExp(exp):
                instrs += compileExp(exp, cfg)
                pass
            case Assign(var, exp):
                instrs += compileExp(exp, cfg)
                instrs.append(WasmInstrVarLocal('set', WasmId("$" + var.name)))
                # print instrs
                #print(instrs)
            # create case for IfStmt(cond, thenBody, elseBody)
            case IfStmt(cond, thenBody, elseBody):
                instrs += compileExp(cond, cfg)
                thenB = compileStmts(thenBody, cfg)
                elseB = compileStmts(elseBody, cfg)
                instrs.append(WasmInstrIf(None, thenB, elseB))
            # create case for WhileStmt(cond, body)
            case WhileStmt(cond, body):
                # use random label
                label_exit = WasmId('$loop_exit')
                label_start = WasmId('$loop_start')

                body = compileExp(cond, cfg) + [WasmInstrIf(None, [], [WasmInstrBranch(label_exit, False)])] + compileStmts(body, cfg) + [WasmInstrBranch(label_start, False)]
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
                instrs += compileExp(rightExp, cfg)
                instrs += arrayOffsetInstrs(leftExp, indexExp, cfg)
                instrs.append(WasmInstrMem('i64' if tyInArr(leftExp) == Int() else 'i32', 'store'))

    return instrs

# returns instructions that places the memory offset for a certain array element on top of the stack
def arrayOffsetInstrs(arrayExp: atomExp, indexExp: atomExp, cfg: CompilerConfig) -> list[WasmInstr]:
    # create bounds check
    # ====================================================================================
    # THIS CODE SEGMENT CHECKS THE LENGTH

    # check in Wasm if the length is greater than the max array size
    # instrs = [WasmInstrConst('i64', 9999999999)]
    # greater : list[WasmInstr] = compileExp(indexExp, cfg)
    greater : list[WasmInstr] = []
    greater += arrayLenInstrs()
    greater.append(WasmInstrIntRelOp('i64', 'gt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    greater.append(WasmInstrIf(None, Errors.outputError(Errors.arrayIndexOutOfBounds) + [WasmInstrTrap()], []))
    #pprint(greater)
    # check in Wasm if the length is smaller than 0
    smaller = compileExp(indexExp, cfg)
    smaller.append(WasmInstrConst('i64', 0))
    smaller.append(WasmInstrIntRelOp('i64', 'lt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    smaller.append(WasmInstrIf(None, Errors.outputError(Errors.arrayIndexOutOfBounds) + [WasmInstrTrap()], []))
    #pprint(smaller)
    # append smaller to greater
    greater += smaller

    # ====================================================================================

    # get the address of the array
    instrs = compileExp(arrayExp, cfg)
    # get the index
    instrs += compileExp(indexExp, cfg)
    # wrap the index to i32
    instrs.append(WasmInstrConvOp('i32.wrap_i64'))
    # get the size of the element
    instrs.append(WasmInstrConst('i32', forTyRetByte(arrayExp.ty)))
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
def compileInitArray(lenExp: atomExp, elemTy: ty, cfg: CompilerConfig) -> list[WasmInstr]:

    # ====================================================================================
    # THIS CODE SEGMENT CHECKS THE LENGTH

    # check in Wasm if the length is greater than the max array size
    # instrs = [WasmInstrConst('i64', 9999999999)]
    greater = compileExp(lenExp, cfg)
    greater.append(WasmInstrConst('i64', int(cfg.maxArraySize / forTyRetByte(elemTy))))
    greater.append(WasmInstrIntRelOp('i64', 'gt_s'))
    # create a block with the if statement if (i32.const 0) (i32.const 14) (call $print_err) unreachable else end
    greater.append(WasmInstrIf(None, Errors.outputError(Errors.arraySize) + [WasmInstrTrap()], []))
    #pprint(greater)
    # check in Wasm if the length is smaller than 0
    smaller = compileExp(lenExp, cfg)
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
    header += compileExp(lenExp, cfg)
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
    move += compileExp(lenExp, cfg)
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
    

def compileModule(m: plainAst.mod, cfg: CompilerConfig) -> WasmModule:
    # type check the module
    vars = array_tychecker.tycheckModule(m)
    # create ctx
    ctx = array_transform.Ctx()

    atomic_stmts = array_transform.transStmts(m.stmts, ctx)

    instr = compileStmts(atomic_stmts, cfg)
    #print(instr)
    #print(vars)
    # return a wasm module that simply print(1)
    #[WasmInstrConst(ty='i64', val=4), WasmInstrVarLocal(op='set', id=WasmId(id='$x')), WasmInstrVarLocal(op='get', id=WasmId(id='$x')), WasmInstrCall(id=WasmId(id='$print'))]
    locals : list[tuple[WasmId, WasmValtype]] = []
    # add to locals the temporary variables
    locals.append((WasmId('$@tmp_i32'), 'i32'))
    # for assign in atomic_stmts get IDENT.NAME and create locals
    for assign in atomic_stmts:
        if isinstance(assign, Assign):
            # only if name starts with tmp
            if assign.var.name.startswith('tmp'):
                # if ArrayInitStatic or ArrayInitDyn
                if isinstance(assign.right, ArrayInitStatic) or isinstance(assign.right, ArrayInitDyn) or isinstance(assign.right, SubscriptAssign) or isinstance(assign.right, Subscript):
                    locals.append((WasmId('$' + assign.var.name), 'i32'))
                else:
                    locals.append((WasmId('$' + assign.var.name), 'i64'))

    # extract the locals and ma the type to the wasm type
    for var, info in vars.items():
        if info.ty == Int():
            locals.append((WasmId("$" + var.name), 'i64'))
        elif info.ty == Bool():
            locals.append((WasmId("$" + var.name), 'i32'))
        elif info.ty == Array(Int()):
            locals.append((WasmId("$" + var.name), 'i32'))
        elif info.ty == Array(Bool()):
            locals.append((WasmId("$" + var.name), 'i32'))
        elif info.ty == Array(Array(Int())):
            locals.append((WasmId("$" + var.name), 'i32'))
        elif info.ty == Array(Array(Bool())):
            locals.append((WasmId("$" + var.name), 'i32'))
        else:
            raise Exception(f'Invalid type {info.ty}')

    #print(locals)

    main = WasmFunc(id=WasmId('$main'),
                    params=[],
                    result=None,
                    locals=locals,
                    instrs=instr)
    return WasmModule(imports=wasmImports(cfg.maxMemSize),
                    exports=[WasmExport('main', WasmExportFunc(WasmId('$main')))],
                    globals=Globals.decls(),
                    data=Errors.data(),
                    funcTable=WasmFuncTable([]),
                    funcs=[main])