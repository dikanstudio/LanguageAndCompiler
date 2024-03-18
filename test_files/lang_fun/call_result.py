def getFun(i: int, f: Callable[[int], int], g: Callable[[int], int]) -> Callable[[int], int]:
    if i == 0:
        return f
    else:
        return g

def inc1(i: int) -> int:
    return i + 1

def inc2(i: int) -> int:
    return i + 2

print(getFun(0, inc1, inc2)(41))
print(getFun(1, inc1, inc2)(40))
