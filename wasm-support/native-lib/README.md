See
https://github.com/bytecodealliance/wasm-micro-runtime/blob/main/doc/export_native_api.md

## Preparation

Please install WASI SDK, download the [wasi-sdk release](https://github.com/CraneStation/wasi-sdk/releases) and extract the archive to default path `/opt/wasi-sdk`.

## Build

```bash
mkdir build
cd build
cmake ..
make
```
