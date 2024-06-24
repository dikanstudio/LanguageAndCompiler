def call_all(l: list[Callable[[int], int]]) -> int:
    sum = 0
    n = len(l)
    i = 0
    while i < n:
        sum = sum + l[i](1)
        i = i + 1
    return sum
