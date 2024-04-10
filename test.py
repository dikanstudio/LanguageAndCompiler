sum = 0
while input_int() == 0:
    sum = sum + 1
    i = 3
    while i > 0:
        sum = sum + i
        i = i - 1
print(sum)