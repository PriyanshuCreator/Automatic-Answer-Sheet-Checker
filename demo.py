def print_name(n,i):
    if n<i:
        return 
    print(n)
    print_name(n-1,i)
print_name(4,1)
