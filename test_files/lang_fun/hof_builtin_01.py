### type error

def foo(f: Callable[[list[int]], int]) -> int:
    return 1

foo(len)
