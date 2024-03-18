const memory = new WebAssembly.Memory({
    initial: 10,
    maximum: 100,
  });

const isBrowser = typeof document !== 'undefined'

function _print(x) {
    if (isBrowser) {
        const elem = document.getElementById("output");
        elem.append("" + x + "\n");
    } else {
        console.log(x);
    }
}

function print(start,len) {
    const arrayBuffer = memory.buffer;
    const buffer = new Uint8Array(arrayBuffer, start, len);
    var string = new TextDecoder().decode(buffer);
    _print(string);
}

function print_i32(i) {
    _print(i);
}

function print_i64(i) {
    _print(i);
}

function print_f32(i) {
    _print(i);
}

function print_f64(i) {
    _print(i);
}

function input_i32_browser() {
    const msg = "input int"
    let i = Number(prompt(msg));
    while (isNaN(i)) {
        i = prompt(msg);
    }
    return i;
}

function abort(msg) {
    console.error("ABORT: " + msg);
    process.exit(1);
}

function input_i32_node() {
    const fs = require('node:fs');
    while (true) {
        process.stdout.write('input int: ');
        const bufsize = 256;
        const buf = Buffer.alloc(bufsize);
        for (let i = 0; i < bufsize; i++) {
            const bytesRead = fs.readSync(0, buf, i, 1);
            if (bytesRead == 0) {
                abort("no more input");
            }
            const c = buf.at(i);
            if (c == 10) { // \n
                const s = buf.toString('utf-8', 0, i);
                let x = Number(s);
                if (!isNaN(x)) {
                    return Math.floor(x);
                } else {
                    abort("invalid number: " + s);
                }
            }
        }
    }
}
function input_i32() {
    if (isBrowser) {
        return input_i32_browser();
    } else {
        return input_i32_node();
    }
}

const envObject = {
    env: { print, print_i32, print_i64, print_f32, print_f64, input_i32, memory },
};

function runWasm(bytes) {
    WebAssembly.instantiate(bytes, envObject).then((wasmModule) => {
        wasmModule.instance.exports.main();
    });
}

exports.runWasm = runWasm;
