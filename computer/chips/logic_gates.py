from bitarray import bitarray


def NAND(a, b):
    if a and b:
        return 0
    return 1


def NOT(a):
    return NAND(a, a)


def AND(a, b):
    return NOT(NAND(a, b))


def OR(a, b):
    return NAND(NOT(a), NOT(b))


def XOR(a, b):
    return NAND(NAND(NOT(a), b), NAND(a, NOT(b)))


def MUX(a, b, sel):
    return OR(AND(a, NOT(sel)), AND(b, sel))


def DMUX(a, sel):
    return bitarray((AND(a, NOT(sel)), AND(a, sel)))
