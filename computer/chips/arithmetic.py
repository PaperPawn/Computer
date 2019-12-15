from computer.chips.logic_gates import XOR, AND, OR, NOT


def half_adder(a, b):
    sum_ab = XOR(a, b)
    carry = AND(a, b)
    return sum_ab, carry


def full_adder(a, b, c):
    sum_bc, carry_1 = half_adder(b, c)
    sum_abc, carry_2 = half_adder(a, sum_bc)
    carry = OR(carry_1, carry_2)
    return sum_abc, carry


def ADD16(a, b):
    out = [0]*16

    out[-1], carry = half_adder(a[-1], b[-1])
    for i in range(2, 17):
        out[-i], carry = full_adder(a[-i], b[-i], carry)
    return out


def INC16(a):
    out = [0]*16
    out[-1] = NOT(a[-1])
    carry = a[-1]
    for i in range(2, 17):
        out[-i], carry = half_adder(a[-i], carry)
    return out
