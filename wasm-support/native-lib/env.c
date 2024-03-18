/*
 * Copyright (C) 2019 Intel Corporation.  All rights reserved.
 * SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
 */

#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <unistd.h>

#include "wasm_export.h"

static void print_wrapper(wasm_exec_env_t exec_env, const char *buf, int buf_len)
{
    printf("%.*s\n", buf_len, buf);
}

static void print_err_wrapper(wasm_exec_env_t exec_env, const char *buf, int buf_len)
{
    fprintf(stderr, "ERROR: %.*s\n", buf_len, buf);
}

static void print_bool_wrapper(wasm_exec_env_t exec_env, int32_t x)
{
    if (x) {
        printf("True\n");
    } else {
        printf("False\n");
    }
}

static void print_i32_wrapper(wasm_exec_env_t exec_env, int32_t x)
{
    printf("%" PRId32 "\n", x);
}

static void print_i64_wrapper(wasm_exec_env_t exec_env, int64_t x)
{
    printf("%" PRId64 "\n", x);
}

static void print_f32_wrapper(wasm_exec_env_t exec_env, float x)
{
    printf("%f\n", x);
}

static void print_f64_wrapper(wasm_exec_env_t exec_env, double x)
{
    printf("%f\n", x);
}

static int32_t input_i32_wrapper(wasm_exec_env_t exec_env) {
    int32_t res;
    if(isatty(1)) {
        // stdout is a terminal
        printf("input int: ");
    }
    int i = scanf("%" PRId32 "", &res);
    if (i == 1) {
        return res;
    } else {
        fprintf(stderr, "Invalid input");
        abort();
    }
}

static int64_t input_i64_wrapper(wasm_exec_env_t exec_env) {
    int64_t res;
    if(isatty(1)) {
        // stdout is a terminal
        printf("input int: ");
    }
    int i = scanf("%" PRId64 "", &res);
    if (i == 1) {
        return res;
    } else {
        fprintf(stderr, "Invalid input");
        abort();
    }
}

/* clang-format off */
#define REG_NATIVE_FUNC(func_name, signature) \
    { #func_name, func_name##_wrapper, signature, NULL }

static NativeSymbol native_symbols[] = {
    REG_NATIVE_FUNC(print, "(*~)"),
    REG_NATIVE_FUNC(print_err, "(*~)"),
    REG_NATIVE_FUNC(print_i32, "(i)"),
    REG_NATIVE_FUNC(print_bool, "(i)"),
    REG_NATIVE_FUNC(print_i64, "(I)"),
    REG_NATIVE_FUNC(print_f32, "(f)"),
    REG_NATIVE_FUNC(print_f64, "(F)"),
    REG_NATIVE_FUNC(input_i32, "()i"),
    REG_NATIVE_FUNC(input_i64, "()I")
};
/* clang-format on */

uint32_t
get_native_lib(char **p_module_name, NativeSymbol **p_native_symbols)
{
    *p_module_name = "env";
    *p_native_symbols = native_symbols;
    return sizeof(native_symbols) / sizeof(NativeSymbol);
}
