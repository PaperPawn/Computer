from bitarray import bitarray
from computer.chips.logic_gates import NOT, AND, OR, XOR, MUX


def NOT16(a):
    out = bitarray(16)

    for i in range(16):
        out[i] = NOT(a[i])
    return out


def AND16(a, b):
    out = bitarray(16)

    for i in range(16):
        out[i] = AND(a[i], b[i])
    return out


def OR16(a, b):
    out = bitarray(16)

    for i in range(16):
        out[i] = OR(a[i], b[i])
    return out


def XOR16(a, b):
    out = bitarray(16)

    for i in range(16):
        out[i] = XOR(a[i], b[i])
    return out


def MUX16(a, b, sel):
    out = bitarray(16)

    for i in range(16):
        out[i] = MUX(a[i], b[i], sel)
    return out
