import pytest

from bitarray import bitarray

from computer.chips.central_processing_unit import CPU
from computer.utility.numbers import bin_to_dec

from computer.chips.tests import (ZEROS, INT_ONE, INT_TWO, INT_THREE,
                                  INT_NEG_ONE, ALTERNATING_ZERO_ONE)

# instruction: ajms oooo prrr prrr

# Not tested opcodes
# opcode      operation
# 0000        pop
# 0001        push
# 0011        hdd op
# 0100        jump
# 0101        (jump, push address?)
# 0110        (jump)
# 0111        (jump, push address?)
# 1000        ALU op
# 1001        (push ALU op)
# 1010        (ALU op)
# 1011        (ALU op)
# 1100        jump if zero
# 1101        (jump if zero, push zero?) (reset?)
# 1110        jump if neg
# 1111        (jump if neg, push neg number?) (shutdown?)

# TODO:
# Stack operations
# ALU operations
# Jump operations
# HDD operations
# reset, shutdown

move_opcode = bitarray('0010')

alu_pass = bitarray('0000')

# address as value
a_address = bitarray('0000')
b_address = bitarray('0001')
c_address = bitarray('0010')
d_address = bitarray('0011')

# address as pointer
ap_address = bitarray('1000')
bp_address = bitarray('1001')
cp_address = bitarray('1010')
dp_address = bitarray('1011')
pcp_address = bitarray('1101')  # pc register +1 as pointer


class MockRam:
    def __init__(self, instructions):
        self.memory = {i: instruction for i, instruction in enumerate(instructions)}

        self.values = []
        self.addresses = []
        self.loads = []

        self.ticked = 0

    def __call__(self, value, address, load):
        self.values.append(value)
        self.addresses.append(address)
        self.values.append(load)

        i = bin_to_dec(address)
        out = self.memory.get(i, bitarray(16))
        if load:
            self.memory[i] = value
        return out

    def tick(self):
        self.ticked += 1


class MockHardDisk:
    pass


def register_map(cpu):
    return {'a': cpu.a, 'b': cpu.b, 'c': cpu.c, 'd': cpu.d}


class TestCPU:

    values = [ZEROS, INT_ONE, INT_TWO, ALTERNATING_ZERO_ONE]

    register_addresses = [('a', a_address),
                          ('b', b_address),
                          ('c', c_address),
                          ('d', d_address),
                          ]

    @pytest.mark.parametrize('register, address_1', register_addresses)
    @pytest.mark.parametrize('value', values)
    def test_move_constant_to_register(self, value, register, address_1):
        instructions = [move_opcode + alu_pass + address_1 + pcp_address,
                        value]

        ram = MockRam(instructions)
        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == value

    def test_move_two_constants_to_register(self):
        value_1 = INT_TWO
        value_2 = INT_THREE
        instructions = [move_opcode + alu_pass + a_address + pcp_address, value_1,
                        move_opcode + alu_pass + b_address + pcp_address, value_2]

        ram = MockRam(instructions)
        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)['a'].value == value_1

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)['b'].value == value_2

    source_target_reg_reg = [(a_address, b_address, 'b'),
                             (a_address, c_address, 'c'),
                             (a_address, d_address, 'd'),
                             (b_address, a_address, 'a'),
                             (c_address, a_address, 'a'),
                             (d_address, a_address, 'a'),
                             (b_address, c_address, 'c'),
                             (b_address, d_address, 'd')]

    @pytest.mark.parametrize('source_address, target_address, target_register', source_target_reg_reg)
    def test_move_from_register_to_register(self, source_address, target_address, target_register):
        value = INT_TWO

        instructions = [move_opcode + alu_pass + source_address + pcp_address, value,
                        move_opcode + alu_pass + target_address + source_address,
                        ]

        ram = MockRam(instructions)
        hdd = MockHardDisk()
        cpu = CPU(ram, hdd)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[target_register].value == value

    def test_move_from_register_to_register_twice(self):
        value = INT_TWO
        source_address = a_address
        target_1 = b_address
        target_2 = c_address

        instructions = [move_opcode + alu_pass + source_address + pcp_address, value,
                        move_opcode + alu_pass + target_1 + source_address,
                        move_opcode + alu_pass + target_2 + source_address,
                        ]

        ram = MockRam(instructions)
        hdd = MockHardDisk()
        cpu = CPU(ram, hdd)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)['b'].value == value
        assert register_map(cpu)['c'].value == value

    memory_value_1 = bitarray('0000010110000111')
    memory_value_2 = bitarray('0010110100000101')
    source_target_reg_mem = [(a_address, b_address, bp_address, memory_value_1),
                             (a_address, b_address, bp_address, memory_value_2),
                             (a_address, c_address, cp_address, memory_value_1),
                             (a_address, d_address, dp_address, memory_value_2),
                             (b_address, a_address, ap_address, memory_value_1),
                             ]

    @pytest.mark.parametrize('constant_reg, reg_address, reg_p_address, memory_address', source_target_reg_mem)
    def test_move_from_register_to_memory(self, constant_reg, reg_address, reg_p_address, memory_address):
        dec_address = bin_to_dec(memory_address)
        value = INT_TWO

        instructions = [move_opcode + alu_pass + constant_reg + pcp_address, value,
                        move_opcode + alu_pass + reg_address + pcp_address, memory_address,
                        move_opcode + alu_pass + reg_p_address + constant_reg
                        ]

        ram = MockRam(instructions)
        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert ram.memory[dec_address] == value

    def test_move_from_register_to_memory_twice(self):
        dec_address_1 = bin_to_dec(self.memory_value_1)
        dec_address_2 = bin_to_dec(self.memory_value_2)
        value = INT_TWO

        instructions = [move_opcode + alu_pass + a_address + pcp_address, value,
                        move_opcode + alu_pass + b_address + pcp_address, self.memory_value_1,
                        move_opcode + alu_pass + bp_address + a_address,
                        move_opcode + alu_pass + b_address + pcp_address, self.memory_value_2,
                        move_opcode + alu_pass + bp_address + a_address
                        ]

        ram = MockRam(instructions)
        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        for i in range(5):
            cpu()
            cpu.tick()

        assert ram.memory[dec_address_1] == value
        assert ram.memory[dec_address_2] == value

    def test_move_from_memory_to_register(self):
        value = INT_THREE

        instructions = [move_opcode + alu_pass + a_address + pcp_address, self.memory_value_1,
                        move_opcode + alu_pass + b_address + ap_address,
                        move_opcode + alu_pass + c_address + ap_address]

        ram = MockRam(instructions)
        dec_address = bin_to_dec(self.memory_value_1)
        ram.memory[dec_address] = value

        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.b.value == value
        assert cpu.c.value == value

    def test_move_from_memory_to_memory(self):
        value = INT_NEG_ONE

        instructions = [move_opcode + alu_pass + a_address + pcp_address, self.memory_value_1,
                        move_opcode + alu_pass + b_address + pcp_address, self.memory_value_2,
                        move_opcode + alu_pass + bp_address + ap_address,
                        ]

        ram = MockRam(instructions)
        dec_address = bin_to_dec(self.memory_value_1)
        ram.memory[dec_address] = value

        hdd = MockHardDisk()

        cpu = CPU(ram, hdd)

        cpu()
        cpu.tick()

        cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        dec_address = bin_to_dec(self.memory_value_2)
        assert ram.memory[dec_address] == value
