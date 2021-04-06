import pytest

from bitarray import bitarray

from computer.chips.central_processing_unit import CPU
from computer.utility.numbers import bin_to_dec, dec_to_bin

from computer.chips.tests import (ZEROS, INT_ONE, INT_TWO, INT_THREE,
                                  INT_NEG_ONE, ALTERNATING_ZERO_ONE)

UNUSED = bitarray(16)
# instruction: ajms oooo prrr prrr

# Not tested opcodes
# opcode      operation
# 0000        (reset?)
# 0001        (shutdown?)
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

push_opcode = bitarray('00110000')
pop_opcode = bitarray('00111000')
move_opcode = bitarray('00100000')

alu_pass = bitarray('0000')

unused = bitarray('0000')

# address as value
a_address = bitarray('0000')
b_address = bitarray('0001')
c_address = bitarray('0010')
d_address = bitarray('0011')

sp_address = bitarray('0100')  # stack pointer as value

# address as pointer
ap_address = bitarray('1000')
bp_address = bitarray('1001')
cp_address = bitarray('1010')
dp_address = bitarray('1011')

spp_address = bitarray('1100')  # stack pointer as pointer
pcp_address = bitarray('1101')  # pc register +1 as pointer


class MockRam:
    def __init__(self):
        self.memory = {}
        self.next_memory = {}

    def __call__(self, value, address, load):
        i = bin_to_dec(bitarray('0') + address)
        out = self.memory.get(i, bitarray(16))
        if load:
            self.next_memory[i] = value
        return out

    def tick(self):
        for key in self.next_memory:
            self.memory[key] = self.next_memory[key]


class MockHardDisk:
    pass


def register_map(cpu):
    return {'a': cpu.a, 'b': cpu.b, 'c': cpu.c, 'd': cpu.d, 'sp': cpu.sp}


class TestCPU:

    @pytest.fixture
    def cpu(self):
        ram = MockRam()
        hdd = MockHardDisk()
        return CPU(ram, hdd)

    @staticmethod
    def load_instructions(ram, instructions):
        for i, instruction in enumerate(instructions):
            ram.memory[i] = instruction


class TestCPUMove(TestCPU):
    values = [ZEROS, INT_ONE, INT_TWO, ALTERNATING_ZERO_ONE]

    register_addresses = [('a', a_address),
                          ('b', b_address),
                          ('c', c_address),
                          ('d', d_address),
                          ('sp', sp_address)
                          ]

    @pytest.mark.parametrize('register, address_1', register_addresses)
    @pytest.mark.parametrize('value', values)
    def test_move_constant_to_register(self, cpu, value, register, address_1):
        instructions = [move_opcode + address_1 + pcp_address,
                        value]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == value

    def test_move_two_constants_to_register(self, cpu):
        value_1 = INT_TWO
        value_2 = INT_THREE
        instructions = [move_opcode + a_address + pcp_address, value_1,
                        move_opcode + b_address + pcp_address, value_2]
        self.load_instructions(cpu.ram, instructions)

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
                             (b_address, d_address, 'd'),
                             (a_address, sp_address, 'sp'),
                             (sp_address, a_address, 'a')]

    @pytest.mark.parametrize('source_address, target_address, target_register', source_target_reg_reg)
    def test_move_from_register_to_register(self, cpu, source_address, target_address, target_register):
        value = INT_TWO

        instructions = [move_opcode + source_address + pcp_address, value,
                        move_opcode + target_address + source_address,
                        ]

        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[target_register].value == value

    def test_move_from_register_to_register_twice(self, cpu):
        value = INT_TWO
        source_address = a_address
        target_1 = b_address
        target_2 = c_address

        instructions = [move_opcode + source_address + pcp_address, value,
                        move_opcode + target_1 + source_address,
                        move_opcode + target_2 + source_address,
                        ]

        self.load_instructions(cpu.ram, instructions)

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
                             (b_address, sp_address, spp_address, memory_value_1),
                             ]

    @pytest.mark.parametrize('constant_reg, reg_address, reg_p_address, memory_address', source_target_reg_mem)
    def test_move_from_register_to_memory(self, cpu, constant_reg, reg_address, reg_p_address, memory_address):
        value = INT_TWO

        instructions = [move_opcode + constant_reg + pcp_address, value,
                        move_opcode + reg_address + pcp_address, memory_address,
                        move_opcode + reg_p_address + constant_reg
                        ]

        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address, 0) == value

    def test_move_from_register_to_memory_twice(self, cpu):
        value = INT_TWO

        instructions = [move_opcode + a_address + pcp_address, value,
                        move_opcode + b_address + pcp_address, self.memory_value_1,
                        move_opcode + bp_address + a_address,
                        move_opcode + b_address + pcp_address, self.memory_value_2,
                        move_opcode + bp_address + a_address
                        ]

        self.load_instructions(cpu.ram, instructions)

        for i in range(5):
            cpu()
            cpu.tick()

        assert cpu.ram_bus(UNUSED, self.memory_value_1, 0) == value
        assert cpu.ram_bus(UNUSED, self.memory_value_2, 0) == value

    source_target_mem_reg = [(a_address, ap_address, b_address, 'b'),
                             (a_address, ap_address, c_address, 'c'),
                             (b_address, bp_address, a_address, 'a'),
                             (sp_address, spp_address, a_address, 'a')]

    @pytest.mark.parametrize('spource_value, source_pointer, target_address, target', source_target_mem_reg)
    def test_move_from_memory_to_register(self, cpu, spource_value, source_pointer, target_address, target):
        value = INT_THREE

        instructions = [move_opcode + spource_value + pcp_address, self.memory_value_1,
                        move_opcode + target_address + source_pointer]

        self.load_instructions(cpu.ram, instructions)
        cpu.ram_bus(value, self.memory_value_1, 1)
        cpu.ram.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[target].value == value
        # assert cpu() == 0
        # cpu.tick()

        # assert cpu.b.value == value
        # assert cpu.c.value == value

    def test_move_from_memory_to_memory(self, cpu):
        value = INT_NEG_ONE

        instructions = [move_opcode + a_address + pcp_address, self.memory_value_1,
                        move_opcode + b_address + pcp_address, self.memory_value_2,
                        move_opcode + bp_address + ap_address,
                        ]
        self.load_instructions(cpu.ram, instructions)
        cpu.ram_bus(value, self.memory_value_1, 1)
        cpu.ram.tick()

        cpu()
        cpu.tick()

        cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, self.memory_value_1, 0) == value


class TestCPUStack(TestCPU):
    def test_push_constant_twice(self, cpu):
        stack_frame = dec_to_bin(100)
        stack_frame_p1 = dec_to_bin(101)
        stack_frame_p2 = dec_to_bin(102)
        value_1 = INT_ONE
        value_2 = INT_TWO

        instructions = [move_opcode + sp_address + pcp_address, stack_frame,
                        push_opcode + spp_address + pcp_address, value_1,
                        push_opcode + spp_address + pcp_address, value_2]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame_p1
        assert cpu.ram_bus(UNUSED, stack_frame, 0) == value_1

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame_p2
        assert cpu.ram_bus(UNUSED, stack_frame, 0) == value_1
        assert cpu.ram_bus(UNUSED, stack_frame_p1, 0) == value_2

    def test_push_then_pop_constant(self, cpu):
        stack_frame = dec_to_bin(100)
        value_1 = INT_ONE

        instructions = [move_opcode + sp_address + pcp_address, stack_frame,
                        push_opcode + spp_address + pcp_address, value_1,
                        pop_opcode + a_address + spp_address]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame
        assert cpu.a.value == value_1

    def test_push_twice_then_pop_twice(self, cpu):
        stack_frame = dec_to_bin(100)
        stack_frame_p1 = dec_to_bin(101)
        # stack_frame_p2 = dec_to_bin(102)
        value_1 = INT_ONE
        value_2 = INT_TWO

        instructions = [move_opcode + sp_address + pcp_address, stack_frame,
                        push_opcode + spp_address + pcp_address, value_1,
                        push_opcode + spp_address + pcp_address, value_2,
                        pop_opcode + a_address + spp_address,
                        pop_opcode + b_address + spp_address]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame_p1
        assert cpu.a.value == value_2

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame
        assert cpu.b.value == value_1
