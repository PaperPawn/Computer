from bitarray import bitarray

from computer.chips.logic_gates import NOT, AND, OR, MUX
from computer.chips.logic_gates_16bit import NOT16, AND16, OR16, XOR16
from computer.chips.logic_gates_multi_way import OR8WAY, MUX16, MUX4WAY16

from computer.chips.arithmetic import INC16, ADD16


def ALU(a, b, opcode):
    """
    :param a: INT16
    :param b: INT16
    :param opcode: 4 bytes

    alt opcodes not tested!

    Arithmetic
    Operation       opcode  alt
    Add: a+b        0100    0110
    Subtract: a-b   0101    0111
    Negate: -a      0001
    Increment: a+1  0010
    Decrement: a-1  0011
    Pass through: a 0000    1000

    Logical
    Operation               opcode  alt
    Bitflip: bitwise not a  1001

    AND: bitwise a and b    1010
    OR: bitwise a or b      1100
    XOR: bitwise a xor b    1110

    NOT(A) AND B:           1101
    NOT(A) OR B:            1011
    NOT(A) XOR B:           1111

    :return:
    :out: INT16
    :is_zero: 1 if out == 0 else 0
    :is_neg: 1 if out < 0 else 0
    """

    bitflip = NOT16(a)

    # Arithmetic
    neg_a, dec_carry = INC16(bitflip)
    a1 = MUX16(a, neg_a, opcode[3])

    inc, inc_carry = INC16(a1)
    dec, _ = INC16(NOT16(inc))
    inc_or_dec = MUX16(inc, dec, opcode[3])

    add, add_carry = ADD16(a1, b)
    sub, _ = INC16(NOT16(add))
    add_or_sub = MUX16(add, sub, opcode[3])

    pass_through_or_incdec = MUX16(a1, inc_or_dec, opcode[2])
    arithmetic = MUX16(pass_through_or_incdec, add_or_sub, opcode[1])

    # Logical
    a_log = MUX16(a, bitflip, opcode[3])

    logical = MUX4WAY16(a_log, AND16(a_log, b), OR16(a_log, b), XOR16(a_log, b), opcode[1:3])

    # Choose arithmetic or logical output
    out = MUX16(arithmetic, logical, opcode[0])

    # Set control bits
    is_zero = NOT(OR(OR8WAY(out[0:8]), OR8WAY(out[8:16])))
    is_neg = out[0]

    # carry = MUX(0, inc_carry, opcode[2])
    carry_2 = MUX(0, add_carry, opcode[1])
    carry_1 = MUX(carry_2, inc_carry, AND(opcode[2], NOT(opcode[3])))
    carry_a = MUX(carry_1, dec_carry, AND(opcode[2], opcode[3]))
    carry = MUX(carry_a, 0, opcode[0])
    return out, is_zero, is_neg, carry
