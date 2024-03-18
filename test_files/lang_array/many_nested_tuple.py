i = 0
while i != 10:
    t1 = [i]
    t2 = [t1,t1,t1]
    t3 = [t2,t2,t2]
    i = t3[0][0][0] + 1  # i = i + 1
print( i - i + 42 )
