t1 = [3, 7]
t2 = t1
t3 = [3, 7]
if (t1 is t2) and not (t1 is t3):
    print(42)
else:
    print(0)
