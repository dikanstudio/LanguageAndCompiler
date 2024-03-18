### type error

def foo(f: Callable[[], int]) -> int:
    return 1

foo(input_int)
