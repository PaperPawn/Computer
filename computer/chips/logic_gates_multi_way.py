from computer.chips.logic_gates import OR, DMUX
from computer.chips.logic_gates_16bit import MUX16


def OR8WAY(a):
    return OR(OR(OR(a[0], a[1]),
                 OR(a[2], a[3])),
              OR(OR(a[4], a[5]),
                 OR(a[6], a[7])))


def MUX4WAY16(a, b, c, d, sel):
    mux16_ab = MUX16(a, b, sel[1])
    mux16_cd = MUX16(c, d, sel[1])
    return MUX16(mux16_ab, mux16_cd, sel[0])


def MUX8WAY16(a, b, c, d, e, f, g, h, sel):
    mux_abcd = MUX4WAY16(a, b, c, d, sel[1:])
    mux_efgh = MUX4WAY16(e, f, g, h, sel[1:])
    return MUX16(mux_abcd, mux_efgh, sel[0])


def DMUX4WAY(a, sel):
    o1, o2 = DMUX(a, sel[0])
    return DMUX(o1, sel[1]) + DMUX(o2, sel[1])


def DMUX8WAY(a, sel):
    o1, o2, o3, o4 = DMUX4WAY(a, sel[:2])
    return DMUX(o1, sel[2]) + DMUX(o2, sel[2]) + DMUX(o3, sel[2]) + DMUX(o4, sel[2])