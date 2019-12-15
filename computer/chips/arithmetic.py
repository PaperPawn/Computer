from computer.chips.logic_gates import XOR, AND, OR


def half_adder(a, b):
    sum_ab = XOR(a, b)
    carry = AND(a, b)
    return sum_ab, carry


def full_adder(a, b, c):
    sum_bc, carry_1 = half_adder(b, c)
    sum_abc, carry_2 = half_adder(a, sum_bc)
    carry = OR(carry_1, carry_2)
    return sum_abc, carry
