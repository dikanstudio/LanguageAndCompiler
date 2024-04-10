n = input_int()
if n < -1:
    print(-1)
else:
    res = 1
    while n > 0:
        res = res * n
        n = n - 1
    print(res)