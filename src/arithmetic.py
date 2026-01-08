def lnot(x: int) -> int:
    return 1 if x == 0 else 0

def land(x: int, y: int) -> int:
    return x & y

def lor(x: int, y: int) -> int:
    return x | y

def add(x: int, y: int) -> int:
    return x + y

def sub(x: int, y: int) -> int:
    return x - y    

def mul(x: int, y: int) -> int:
    return x * y

def greater(x: int, y: int) -> int:
    return x > y

def less(x: int, y: int) -> int:
    return x < y

def leq(x: int, y: int) -> int:
    return x <= y

def geq(x: int, y: int) -> int:
    return x >= y