def foo(b: bool) -> int:
    if b:
        print(1)
    else:
        return 1
    return 0
print(foo(True))
print(foo(False))
