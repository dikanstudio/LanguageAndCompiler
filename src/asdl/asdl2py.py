import asdl
import sys
import argparse
from dataclasses import dataclass
import datetime
import shell
from typing import *

BUILTIN_TYPES = ['ident', 'int', 'bool', 'str']

IMPORTS = """
from __future__ import annotations
from dataclasses import dataclass
"""

PRELUDE = """
type optional[T] = T | None

@dataclass(frozen=True)
class Ident:
    name: str

type ident = Ident
type string = str
"""

def abort(msg: str):
    sys.stderr.write(f'ERROR: {msg}\n')
    sys.exit(1)

@dataclass
class Record:
    name: str
    fields: list[tuple[str, str, Optional[str]]]
    def generate(self):
        fs = []
        for (name, ty, default) in self.fields:
            if default is not None:
                fs.append(f'    {name}: {ty} = {default}')
            else:
                fs.append(f'    {name}: {ty}')
        fsStr = '\n'.join(fs) if fs else '    pass'
        return f"""@dataclass
class {self.name}:
{fsStr}
"""

@dataclass
class Union:
    name: str
    alternatives: list[str]
    def __post_init__(self):
        if not self.alternatives:
            abort(f'Union {self.name} with no alternatives')
    def generate(self):
        if len(self.alternatives) == 1:
            return f'type {self.name} = {self.alternatives[0]}'
        else:
            return f'type {self.name} = {" | ".join(self.alternatives)}'

class Output:
    def __init__(self):
        self.defs = []
    def append(self, d):
        self.defs.append(d)
    def generate(self, commonModule: Optional[str]):
        l = [IMPORTS.strip()]
        if commonModule:
            l.append(f'from {commonModule} import *')
        else:
            l.append(PRELUDE.strip())
        for d in self.defs:
            l.append(d.generate().strip())
        return '\n\n'.join(l)

def generateCodeForConstructor(c: asdl.Constructor, attrs: list[asdl.Field], allTypes: set[str]) -> Record:
    fields = []
    inputFields = c.fields + attrs
    for i, f in enumerate(inputFields):
        default = None
        if f.seq:
            ty = f'list[{f.type}]'
        elif f.opt:
            ty = f'optional[{f.type}]'
            restFields = inputFields[i+1:]
            if all([f.opt for f in restFields]):
                # only have a default if all remaining fields have a default. Otherwise, you
                # get the error "Fields without default values cannot appear after fields
                # with default values"
                default = 'None'
        else:
            ty = f.type
        name = f.name if f.name else f.type
        fields.append((name, ty, default))
    return Record(c.name, fields)

asdl.Product.__match_args__ = ('fields', 'attributes')
asdl.Sum.__match_args__ = ('types', 'attributes')

def generateCode(mod: asdl.Module, out: Output):
    allTypes = set(mod.types.keys())
    for ty in mod.dfns:
        match ty.value:
            case asdl.Product(fields, _attrs):
                abort(f'Definition {ty.name} has no constructor, this is not supported')
            case asdl.Sum(constructors, attrs):
                alternatives = []
                for c in constructors:
                    d = generateCodeForConstructor(c, attrs, allTypes)
                    out.append(d)
                    alternatives.append(c.name)
                out.append(Union(ty.name, alternatives))

def parseArgs():
    parser = argparse.ArgumentParser(
                    prog='asdl2py',
                    description='Generate python code from ASDL specification',
                    epilog='Text at the bottom of help')
    parser.add_argument('inputFile')
    parser.add_argument('--out', required=False)
    parser.add_argument('--common', required=False)
    return parser.parse_args()

def writeFile(filename: str, content: str):
    header = '# AUTOMATICALLY GENERATED'
    if shell.isFile(filename):
        with open(filename, 'r') as f:
            if not f.readline().startswith(header):
                abort(f'Refusing to overwrite file {filename}')
    with open(filename, 'w') as f:
        f.write(header)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f' ({ts})\n')
        f.write(content)

def main():
    args = parseArgs()
    print(f'Parsing {args.inputFile}')
    mod = asdl.parse(args.inputFile)
    out = Output()
    generateCode(mod, out)
    s = out.generate(args.common)
    if args.out:
        writeFile(args.out, s)
    else:
        print(s)

if __name__ == '__main__':
    main()
