from lang_loop.loop_ast import *
from common.wasm import *
import lang_loop.loop_tychecker as loop_tychecker
from common.compilerSupport import *
#import common.utils as utils

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



def compileExp(exp: exp) -> list[WasmInstr]:
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
                instrs += compileExp(arg)
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
            instrs = compileExp(arg)
            instrs.append(WasmInstrConst('i64', -1))
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
            return instrs
        # translate UnOp to WasmInstrIntRelOp
        case UnOp(Not(), arg):
            instrs = compileExp(arg)
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
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrNumBinOp('i64', 'add'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Sub()
        case BinOp(left, Sub(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrNumBinOp('i64', 'sub'))
            return instrs
        # translate BinOp to WasmInstrNumBinOp Mul()
        case BinOp(left, Mul(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Less()
        case BinOp(left, Less(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrIntRelOp('i64', 'lt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp LessEq()
        case BinOp(left, LessEq(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrIntRelOp('i64', 'le_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Greater()
        case BinOp(left, Greater(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrIntRelOp('i64', 'gt_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp GreaterEq()
        case BinOp(left, GreaterEq(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            instrs.append(WasmInstrIntRelOp('i64', 'ge_s'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp Eq()
        case BinOp(left, Eq(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
            # check if 'i64' or 'i32'
            if tyOfExp(left) == Int():
                instrs.append(WasmInstrIntRelOp('i64', 'eq'))
            else:
                instrs.append(WasmInstrIntRelOp('i32', 'eq'))
            return instrs
        # translate BinOp to WasmInstrIntRelOp NotEq()
        case BinOp(left, NotEq(), right):
            instrs = compileExp(left)
            instrs += compileExp(right)
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
            instrs = compileExp(left)
            instrs.append(WasmInstrIf('i32', compileExp(right), [WasmInstrConst('i32', 0)]))
            return instrs
        # translate BinOp to WasmInstrIf using same approach like and but returning true if first true
        case BinOp(left, Or(), right):
            instrs = compileExp(left)
            instrs.append(WasmInstrIf('i32', [WasmInstrConst('i32', 1)], compileExp(right)))
            return instrs
        # raise exception if no match
        case _:
            raise Exception(f'No match for expression {exp}')

def compileStmts(stmts: list[stmt]) -> list[WasmInstr]:
    # create pattern matching stmt can be StmtExp | Assign
    # instruction list that will be returned

    # var=Ident(name='x'), 
    # right=BinOp(left=IntConst(value=1), op=Add(), right=IntConst(value=4))

    instrs : list[WasmInstr] = []
    for stmt in stmts:
        match stmt:
            case StmtExp(exp):
                instrs += compileExp(exp)
                pass
            case Assign(var, exp):
                instrs += compileExp(exp)
                instrs.append(WasmInstrVarLocal('set', WasmId("$" + var.name)))
                # print instrs
                #print(instrs)
            # create case for IfStmt(cond, thenBody, elseBody)
            case IfStmt(cond, thenBody, elseBody):
                instrs += compileExp(cond)
                thenB = compileStmts(thenBody)
                elseB = compileStmts(elseBody)
                instrs.append(WasmInstrIf(None, thenB, elseB))
            # create case for WhileStmt(cond, body)
            case WhileStmt(cond, body):
                # use random label
                label_exit = WasmId('$loop_exit')
                label_start = WasmId('$loop_start')

                body = compileExp(cond) + [WasmInstrIf(None, [], [WasmInstrBranch(label_exit, False)])] + compileStmts(body) + [WasmInstrBranch(label_start, False)]
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

                
            

    return instrs

def compileModule(m: mod, cfg: CompilerConfig) -> WasmModule:
    # type check the module
    vars = loop_tychecker.tycheckModule(m)
    # vorher {Ident(name='z'), Ident(name='x'), Ident(name='y')}
    # jetzt Symtab({Ident(name='n'): VarInfo(ty=Int(), definitelyAssigned=True, scope='var')})
    #items = vars.items()
    #rint(m.stmts)
    instr = compileStmts(m.stmts)
    print(instr)
    #print(vars)
    # return a wasm module that simply print(1)
    #[WasmInstrConst(ty='i64', val=4), WasmInstrVarLocal(op='set', id=WasmId(id='$x')), WasmInstrVarLocal(op='get', id=WasmId(id='$x')), WasmInstrCall(id=WasmId(id='$print'))]
    locals : list[tuple[WasmId, WasmValtype]] = []
    # extract the locals and ma the type to the wasm type
    for var, info in vars.items():
        if info.ty == Int():
            locals.append((WasmId("$" + var.name), 'i64'))
        elif info.ty == Bool():
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
                    globals=[],
                    data=[],
                    funcTable=WasmFuncTable([]),
                    funcs=[main])