### type error

def foo(f: Callable[[int], None]) -> int:
    return 1

foo(print)
