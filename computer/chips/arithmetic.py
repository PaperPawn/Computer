from computer.chips.logic_gates import XOR, AND


def half_adder(a, b):
    sum_ab = XOR(a, b)
    carry = AND(a, b)
    return sum_ab, carry
