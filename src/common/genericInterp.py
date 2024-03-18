import common.genericParser as parser
import common.log as log
import common.compilerSupport as compilerSupport
import common.constants as constants
from typing import *
import inspect
from dataclasses import dataclass
import traceback
import sys

@dataclass(frozen=True)
class Args:
    filename: str

def interpMain(args: Args, interpFun: Callable[[Any], None], astMod: Any):
    ast = parser.parseFile(args.filename, astMod)
    log.info(f'Interpreting AST with {interpFun} from file {inspect.getmodule(interpFun)}')
    try:
        interpFun(ast)
    except compilerSupport.CompileError as e:
        e.displayAndDie()
    except Exception:
        traceback.print_exc()
        sys.exit(constants.RUN_ERROR_EXIT_CODE)
