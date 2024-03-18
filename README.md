# Introduction

This repository implements a compiler from a statically typed subset of Python to Wasm.
It proceeds in several steps, adding more language features in every step. The approach
is heavily inspired by Jeremy Siek's book *Essentials of compilation*.

Currently, the following steps havee been realized as different input languages:

* Language `var`: variables and arithmetic expressions
* Language `loop`: conditionals and while loops
* Language `arrays`: dynamically-size, heap-allocated arrays (support for GC is missing)
* Language `fun`: top-level functions and C-style function points (no compiler yet)

The dynamic semantics of all these languages is that of python: if a source
program passes our type checker, it yields the same result as running the program
through python.

The implementation language of the interpreters and compilers is Python, with static
type checking handled by [pyright's](https://github.com/microsoft/pyright/tree/main)
strict mode.

Installation instructions can be found at the end of this document.

**NOTE: do not pass to students, this repository contains all solutions!**

# Commands

You start the interpreter and the compiler through the `./run` script or via
`python src/main.py`. Here are the three most common ways of invocation:

* `./run interp FILE.py` runs the input file `FILE.py` throught the interpreter.
* `./run compile FILE.py` compiles input file `FILE.py`, the compilation result will
be placed in textual form in `out.wat`.
* `./run run FILE.py` compiles the input file and runs the resulting wasm code with iwasm.

Use the `--help` option to see all available options.

# Development

## Architecture

Each language `L` has its AST, type checker, and interpreter in  `src/lang_L`. The compiler
is in `src/compilers/lang_L`. The AST of each language is specified in
[ASDL](https://www.cs.princeton.edu/~appel/papers/asdl97.pdf), running `make` generates
python code from these specifications.

Parsing for each language is handled by Python's
[ast](https://docs.python.org/3/library/ast.html) module. In
[src/common/genericParser.py](src/common/genericParser.py), the Python
AST is translated into the AST defined by the ASDL specification.

Between the implementations of the different languages, there is quite a lot of code
duplication. This is on purpose to keep the structure of the code as simply as possible.
(Jeremy Siek uses an open recursion pattern based on
inheritance to avoid this kind of code duplication. But this approach makes
the code somewhat hard to read, so I did not use it.)

## Static Typing

All python code in this repository is statically type checked with
[pyright's](https://github.com/microsoft/pyright/tree/main)
strict mode. If you use Visual Studio Code as an IDE, you should at the
following configuration option:

```
"python.analysis.typeCheckingMode": "strict"
```

You can run the type checker manually with the `./tycheck` command.

## Tests

The `test_files` directory contains many tests for the different languages. We
use [pytest](https://docs.pytest.org/en/8.0.x/) for executing the tests.

The `./run-tests` command runs all tests. Here is how to run only a subset of the tests:

```
./run-tests FILES_OR_DIRECTORIES -k TEST_NAME_PATTERN
```

Adding new tests is simple:

* Save the code for the test in a `TEST.py` file and place it in one of the subdirectories
  of `test_file`.
* If the test expected input on stdin, write the desired input in the corresponding `TEST.in`
  file and place the `.in` file next to the `.py` file.
* If the test is expected to trigger a type error, the first line of `TEST.py` should be
  `### type error`.
* If the test is expected to trigger a runtime error, the first line of `TEST.py` should be
  `### run error`.
* You do not need to specify the expected output of the test. We run the test file
  through Python for this purpose.

# Installation

Requirements:

* Python version 3.12
* iwasm virtual from the [wasm-micro-runtime](https://github.com/bytecodealliance/wasm-micro-runtime) package,
  a virtual machine for Wasm.
* [wabt](https://github.com/webassembly/wabt), which contains the `wat2wasm` tool for converting
  the textual representation of Wasm to binary form.
* GNU make
* cmake, to build the native extension functions for wasm-micro-runtime.
* Optional, for visualizing graph trees: graphviz
* Supported platforms: Mac OSX and Linux. Windows should work as well, but I did not test. I recommand using docker if you are running Windows.

You can either install the requirements on your local system (alternative 2, see below) or
you can use a prebuilt docker image (alternative 1). Using docker seems to be the
preferred way to get everything running under Windows.

## Alternative 1: Use docker

With this alternative, you edit the code of the compiler on your host system,
but running the compiler, executing the tests, type checking your code
is done inside a prebuilt docker image.

You need to perform the following steps:

* Install docker
* Start a shell using the provided docker image
  (you have to be in the toplevel directory of this project):

```
$ docker run -v .:/cc -ti skogsbaer/compiler-construction-wasm_linux-amd64:latest bash
```

Inside the shell, you can now run all tests (`./run-tests`) or type check your code
(`./tycheck`).

There are different docker images for x86 and arm:

* `skogsbaer/compiler-construction-wasm_linux-amd64:latest`
* `skogsbaer/compiler-construction-wasm_linux-arm64:latest`

### Keeping the image up-to-date

The docker image has to be in sync with some parts of this repository, most notably
with `requirements.txt` (for python dependencies) and
with `wasm-support/native-lib/env.c` (for native code used by wasm). The script
`docker/check-image-uptodate` can be used to check if everything is in sync.
Please contact the maintainer of this repository if a new docker image is needed.

## Alternative 2: Install everything by hand

The following installation instruction should work under Mac OSX and Linux.
I did not test under Windows, feel free to create a pull request to
add instructions for Windows.

### Install `wasm-micro-runtime` and `wabt`

On Mac OSX, `wasm-micro-runtime` and `wabt` are available as brew packages:

```
$ brew install wasm-micro-runtime
$ brew install wabt
```

On Linux, there is a package for wabt (at least on Ubuntu) but `wasm-micro-runtime`
has to be installed from source. See [docker/Dockerfile](docker/Dockerfile)
or the [official installation instructions](https://github.com/bytecodealliance/wasm-micro-runtime/blob/main/product-mini/README.md).

### Install the python toolchain:

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

### Build native exension functions for iwasm

The compiler relies on some Wasm extension functions to provide input/output functionality.
Here is how to build the native extension functions for the [iwasm](https://github.com/bytecodealliance/wasm-micro-runtime) virtual machine. `WAMR_ROOT_DIR` must point to a checkout of
[wasm-micro-runtime](https://github.com/bytecodealliance/wasm-micro-runtime).

```
$ cd wasm-support
$ make native WAMR_ROOT_DIR=/PATH_TO_CHECKOUT/wasm-micro-runtime
```

### Verifying your installation

You can now use `./run-tests` from the toplevel directory to run all tests.
If this works, your setup is complete.
