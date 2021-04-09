from bitarray import bitarray

from computer.chips.logic_gates import NOT, AND, MUX, DMUX
from computer.chips.logic_gates_16bit import NOT16
from computer.chips.logic_gates_multi_way import MUX16, MUX4WAY16, MUX8WAY16, DMUX4WAY, DMUX8WAY
from computer.chips.arithmetic import INC16
from computer.chips.memory import Register, PC

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
        call?

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

    jump: ajjs oooo prrr prrr
        jump: ajj = 01x, oooo = xxxx
        jump if zero: ajj = 110, oooo = ALU op
        jump if neg: ajj = 111, oooo = ALU op
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
    0000        (reset?)
    0001        (shutdown?)
    0010        move
    0011        stack op (push/pop) #hdd op
    0100        jump
    0101        (jump, push address?)
    0110        (jump)
    0111        (jump, push address?)
    1000        ALU op (no move?)
    1001        (push ALU op)
    1010        (ALU op) (with move?)
    1011        (ALU op)
    1100        jump if zero
    1101        (jump if zero, push zero?) (reset?)
    1110        jump if neg
    1111        (jump if neg, push neg number?) (shutdown)
    """

    def __init__(self, ram, hdd):
        self.ram = ram

        self.a = Register()
        self.b = Register()
        self.c = Register()
        self.d = Register()

        self.sp = Register()
        self.pc = PC()

    def __call__(self):
        pc_value = self.pc(NULL_ADDRESS, 0, 0, 0)
        instruction = self.ram_bus(NULL_ADDRESS, pc_value, 0)

        a_value = self.a(NULL_ADDRESS, 0)
        b_value = self.b(NULL_ADDRESS, 0)
        c_value = self.c(NULL_ADDRESS, 0)
        d_value = self.d(NULL_ADDRESS, 0)

        sp_value = self.sp(NULL_ADDRESS, 0)

        opcode = instruction[:4]
        secondary_opcode = instruction[4:8]

        is_pop = AND(opcode[3], secondary_opcode[0])
        sp_pop = INC16(sp_value)
        used_sp_value = MUX16(sp_value, sp_pop, is_pop)

        # MOVE
        # source value
        source_address = instruction[12:]

        constant_address = INC16(pc_value)
        register_value = MUX8WAY16(a_value, b_value, c_value, d_value,
                                   used_sp_value, constant_address, NULL_ADDRESS, NULL_ADDRESS,
                                   source_address[1:])

        memory_value = self.ram_bus(NULL_ADDRESS, register_value, 0)

        source_is_pointer = source_address[0]
        move_value = MUX16(register_value, memory_value, source_is_pointer)

        # target
        target_address = instruction[8:12]
        target_is_pointer = target_address[0]

        selected_target = DMUX(1, target_is_pointer)
        selected_register = DMUX8WAY(selected_target[0], target_address[1:])
        memory_address = MUX8WAY16(a_value, b_value, c_value, d_value,
                                   sp_value, NULL_ADDRESS, NULL_ADDRESS, NULL_ADDRESS,
                                   target_address[1:])

        # Load moved value
        self.ram_bus(move_value, memory_address, selected_target[1])
        self.a(move_value, selected_register[0])
        self.b(move_value, selected_register[1])
        self.c(move_value, selected_register[2])
        self.d(move_value, selected_register[3])

        # Update stack pointer
        sp_push = NOT16(INC16(NOT16(sp_value)))
        updated_sp = MUX16(sp_push, sp_pop, secondary_opcode[0])
        new_sp_value = MUX16(move_value, updated_sp, opcode[3])
        load_sp = MUX(selected_register[4], 1, opcode[3])
        self.sp(new_sp_value, load_sp)

        # Set PC
        next_pc_address = INC16(constant_address)
        select_pc_load = DMUX4WAY(1, source_address[:2])
        load = AND(select_pc_load[3], source_address[3])
        inc = NOT(load)
        reset = 0
        self.pc(next_pc_address, load, inc, reset)
        return 0

    def ram_bus(self, value, address, load):
        return self.ram(value, address[1:], load)

    def tick(self):
        self.a.tick()
        self.b.tick()
        self.c.tick()
        self.d.tick()

        self.sp.tick()
        self.pc.tick()

        self.ram.tick()
