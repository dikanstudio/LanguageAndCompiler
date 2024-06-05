[![Python CI](https://github.com/HSO-swehr/compiler-construction-student/actions/workflows/github-action-test-python.yml/badge.svg)](https://github.com/HSO-swehr/compiler-construction-student/actions/workflows/github-action-test-python.yml)

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

**NOTE: this is the student repository. It is a partial copy of the main repository.**

# Commands

You start the interpreter and the compiler through the `scripts/run` script or via
`python src/main.py`. Here are the three most common ways of invocation:

* `scripts/run interp FILE.py` runs the input file `FILE.py` throught the interpreter.
* `scripts/run compile FILE.py` compiles input file `FILE.py`, the compilation result will
be placed in textual form in `out.wat`.
* `scripts/run run FILE.py` compiles the input file and runs the resulting wasm code with iwasm.

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

You can run the type checker manually with the `scripts/tycheck` command.

## Tests

The `test_files` directory contains many tests for the different languages. We
use [pytest](https://docs.pytest.org/en/8.0.x/) for executing the tests.

The `scripts/run-tests` command runs all tests. Here is how to run only a subset of the tests:

```
scripts/run-tests FILES_OR_DIRECTORIES -k TEST_NAME_PATTERN
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

See below for a list of requirements.
You can either install the requirements on your local system (alternative 2) or
you can use a prebuilt docker image (alternative 1).
Installation via docker is simpler that a local installation. Especially under
Windows, using docker is the
preferred way to get everything running.

## Requirements

* Python version 3.12.x (a later version should also work, 3.11 or earlier does **not** work)
* iwasm virtual from the [wasm-micro-runtime](https://github.com/bytecodealliance/wasm-micro-runtime) package,
  a virtual machine for Wasm.
* [wabt](https://github.com/webassembly/wabt), which contains the `wat2wasm` tool for converting
  the textual representation of Wasm to binary form.
* GNU make
* cmake, to build the native extension functions for wasm-micro-runtime.
* nodejs and npm
* bash
* timeout command.
* [SPIM](https://spimsimulator.sourceforge.net/), a MIPS32 simulator (version 8 or 9)
* Optional, for visualizing graph trees: graphviz

## Alternative 1: Use docker

With this alternative, you edit the code of the compiler on your host system,
but running the compiler, executing the tests, type checking your code
is done inside a prebuilt docker image.

You need to perform the following steps:

* Install docker (Under Windows, use docker under WSL. See below)
* Start a shell using the provided docker image
  (you have to be in the toplevel directory of this project):

```
$ docker run -v .:/cc -ti skogsbaer/compiler-construction-wasm_linux-amd64:latest bash
```

In some cases, you might need to specify the current directory not via `.`
but as an absolute path. In this case, the command is:

```
$ docker run -v /PATH_TO_YOUR_CHECKOUT_OF_THIS_REPO:/cc -ti skogsbaer/compiler-construction-wasm_linux-amd64:latest bash
```

(Replace
`/PATH_TO_YOUR_CHECKOUT_OF_THIS_REPO` with the absolute path to the clone
of this repository):


Inside the shell, you can now run all tests (`scripts/run-tests`) or type check your code
(`scripts/tycheck`).

There are different docker images for x86 and arm:

* `skogsbaer/compiler-construction-wasm_linux-amd64:latest`
* `skogsbaer/compiler-construction-wasm_linux-arm64:latest`

### Keeping the image up-to-date

The docker image has to be in sync with some parts of this repository, most notably
with `requirements.txt` (for python dependencies) and
with `wasm-support/native-lib/env.c` (for native code used by wasm). The script
`docker/check-image-uptodate` can be used to check if everything is in sync.
Please contact the maintainer of this repository if a new docker image is needed.

### Tips for Windows user

On Windows, you might run into line ending problems. For example, if you
perform a git checkout in Windows, line endings are transformed into
`\r\n`, but the commands inside the docker container expects unix-style
line endings `\n`. Also, there are sometimes problems with Docker Desktop
on Windows.

To solve these problems, follow these steps:

* Install the Windows Subsystem for Linux (WSL).
* Install docker inside the WSL and use docker inside WSL. Do not use Docker Desktop.
* Install git under WSL and always use git under WSL.

The only downside of this approach is that you cannot use the git tools
provide by Visual Studio code, you always have to use the commandline
under WSL.

### Using Visual Studio Code with Docker

To make proper use of the Python extension for Visual Studio Code, you need to install
the python toolchain also outside of docker.
First, make sure you have Python 3.12 (a later version should also work). Then execute
the following commands from the toplevel directory of this project:

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Alternative 2: Install everything by hand

The following installation instruction should work under Mac OSX and Linux. Make sure
you install all tools mentioned in the list above. Below, you find more detailed instructions
for some but not all required tools.

I did not test under Windows, feel free to create a pull request to
add instructions for Windows. However, I recommend using the installation
via docker under Windows.

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

First, make sure you have Python 3.12 (a later version should also work).
Then execute from the toplevel directory of this project:

```
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

### Build native extension functions for iwasm

The compiler relies on some Wasm extension functions to provide input/output functionality.
Here is how to build the native extension functions for the
[iwasm](https://github.com/bytecodealliance/wasm-micro-runtime) virtual
machine.
To build the native functions, you must checkout the
[wasm-micro-runtime](https://github.com/bytecodealliance/wasm-micro-runtime)
repositoy via git, even if installed it previously in some other way.
After cloning the wasm-micro-runtime repository, switch to the branch that
corresponds to the version of iwasm that you installed previously.

1. Get the version of iwasm with `iwasm --version`. Suppose the version is
   1.3.2.
2. In the clone of the wasm-micro-runtime repository, switch to the right
   branch with `git checkout WAMR-1.3.2`.

After setting up the clone of wasm-micro-runtime this way, execute the
following commands to build the native functions.
Here, `PATH_TO_WARM_CHECKOUT` must point to the directory with the clone of
wasm-micro-runtime.

```
$ cd wasm-support
$ make native WAMR_ROOT_DIR=/PATH_TO_WARM_CHECKOUT
```

## Install pyright

You need to install nodejs and npm first. Then, from the toplevel
directory of this project, execute:

```
$ npm install
```

## Misc

The tests of this project rely on the `timeout` command. Under Mac,
this is available via `brew install coreutils`.


### Verifying your installation

You can now use `scripts/run-tests` from the toplevel directory to run all tests.
If this works, your setup is complete.
