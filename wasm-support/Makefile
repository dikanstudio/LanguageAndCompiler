.phony: native build run clean

WAMR_ROOT_DIR = /Users/swehr/devel/wasm-micro-runtime

native:
	mkdir -p native-lib/build
	cd native-lib/build && cmake -DWAMR_ROOT_DIR=$(WAMR_ROOT_DIR) .. && make

hello.wasm: hello.wat
	wat2wasm hello.wat

build: hello.wasm

run: build
	iwasm --native-lib=native-lib/build/libenv.dylib hello.wasm

run-node: build
	./run_node hello.wasm

clean:
	rm -rf native-lib/build
	rm -f hello.wasm
