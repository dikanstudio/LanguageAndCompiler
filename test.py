TEST = 5

def call_all(l: list[Callable[[int], int]]) -> int:
    sum = 0
    n = len(l)
    i = 0
    while i < n:
        sum = sum + l[i](1)
        i = i + 1
    return sum

def add_one(i: int) -> int:
    return i + 1

def add_two(i: int) -> int:
    return i + 2

print(call_all([add_one, add_two, add_one]))
