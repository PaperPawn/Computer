import pytest
from computer.chips.arithmetic_logic_unit import ALU

# Inputs:
# a: Int16
# b: Int16
# opcode:
# Bit 0: a = !a
# Bit 1: a = a+1
# Bit 2: b = 0
# Bit 3:

# Arithmetic        Opcode
# Add: a+b
# Subtract: b-a
# Negate: -a
# Increment: a+1
# Decrement: a-1
# Pass through: a

# Logical
# AND: bitwise a and b
# OR: bitwise a or b
# XOR: bitwise a xor b
# Bitflip: bitwise not a


# Outputs:
# out: Int16
# zero: 1 if out == 0 else 0
# neg: 1 if out < 0 else 0



# def test_alu_add