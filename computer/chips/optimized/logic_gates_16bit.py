from computer.chips.optimized.logic_gates import NOT, AND, OR, MUX


def NOT16(a):
    out = [0] * 16

    for i in range(16):
        out[i] = NOT(a[i])
    return out


def AND16(a, b):
    out = [0]*16

    for i in range(16):
        out[i] = AND(a[i], b[i])
    return out


def OR16(a, b):
    out = [0]*16

    for i in range(16):
        out[i] = OR(a[i], b[i])
    return out


def MUX16(a, b, sel):
    out = [0] * 16

    for i in range(16):
        out[i] = MUX(a[i], b[i], sel)
    return out
