(module
  (import "env" "memory" (memory 1))
  (import "env" "print" (func $print (param i32 i32)))
  (import "env" "print_i32" (func $print_i32 (param i32)))
  (import "env" "print_i64" (func $print_i64 (param i64)))
  (import "env" "print_f32" (func $print_f32 (param f32)))
  (import "env" "print_f64" (func $print_f64 (param f64)))
  (import "env" "input_i32" (func $input_i32 (result i32)))

  (table funcref
    (elem $my_add $my_add_4 $my_hof))

  (export "main" (func $main))

  (data (i32.const 1) "Hello, World!")

  (func $my_add (param $x i32) (param $y i32) (result i32)
    (local $z i32)
    ;; (local $y i32)

    (i32.const 1)
    (local.set $z)
    (local.get $x)
    (local.get $y)
    i32.add
    (local.get $z)
    i32.add
  )

  ;; if x == 0:
  ;;     return 42
  ;; x = x + 1
  ;; return x
  (func $early_exit (param $x i64) (result i64)
    block $fun_exit (result i64)
      (local.get $x)
      (i64.const 0)
      i64.eq
      if
        (i64.const 42)
        (br $fun_exit)
      else
      end
      (local.get $x)
      (i64.const 1)
      i64.add
      (local.set $x)
      (local.get $x)
      (br $fun_exit)
    end
  )

  (func $my_add_4 (param $x i64) (result i64)
    (i64.const 4)
    (local.get $x)
    i64.add
  )

  (func $my_hof (param $f i32) (result i64) ;; a function i64 -> i64
    (i64.const 38)
    (local.get $f)
    (call_indirect (param i64) (result i64))
  )

  (func $main
    (local $n i32)
    (local $res i32)
    (local $top i32)

    (i32.const 1)  ;; start of string
    (i32.const 13) ;; length of string
    (call $print)

    i32.const 42
    call $print_i32

    ;; computer (2*3) + (4*5)
    i32.const 2
    i32.const 3
    i32.mul

    i32.const 4
    i32.const 5
    i32.mul

    i32.add

    call $print_i32

    ;; print 1 if user entered non-zero number, print 0 otherwise
    ;; (call $input_i32)
    (i32.const 4)
    if (result i32)
      (i32.const 1)
    else
      (i32.const 0)
    end
    call $print_i32


    ;; compute n+(n-1)+(n-2)+...+1, where n is user input
    ;; pseudo-code:
    ;; res = 0; while (n > 0) { res = res + n; n--; }
    ;; call $input_i32
    (i32.const 2)
    (local.set $n)

    i32.const 0
    (local.set $res)
    block $loop_exit
      loop $loop_start ;; (result i32)
        ;; jump out of loop if n > 0
        (local.get $n)
        (i32.const 0)
        i32.gt_s

        ;; (local.tee $top)
        ;; (local.get $top)
        ;; (call $print_i32)

        if else (br $loop_exit) end
        ;; (br_if $loop_exit)

        ;; loop body
        ;; res = res + n
        (local.get $res)
        (local.get $n)
        i32.add
        (local.set $res)
        ;; n--
        (local.get $n)
        (i32.const 1)
        i32.sub
        (local.set $n)

        ;; (local.get $n)
        ;; (call $print_i32)

        (br $loop_start)
      end
    end
    (local.get $res)
    (call $print_i32)

    ;; play with arrays
    ;; allocate the array 1,2,3 starting at address 38
    (i32.const 38)
    (i64.const 1)
    i64.store
    (i32.const 46)
    (i64.const 2)
    i64.store
    (i32.const 54)
    (i64.const 3)
    i64.store
    ;; get array at index 1
    (i32.const 46)
    i64.load
    (call $print_i64)

    (i32.const 1)
    (i32.const 40)
    (call $my_add)
    (call $print_i32)

    ;;(u32.const $my_add_4)
    (i32.const 1) ;; index of $my_add
    (call $my_hof)
    (call $print_i64)

    (i64.const 1)
    (call $early_exit)
    (call $print_i64)
    (i64.const 0)
    (call $early_exit)
    (call $print_i64)
  )

)
