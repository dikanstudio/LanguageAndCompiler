from lang_var.var_ast import *
from common.wasm import *
import lang_var.var_tychecker as var_tychecker
from common.compilerSupport import *
#import common.utils as utils

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
                instrs.append(WasmInstrCall(WasmId('$print_i64')))
            elif name.name == 'input_int':
                instrs.append(WasmInstrCall(WasmId('$input_i64')))
            else:
                raise Exception(f'Invalid function call of {name.name} with {len(args)} arguments')
            return instrs
        # translate UnOp to WasmInstrConst and WasmInstrNumBinOp
        case UnOp(USub(), arg):
            instrs = compileExp(arg)
            instrs.append(WasmInstrConst('i64', -1))
            instrs.append(WasmInstrNumBinOp('i64', 'mul'))
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
    return instrs

def compileModule(m: mod, cfg: CompilerConfig) -> WasmModule:
    # type check the module
    vars = var_tychecker.tycheckModule(m)
    print(vars)
    print(m.stmts)
    instr = compileStmts(m.stmts)
    print(instr)
    #print(vars)
    # return a wasm module that simply print(1)
    # instr : list[WasmInstr] = [
    #    WasmInstrConst('i64', 1),
    #    WasmInstrCall(WasmId('$print_i64'))
    #]
    # [WasmInstrConst(ty='i64', val=4), WasmInstrVarLocal(op='set', id=WasmId(id='$x')), WasmInstrVarLocal(op='get', id=WasmId(id='$x')), WasmInstrCall(id=WasmId(id='$print'))]
    locals : list[tuple[WasmId, WasmValtype]] = []
    # extract locals from the instructions as list[tuple[WasmId, WasmValtype]]
    for i in instr:
        if isinstance(i, WasmInstrVarLocal):
            # check if the WasmInstrVarLocal is a set operation
            if i.op == 'set' and (i.id, 'i64') not in locals:
                # add the local to the list
                locals.append((i.id, 'i64'))

    print(locals)

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

