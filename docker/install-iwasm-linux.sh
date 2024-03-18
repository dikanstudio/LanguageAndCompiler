#!/bin/bash

mkdir /cc-support || exit 1
cd /cc-support || exit 1
git clone https://github.com/bytecodealliance/wasm-micro-runtime.git wasm-micro-runtime || exit 1
cd wasm-micro-runtime/product-mini/platforms/linux/ || exit 1
mkdir build || exit 1
cd build || exit 1
cmake .. || exit 1
make || exit 1
cp ./iwasm /usr/local/bin || exit 1
