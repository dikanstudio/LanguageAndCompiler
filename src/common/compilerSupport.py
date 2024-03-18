from __future__ import annotations
from common.wasm import *
import common.constants as constants
import common.log as log
import sys
import traceback

def wasmImports(maxMemSize: int) -> list[WasmImport]: return [
    WasmImport("env", "memory", WasmImportMemory(maxMemSize, None)),
    WasmImport("env", "print", WasmImportFunc(WasmId('$print'), ['i32', 'i32'], None)),
    WasmImport("env", "print_err", WasmImportFunc(WasmId('$print_err'), ['i32', 'i32'], None)),
    WasmImport("env", "print_i32", WasmImportFunc(WasmId("$print_i32"), ['i32'], None)),
    WasmImport("env", "print_bool", WasmImportFunc(WasmId("$print_bool"), ['i32'], None)),
    WasmImport("env", "print_i64", WasmImportFunc(WasmId("$print_i64"), ['i64'], None)),
    WasmImport("env", "input_i32", WasmImportFunc(WasmId("$input_i32"), [], 'i32')),
    WasmImport("env", "input_i64", WasmImportFunc(WasmId("$input_i64"), [], 'i64'))
]

class CompileError(Exception):
    def __init__(self, prefix: str, msg: str):
        super().__init__(prefix + ': ' + msg)
    @staticmethod
    def typeError(msg: str) -> CompileError:
        return CompileError('type error', msg)
    def displayAndDie(self) -> Never:
        lines = traceback.format_exception(self)
        msg = 'Compile error: ' + str(self) + '\n' + ''.join(lines)
        log.error(msg)
        sys.exit(constants.COMPILE_ERROR_EXIT_CODE)

@dataclass(frozen=True)
class CompilerConfig:
    maxMemSize: int   # (in pages of size 64kb)
    defaultMaxMemSize = (100 * 1024) // 64  # 100MB
    maxArraySize: int # (in bytes)
    defaultMaxArraySize = 50 * 1024 * 1024 # 50MB

