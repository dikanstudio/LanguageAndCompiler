arr = 2 * [3 * [0]]
print(arr[0][0])
print(arr[0][1])
print(arr[0][2])
print(arr[1][0])
print(arr[1][1])
print(arr[1][2])

arr[1][1] = 42
print(arr[0][0])
print(arr[0][1])
print(arr[0][2])
print(arr[1][0])
print(arr[1][1])
print(arr[1][2])