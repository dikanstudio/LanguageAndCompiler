def f1(i: int) -> int:
    if i == 0:
        return 0
    else:
        return f2(i) + 1

def f2(i: int) -> int:
    return f1(i - 1)

print(f1(5))
