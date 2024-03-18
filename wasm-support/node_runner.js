const fs = require('node:fs');
const lib = require('./wasm_lib');

const args = process.argv;

if (args.length != 3) {
    console.error("USAGE: node node_runner.js FILE.wasm");
    process.exit(1);
}

const wasmBuffer = fs.readFileSync(args[2]);
lib.runWasm(wasmBuffer);
