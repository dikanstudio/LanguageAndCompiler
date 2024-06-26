def foo(i: int, b: bool, arr: list[list[int]], fun: Callable[[int, bool], list[bool]]) -> bool:
    x = arr[i][0]
    y = fun(x, b)
    return y[0]

def bar(i: int, b: bool) -> list[bool]:
    return [b]

def spam(i: int, b: bool) -> list[bool]:
    if i == 1:
        return [False]
    else:
        return [True]

print(foo(1, True, [[1], [2]], bar))
print(foo(1, True, [[1], [2]], spam))