def NAND(a, b):
    return not (a and b)


def NOT(a):
    return not a


def AND(a, b):
    return a and b


def OR(a, b):
    return a or b


def XOR(a, b):
    return a != b


def MUX(a, b, sel):
    if sel:
        return b
    else:
        return a


def DMUX(a, sel):
    if sel:
        return 0, a
    else:
        return a, 0
