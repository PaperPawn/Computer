import pytest

from bitarray import bitarray

from computer.chips.central_processing_unit import CPU
from computer.io.harddisk import HardDisk
from computer.utility.numbers import bin_to_dec, dec_to_bin
from computer.opcodes import *

from computer.chips.tests import (ZEROS, INT_ONE, INT_TWO, INT_THREE,
                                  INT_NEG_ONE, ALTERNATING_ZERO_ONE)

UNUSED = bitarray(16)
# Not tested opcodes:
# opcode      operation
# 1000        ALU op, without move (not all ALU operations tested in CPU)
# 1001        (ALU op, no move)
# 1010        ALU op (not all ALU operations tested in CPU)
# 1011        (ALU op, to stack?)
# 1100        (ALU op, with jump?)
# 1101        (ALU op, with jump?)
# 1110        (ALU op, with move)
# 1111        (ALU op, to stack?)

# TODO:
# ALU operations with stack pointer as target
# Update status register to three single bit registers?


class MockRam:
    def __init__(self):
        self.memory = {}
        self.next_memory = {}

    def __call__(self, value, address, load):
        i = bin_to_dec(address)
        out = self.memory.get(i, bitarray(16))
        if load:
            self.next_memory[i] = value
        return out

    def tick(self):
        for key in self.next_memory:
            self.memory[key] = self.next_memory[key]


class MockHardDisk:
    def __call__(self, address, select_sector, value, write):
        if select_sector or write:
            raise AssertionError(f'select_sector ({select_sector}) and write ({write}) must be 0')
        return UNUSED

    def tick(self):
        pass


def register_map(cpu):
    return {'a': cpu.a, 'b': cpu.b, 'c': cpu.c, 'd': cpu.d, 'sp': cpu.sp}


class TestCPU:

    @pytest.fixture
    def cpu(self):
        ram = self.make_ram()
        hdd = self.make_hdd()
        return CPU(ram, hdd)

    @staticmethod
    def make_ram():
        return MockRam()

    @staticmethod
    def make_hdd():
        return MockHardDisk()

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
        instructions = [move_opcode + address_1 + constant_address, value]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == value

    def test_move_constant_as_pointer_to_register(self, cpu):
        memory_address = dec_to_bin(1024)
        value = INT_ONE
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + ap_address + constant_address, value,
                        move_opcode + b_address + constantp_address, memory_address
                        ]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.b.value == value

    def test_move_from_register_to_constant_as_pointer(self, cpu):
        memory_address = dec_to_bin(1024)
        value = INT_ONE
        instructions = [move_opcode + a_address + constant_address, value,
                        move_opcode + constantp_address + a_address, memory_address,
                        ]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address, 0) == value
        assert cpu.pc(UNUSED, 0, 0, 0) == dec_to_bin(4)

    def test_move_two_constants_to_register(self, cpu):
        value_1 = INT_TWO
        value_2 = INT_THREE
        instructions = [move_opcode + a_address + constant_address, value_1,
                        move_opcode + b_address + constant_address, value_2]
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

        instructions = [move_opcode + source_address + constant_address, value,
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

        instructions = [move_opcode + source_address + constant_address, value,
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

        instructions = [move_opcode + constant_reg + constant_address, value,
                        move_opcode + reg_address + constant_address, memory_address,
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

        instructions = [move_opcode + a_address + constant_address, value,
                        move_opcode + b_address + constant_address, self.memory_value_1,
                        move_opcode + bp_address + a_address,
                        move_opcode + b_address + constant_address, self.memory_value_2,
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

        instructions = [move_opcode + spource_value + constant_address, self.memory_value_1,
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

        instructions = [move_opcode + a_address + constant_address, self.memory_value_1,
                        move_opcode + b_address + constant_address, self.memory_value_2,
                        move_opcode + bp_address + ap_address,
                        ]
        self.load_instructions(cpu.ram, instructions)
        cpu.ram_bus(value, self.memory_value_1, 1)
        cpu.ram.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        # assert cpu.a.value == self.memory_value_1
        # assert cpu.b.value == self.memory_value_2
        assert cpu.ram_bus(UNUSED, self.memory_value_1, 0) == value


class TestCPUStack(TestCPU):
    stack_frames = [1024, 2048]

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_constant_twice(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        stack_frame_p1 = dec_to_bin(stack_frame_dec - 1)
        stack_frame_p2 = dec_to_bin(stack_frame_dec - 2)
        value_1 = INT_ONE
        value_2 = INT_TWO

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        push_opcode + spp_address + constant_address, value_1,
                        push_opcode + spp_address + constant_address, value_2]
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

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_from_register(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        stack_frame_p1 = dec_to_bin(stack_frame_dec - 1)
        value_1 = INT_ONE

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        move_opcode + a_address + constant_address, value_1,
                        push_opcode + spp_address + a_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame_p1
        assert cpu.ram_bus(UNUSED, stack_frame, 0) == value_1

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_from_memory(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        stack_frame_p1 = dec_to_bin(stack_frame_dec - 1)
        value_1 = INT_ONE
        memory_address = dec_to_bin(20)

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        move_opcode + a_address + constant_address, memory_address,
                        move_opcode + ap_address + constant_address, value_1,
                        push_opcode + spp_address + ap_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame_p1
        assert cpu.ram_bus(UNUSED, memory_address, 0) == value_1

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_constant_then_pop_to_register(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        value_1 = INT_ONE

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        push_opcode + spp_address + constant_address, value_1,
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

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_constant_then_pop_to_memory(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        value_1 = INT_ONE
        memory_address = dec_to_bin(10)

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        move_opcode + a_address + constant_address, memory_address,
                        push_opcode + spp_address + constant_address, value_1,
                        pop_opcode + ap_address + spp_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.sp.value == stack_frame
        assert cpu.ram_bus(UNUSED, memory_address, 0) == value_1

    @pytest.mark.parametrize('stack_frame_dec', stack_frames)
    def test_push_twice_then_pop_twice(self, cpu, stack_frame_dec):
        stack_frame = dec_to_bin(stack_frame_dec)
        stack_frame_p1 = dec_to_bin(stack_frame_dec - 1)
        value_1 = INT_ONE
        value_2 = INT_TWO

        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        push_opcode + spp_address + constant_address, value_1,
                        push_opcode + spp_address + constant_address, value_2,
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


class TestCPUALU(TestCPU):
    addresses_register = [(a_address, 'a'),
                          (b_address, 'b'),
                          (c_address, 'c'),
                          (d_address, 'd')]

    @pytest.mark.parametrize('address, register', addresses_register)
    def test_alu_pass(self, cpu, address, register):
        value = INT_ONE
        instructions = [move_opcode + address + constant_address, value,
                        alu_opcode + alu_pass + address + unused_opcode]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == value

    values_add = [(INT_ONE, INT_ONE, INT_TWO),
                  (ZEROS, INT_ONE, INT_ONE),
                  (INT_NEG_ONE, INT_ONE, ZEROS)]
    addresses_registers = [(a_address, b_address, 'a'),
                           (b_address, a_address, 'b'),
                           (c_address, a_address, 'c'),
                           (d_address, a_address, 'd')]

    @pytest.mark.parametrize('address_1, address_2, register', addresses_registers)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_registers(self, cpu, address_1, address_2, register,
                               value_1, value_2, expected):
        instructions = [move_opcode + address_1 + constant_address, value_1,
                        move_opcode + address_2 + constant_address, value_2,
                        alu_opcode + alu_add + address_1 + address_2]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == expected

    @pytest.mark.parametrize('address_1, register', addresses_register)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_constant_to_register(self, cpu, address_1, register,
                                          value_1, value_2, expected):
        instructions = [move_opcode + address_1 + constant_address, value_1,
                        alu_opcode + alu_add + address_1 + constant_address, value_2]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == expected

    values_sub = [(INT_ONE, INT_ONE, ZEROS),
                  (INT_ONE, ZEROS, INT_ONE),
                  (INT_ONE, INT_NEG_ONE, INT_TWO),
                  ]

    memory_addresses = [dec_to_bin(100), dec_to_bin(1000)]

    @pytest.mark.parametrize('memory_address', memory_addresses)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_constant_to_memory(self, cpu, memory_address,
                                        value_1, value_2, expected):
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + ap_address + constant_address, value_1,
                        alu_opcode + alu_add + ap_address + constant_address, value_2]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address, 0) == expected

    @pytest.mark.parametrize('memory_address', memory_addresses)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_register_to_memory(self, cpu, memory_address,
                                        value_1, value_2, expected):
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + b_address + constant_address, value_2,
                        move_opcode + ap_address + constant_address, value_1,
                        alu_opcode + alu_add + ap_address + b_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address, 0) == expected

    @pytest.mark.parametrize('memory_address', memory_addresses)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_register_to_constant_as_pointer(self, cpu, memory_address,
                                                     value_1, value_2, expected):
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + b_address + constant_address, value_2,
                        move_opcode + ap_address + constant_address, value_1,
                        alu_opcode + alu_add + constantp_address + b_address, memory_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address, 0) == expected

    @pytest.mark.parametrize('memory_address', memory_addresses)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_memory_register(self, cpu, memory_address,
                                     value_1, value_2, expected):
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + b_address + constant_address, value_2,
                        move_opcode + ap_address + constant_address, value_1,
                        alu_opcode + alu_add + b_address + ap_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.b.value == expected

    two_memory_addresses = [(dec_to_bin(1000), dec_to_bin(2000)),
                            (dec_to_bin(1024), dec_to_bin(4000))]

    @pytest.mark.parametrize('memory_address_1, memory_address_2', two_memory_addresses)
    @pytest.mark.parametrize('value_1, value_2, expected', values_add)
    def test_alu_add_memory_to_memory(self, cpu, memory_address_1, memory_address_2,
                                      value_1, value_2, expected):
        instructions = [move_opcode + a_address + constant_address, memory_address_1,
                        move_opcode + b_address + constant_address, memory_address_2,
                        move_opcode + ap_address + constant_address, value_1,
                        move_opcode + bp_address + constant_address, value_2,
                        alu_opcode + alu_add + ap_address + bp_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.ram_bus(UNUSED, memory_address_1, 0) == expected

    @pytest.mark.parametrize('address_1, address_2, register', addresses_registers)
    @pytest.mark.parametrize('value_1, value_2, expected', values_sub)
    def test_alu_sub_registers(self, cpu, address_1, address_2, register,
                               value_1, value_2, expected):
        instructions = [move_opcode + address_1 + constant_address, value_1,
                        move_opcode + address_2 + constant_address, value_2,
                        alu_opcode + alu_sub + address_1 + address_2]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert register_map(cpu)[register].value == expected

    def test_alu_no_move(self, cpu):
        instructions = [move_opcode + a_address + constant_address, INT_ONE,
                        move_opcode + b_address + constant_address, INT_ONE,
                        alu_no_move_opcode + alu_add + a_address + b_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == INT_ONE


class TestCPUJump(TestCPU):
    addresses = [dec_to_bin(1024), dec_to_bin(2048)]

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant(self, cpu, address):
        instructions = [jump_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address

    registers = [a_address, b_address, c_address, d_address]

    @pytest.mark.parametrize('register_address', registers)
    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_register(self, cpu, register_address, address):
        instructions = [move_opcode + register_address + constant_address, address,
                        jump_opcode + unused_opcode + register_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_memory(self, cpu, address):
        memory_address = dec_to_bin(100)
        instructions = [move_opcode + a_address + constant_address, memory_address,
                        move_opcode + ap_address + constant_address, address,
                        jump_opcode + unused_opcode + ap_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address

    @pytest.mark.parametrize('address', addresses)
    def test_jump_should_not_set_register(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, ZEROS,
                        jump_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu.a.value == ZEROS

    def test_jump_loop(self, cpu):
        instructions = [move_opcode + a_address + constant_address, ZEROS,
                        alu_opcode + alu_inc + a_address + unused_opcode,
                        jump_opcode + unused_opcode + constant_address, dec_to_bin(2)]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        for i in range(10):
            for _ in range(2):
                cpu()
                cpu.tick()

        assert cpu.a.value == dec_to_bin(10)


class TestCPUJumpZero(TestCPU):
    addresses = [dec_to_bin(1024), dec_to_bin(2048)]

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_not_zero(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, INT_ONE,
                        alu_no_move_opcode + alu_pass + a_address + unused_opcode,
                        jump_zero_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == INT_ONE
        assert cpu.pc(UNUSED, 0, 0, 0) == dec_to_bin(5)

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_is_zero(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, ZEROS,
                        alu_no_move_opcode + alu_pass + a_address + unused_opcode,
                        jump_zero_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == ZEROS
        assert cpu.pc(UNUSED, 0, 0, 0) == address

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_is_zero_intermediate_move(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, ZEROS,
                        alu_no_move_opcode + alu_pass + a_address + unused_opcode,
                        move_opcode + b_address + constant_address, INT_ONE,
                        jump_zero_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address


class TestCPUJumpNegative(TestCPU):
    addresses = [dec_to_bin(1024), dec_to_bin(2048)]

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_not_neg(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, INT_ONE,
                        alu_no_move_opcode + alu_pass + a_address + unused_opcode,
                        jump_neg_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == dec_to_bin(5)

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_neg(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, INT_NEG_ONE,
                        alu_no_move_opcode + alu_pass + a_address + unused_opcode,
                        jump_neg_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address


class TestCPUJumpOverflow(TestCPU):
    addresses = [dec_to_bin(1024), dec_to_bin(2048)]

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_not_neg(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, INT_ONE,
                        alu_no_move_opcode + alu_add + a_address + a_address,
                        jump_overflow_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == dec_to_bin(5)

    @pytest.mark.parametrize('address', addresses)
    def test_jump_to_constant_overflow(self, cpu, address):
        instructions = [move_opcode + a_address + constant_address, INT_NEG_ONE,
                        alu_no_move_opcode + alu_add + a_address + a_address,
                        jump_overflow_opcode + unused_opcode + constant_address, address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == address


class TestCPUReset(TestCPU):
    def test_hardware_reset(self, cpu):
        instructions = [move_opcode + a_address + constant_address, INT_ONE]
        self.load_instructions(cpu.ram, instructions)

        assert cpu(reset=1) == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == ZEROS

    def test_software_reset(self, cpu):
        instructions = [reset_opcode]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc(UNUSED, 0, 0, 0) == ZEROS


class TestCPUShutdown(TestCPU):
    def test_shutdown(self, cpu):
        instructions = [shutdown_opcode]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 1


class TestCPUHDD(TestCPU):
    @staticmethod
    def make_hdd():
        hdd = HardDisk()
        data = ZEROS + INT_NEG_ONE + INT_ONE + INT_TWO
        data += bitarray(512 - 4*16)
        data += INT_THREE + INT_TWO + INT_ONE
        hdd.data = data
        return hdd

    hdd_sector_0 = [(ZEROS, ZEROS),
                    (INT_ONE, INT_NEG_ONE),
                    (INT_TWO, INT_ONE),
                    (INT_THREE, INT_TWO)]

    @pytest.mark.parametrize('hdd_address, expected', hdd_sector_0)
    def test_hdd_read(self, cpu, hdd_address, expected):
        instructions = [hdd_opcode + hdd_read + a_address + constant_address, hdd_address]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == expected

    def test_hdd_read_twice(self, cpu):
        hdd_address_1 = self.hdd_sector_0[0][0]
        hdd_address_2 = self.hdd_sector_0[1][0]
        expected_1 = self.hdd_sector_0[0][1]
        expected_2 = self.hdd_sector_0[1][1]

        instructions = [hdd_opcode + hdd_read + a_address + constant_address, hdd_address_1,
                        hdd_opcode + hdd_read + b_address + constant_address, hdd_address_2]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == expected_1
        assert cpu.b.value == expected_2

    hdd_sector_1 = [(ZEROS, INT_THREE),
                    (INT_ONE, INT_TWO),
                    (INT_TWO, INT_ONE)]

    @pytest.mark.parametrize('hdd_address, expected', hdd_sector_1)
    def test_set_sector(self, cpu, hdd_address, expected):
        sector_address = INT_ONE
        instructions = [hdd_opcode + hdd_set_sector + unused_opcode + constant_address, sector_address,
                        hdd_opcode + hdd_read + a_address + constant_address, hdd_address]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == expected

    def test_hdd_write_sector_0(self, cpu):
        value_1 = dec_to_bin(234)
        value_2 = dec_to_bin(52)
        hdd_address_1 = ZEROS
        hdd_address_2 = INT_ONE
        instructions = [move_opcode + a_address + constant_address, hdd_address_1,
                        hdd_opcode + hdd_write + a_address + constant_address, value_1,
                        move_opcode + a_address + constant_address, hdd_address_2,
                        hdd_opcode + hdd_write + a_address + constant_address, value_2
                        ]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.hdd.data[:16] == value_1

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.hdd.data[:16] == value_1
        assert cpu.hdd.data[16:32] == value_2

    def test_hdd_write_sector_1(self, cpu):
        value_1 = dec_to_bin(453)
        value_2 = dec_to_bin(531)
        hdd_address_1 = ZEROS
        hdd_address_2 = INT_ONE
        instructions = [hdd_opcode + hdd_set_sector + unused_opcode + constant_address, INT_ONE,
                        move_opcode + a_address + constant_address, hdd_address_1,
                        hdd_opcode + hdd_write + a_address + constant_address, value_1,
                        move_opcode + a_address + constant_address, hdd_address_2,
                        hdd_opcode + hdd_write + a_address + constant_address, value_2
                        ]
        self.load_instructions(cpu.ram, instructions)

        assert cpu() == 0
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.hdd.data[512:512+16] == value_1

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.hdd.data[512:512+16] == value_1
        assert cpu.hdd.data[512+16:512+32] == value_2


class TestCpuCallReturn(TestCPU):
    def test_call_register(self, cpu):
        stack_frame = dec_to_bin(1024)
        function_address = dec_to_bin(52)
        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        move_opcode + a_address + constant_address, function_address,
                        call_opcode + spp_address + a_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc.register.value == function_address
        assert cpu.ram_bus(UNUSED, stack_frame, 0) == dec_to_bin(5)
        assert cpu.sp.value == dec_to_bin(1023)

    def test_call_constant(self, cpu):
        stack_frame = dec_to_bin(1024)
        function_address = dec_to_bin(52)
        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        call_opcode + spp_address + constant_address, function_address]
        self.load_instructions(cpu.ram, instructions)

        cpu()
        cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.pc.register.value == function_address
        assert cpu.ram_bus(UNUSED, stack_frame, 0) == dec_to_bin(4)
        assert cpu.sp.value == dec_to_bin(1023)

    def test_return(self, cpu):
        stack_frame = dec_to_bin(1024)
        function = dec_to_bin(8)
        instructions = [move_opcode + sp_address + constant_address, stack_frame,
                        call_opcode + spp_address + constant_address, function,
                        shutdown_opcode,
                        shutdown_opcode,
                        shutdown_opcode,
                        shutdown_opcode,
                        move_opcode + a_address + constant_address, dec_to_bin(10),
                        return_opcode + unused_opcode + spp_address]
        self.load_instructions(cpu.ram, instructions)

        for _ in range(3):
            cpu()
            cpu.tick()

        assert cpu() == 0
        cpu.tick()

        assert cpu.a.value == dec_to_bin(10)
        assert cpu.pc.register.value == dec_to_bin(4)
        assert cpu.sp.value == dec_to_bin(1024)
