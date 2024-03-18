### type error
def foo(i: int) -> int:
    return i + 1

def bar(i: int, f: Callable[[int], int]) -> int:
    if i == 0:
        foo = f  # keep it simple: do not allow assignments to global function vars
    return foo(1)
