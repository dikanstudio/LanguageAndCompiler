### run error
n = 10001 # needs 80012 bytes of memory
arr = n * [0]
arr[0] = 42
arr[n - 2] = 10
arr[n - 1] = 11

print(arr[0])
print(arr[1])
print(arr[n-3])
print(arr[n-2])
print(arr[n-1])
