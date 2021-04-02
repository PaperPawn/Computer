class CPU:
    """
    Registers:
    # m - memory loader
    a, b, c, d - general purpose
    sp - stack pointer
    pc - program counter

    Data buses:
    RAM
    Hard Drive

    Instruction: 16bit
    # load instruction: 0xxx xxxx xxxx xxxx
    #      load 15bit number into register m

    # instruction: 1aj(j/m) (s/o)(ooo) prrr prrr
    instruction: aj(j/m)s oooo prrr prrr
        push
        pop
        arithmetic (add, sub, neg...):
        jump
        jump if zero
        jump if neg
        move
        hdd op
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

    # push: lajm sxxx prrr xxxx
    push: ajms xxxx prrr xxxx
        Stack operation: ajms = 0001
        push: s = 1
        Register address: prrr
        push value from prrr to stack

    # pop: lajm sxxx prrr xxxx
    pop: ajms xxxx prrr xxxx
        Stack operation: ajms = 0000
        pop: s = 0
        Register address: prrr
        pop value from stack to prrr

    # arithmetic: lajj oooo prrr prrr, 16 bits
    arithmetic: ajms oooo prrr prrr, 16 bits
        Perform ALU operation: ajms = 1000, 4 bits
        ALU opcode: oooo, 4 bits
        Register adresses; prrrprrr, 8 bits
        Outputs to second register

    # jump: lajj oooo prrr prrr
    jump: ajjs oooo prrr prrr
        jump: ajj = 01x, oooo = xxxx
        jump if zero: ajj = 110, oooo = ALU op
        jump if neg: ajj = 111, oooo = ALU op
        jump to prrr

    # move: lajm xxxx prrr prrr
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
    1101        (jump if zero, push zero?)
    1110        jump if neg
    1111        (jump if neg, push neg number?)
    """
    pass