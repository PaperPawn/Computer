from bitarray import bitarray

from computer.chips.logic_gates import NOT, AND, OR, MUX, DMUX
from computer.chips.logic_gates_16bit import NOT16
from computer.chips.logic_gates_multi_way import OR8WAY, MUX16, MUX4WAY16, MUX8WAY16, DMUX4WAY, DMUX8WAY
from computer.chips.arithmetic import INC16
from computer.chips.arithmetic_logic_unit import ALU
from computer.chips.memory import Register, PC

ZERO_ADDRESS = bitarray('0'*16)
NULL_ADDRESS = bitarray(16)


class CPU:
    """
    Registers:
    a, b, c, d - general purpose
    sp - stack pointer
    pc - program counter

    Data buses:
    RAM
    Hard Drive

    Instruction: 16bit

    instruction: oooo aaaa prrr prrr
        push
        pop
        arithmetic (add, sub, neg...):
        jump
        jump if zero
        jump if neg
        move
        hdd op
        reset
        shutdown

    Register address: prrr 4 bits
        Value (0) or pointer (1): p, 1 bit
        Select register: rrr, 3 bits

        a - 000
        b - 001
        c - 010
        d - 011
        sp - 1x0
        pc - 1x1

        When move from 1101 (pc pointer) read from pc+1 and update pc=pc+2 at tick

    push: ajms oxxx 1100 prrr
        Stack operation: ajms = 0001
        push: s = 1, o = 0
        Register address: prrr
        push value from prrr to stack

    pop: ajms oxxx prrr 1100
        Stack operation: ajms = 0000
        pop: s = 1, o = 1
        Register address: prrr
        pop value from stack to prrr

    arithmetic: ajms oooo prrr prrr, 16 bits
        Perform ALU operation: ajms = 1000, 4 bits
        ALU opcode: oooo, 4 bits
        Register adresses; prrrprrr, 8 bits
        Outputs to second register

    jump: ajjs xxxx xxxx prrr
        jump: ajj = 01x, oooo = xxxx
        jump if zero: ajj = 110
        jump if negative: ajj = 101
        jump if overflow: ajj = 111
        jump to prrr

    move: ajms oooo prrr prrr
        Perform move operation: ajms = 0010, 4 bits
        Move opcode: oooo = 0000
        Register adresses; prrrprrr, 8 bits
        move from 2nd to first prrr

    hdd: ajmd hswx prrr prrr
        Perform Move operation ajmd = 0010, 4 bits
        Move opcode: oooo = 1swx
        Set sector: s, 1 bit
        Set write: w, 1 bit
        HDD address: first prrr
        Memory read/write: second prrr

    reset
    shutdown

    opcode      operation
    0000        reset
    0001        shutdown
    0010        move (possible hdd op)
    0011        stack op (push/pop)
    0100        jump
    0101        jump if neg
    0110        jump if zero
    0111        jump if overflow
    1000        (ALU op, no move)
    1001        (ALU op, no move)
    1010        ALU op, with move
    1011        (ALU op, to stack?)
    1100        (ALU op, with jump?)
    1101        (ALU op, with jump?)
    1110        (ALU op, with move)
    1111        (ALU op, to stack?)
    """

    def __init__(self, ram, hdd):
        self.ram = ram
        self.hdd = hdd

        self.a = Register()
        self.b = Register()
        self.c = Register()
        self.d = Register()

        self.sp = Register()
        self.pc = PC()

        self.status = Register()

    def __call__(self, reset=0):
        pc_value = self.pc(NULL_ADDRESS, 0, 0, 0)
        instruction = self.ram_bus(NULL_ADDRESS, pc_value, 0)

        a_value = self.a(NULL_ADDRESS, 0)
        b_value = self.b(NULL_ADDRESS, 0)
        c_value = self.c(NULL_ADDRESS, 0)
        d_value = self.d(NULL_ADDRESS, 0)

        sp_value = self.sp(NULL_ADDRESS, 0)

        constant_address, _ = INC16(pc_value)
        constant_value = self.ram_bus(NULL_ADDRESS, constant_address, 0)

        opcode = instruction[:4]
        secondary_opcode = instruction[4:8]

        is_pop = AND(opcode[3], secondary_opcode[0])
        sp_pop, _ = INC16(sp_value)
        used_sp_value = MUX16(sp_value, sp_pop, is_pop)

        # source value
        source_address = instruction[12:]

        source_register_value = MUX8WAY16(a_value, b_value, c_value, d_value,
                                          used_sp_value, constant_value, NULL_ADDRESS, NULL_ADDRESS,
                                          source_address[1:])

        source_memory_value = self.ram_bus(NULL_ADDRESS, source_register_value, 0)

        source_is_pointer = source_address[0]
        source_value = MUX16(source_register_value, source_memory_value, source_is_pointer)

        # target
        target_address = instruction[8:12]
        target_is_pointer = target_address[0]

        target_register_value = MUX8WAY16(a_value, b_value, c_value, d_value,
                                          sp_value, constant_value, NULL_ADDRESS, NULL_ADDRESS,
                                          target_address[1:])
        target_memory_value = self.ram_bus(NULL_ADDRESS, target_register_value, 0)
        target_value = MUX16(target_register_value, target_memory_value, target_is_pointer)

        # HDD op
        is_hdd = AND(NOT(OR(opcode[0], opcode[3])),
                     AND(opcode[2], secondary_opcode[0]))
        # print()
        # print(f'secondary_opcode: {secondary_opcode}')
        hdd_write = AND(is_hdd, secondary_opcode[2])
        hdd_read = NOT(hdd_write)

        hdd_address = MUX16(source_value, target_value, hdd_write)
        hdd_address = MUX16(ZERO_ADDRESS, hdd_address, is_hdd)
        # hdd_address = source_value
        hdd_set_sector = AND(is_hdd, secondary_opcode[1])
        # hdd_value = MUX16(NULL_ADDRESS, source_value, secondary_opcode[2])
        hdd_value = source_value
        hdd_out = self.hdd(hdd_address, hdd_set_sector, hdd_value, hdd_write)

        # ALU op
        alu_result, is_zero, is_neg, overflow = ALU(target_value, source_value, secondary_opcode)
        result_source_alu = MUX16(source_value, alu_result, opcode[0])
        result = MUX16(result_source_alu, hdd_out, is_hdd)

        status = bitarray('0'*16)
        status[0] = is_zero
        status[1] = is_neg
        status[2] = overflow
        self.status(status, opcode[0])

        selected_target = DMUX(1, target_is_pointer)
        selected_register = DMUX8WAY(selected_target[0], target_address[1:])
        memory_address = MUX8WAY16(a_value, b_value, c_value, d_value,
                                   sp_value, constant_value, NULL_ADDRESS, NULL_ADDRESS,
                                   target_address[1:])

        # Load moved value
        load = opcode[2]
        self.ram_bus(result, memory_address, AND(selected_target[1], load))
        self.a(result, AND(selected_register[0], load))
        self.b(result, AND(selected_register[1], load))
        self.c(result, AND(selected_register[2], load))
        self.d(result, AND(selected_register[3], load))

        # Update stack pointer
        sp_push, _ = INC16(NOT16(sp_value))
        sp_push = NOT16(sp_push)
        updated_sp = MUX16(sp_push, sp_pop, secondary_opcode[0])
        new_sp_value = MUX16(result, updated_sp, opcode[3])
        load_sp = MUX(selected_register[4], 1, opcode[3])
        self.sp(new_sp_value, load_sp)

        # Set PC
        status = self.status(NULL_ADDRESS, 0)

        jump_setting = DMUX4WAY(opcode[1], opcode[2:4])
        do_jump = OR(OR(jump_setting[0],  # jump
                        AND(jump_setting[1], status[1]),  # jump neg
                        ),
                     OR(AND(jump_setting[2], status[0]),  # jump zero
                        AND(jump_setting[3], status[2])   # jump overflow
                        )
                     )

        inc_pc_address, _ = INC16(constant_address)
        next_pc_address = MUX16(inc_pc_address, result, do_jump)

        load = OR(OR(AND(source_address[1], source_address[3]),
                     AND(target_address[1], target_address[3])),
                  do_jump)
        inc = NOT(load)
        reset = OR(reset, NOT(OR(OR(opcode[0], opcode[1]), OR(opcode[2], opcode[3]))))
        self.pc(next_pc_address, load, inc, reset)
        shutdown = NOT(OR(OR(opcode[0], opcode[1]), OR(opcode[2], NOT(opcode[3]))))
        return shutdown

    def ram_bus(self, value, address, load):
        return self.ram(value, address[1:], load)

    def tick(self):
        self.a.tick()
        self.b.tick()
        self.c.tick()
        self.d.tick()

        self.sp.tick()
        self.pc.tick()

        self.status.tick()

        self.ram.tick()
        self.hdd.tick()
