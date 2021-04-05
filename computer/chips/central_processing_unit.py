from bitarray import bitarray

from computer.chips.logic_gates import NOT, DMUX
from computer.chips.logic_gates_multi_way import MUX16, MUX4WAY16, DMUX4WAY
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

    instruction: aj(j/m)s oooo prrr prrr
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

    push: ajms xxxx prrr xxxx
        Stack operation: ajms = 0001
        push: s = 1
        Register address: prrr
        push value from prrr to stack

    pop: ajms xxxx prrr xxxx
        Stack operation: ajms = 0000
        pop: s = 0
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

    move: ajms xxxx prrr prrr
        Perform move operation: ajms = 0010, 4 bits
        Register adresses; prrrprrr, 8 bits
        move from 2nd to first prrr

    hdd: ajmd swxx prrr prrr
        Perform HDD operation ajmd = 0011, 4 bits
        Set sector: s, 1 bit
        Set write: w, 1 bit
        HDD address: first prrr
        Memory read/write: second prrr

    reset
    shutdown


    ajm(d/s)    operation
    0000        pop
    0001        push
    0010        move
    0011        hdd op
    0100        jump
    0101        (jump, push address?)
    0110        (jump)
    0111        (jump, push address?)
    1000        ALU op
    1001        (push ALU op)
    1010        (ALU op)
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

        self.pc = PC()

    def __call__(self):
        pc_value = self.pc(NULL_ADDRESS, 0, 0, 0)
        instruction = self.ram(NULL_ADDRESS, pc_value, 0)

        a_value = self.a(NULL_ADDRESS, 0)
        b_value = self.b(NULL_ADDRESS, 0)
        c_value = self.c(NULL_ADDRESS, 0)
        d_value = self.d(NULL_ADDRESS, 0)

        # MOVE
        # MOVE source
        source_address = instruction[12:]
        source_is_pointer = source_address[0]
        source_is_pc = source_address[1]

        # MOVE value
        register_value = MUX4WAY16(a_value, b_value, c_value, d_value, source_address[2:])
        constant_address = INC16(pc_value)

        memory_address = MUX16(register_value, constant_address, source_is_pc)
        memory_value = self.ram(NULL_ADDRESS, memory_address, 0)

        move_value = MUX16(register_value, memory_value, source_is_pointer)

        # MOVE target
        target_address = instruction[8:12]
        target_is_pointer = target_address[0]

        selected_target = DMUX(1, target_is_pointer)
        selected_register = DMUX4WAY(selected_target[0], target_address[2:])
        memory_address = MUX4WAY16(a_value, b_value, c_value, d_value, target_address[2:])

        # Load moved value
        self.ram(move_value, memory_address, selected_target[1])
        self.a(move_value, selected_register[0])
        self.b(move_value, selected_register[1])
        self.c(move_value, selected_register[2])
        self.d(move_value, selected_register[3])

        # Set PC
        next_pc_address = INC16(constant_address)
        select_pc_load = DMUX4WAY(1, source_address[:2])

        load = select_pc_load[3]
        inc = NOT(load)
        reset = 0
        self.pc(next_pc_address, load, inc, reset)
        return 0

    def tick(self):
        self.a.tick()
        self.b.tick()
        self.c.tick()
        self.d.tick()

        self.pc.tick()
