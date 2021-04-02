class CPU:
    """
    Registers:
    m - memory loader
    a, b, c, d - general purpose
    sp - stack pointer
    pc - program counter

    Data buses:
    RAM
    Hard Drive

    Instruction: 16bit
    load instruction: 0xxx xxxx xxxx xxxx
        load 15bit number into register m

    opcode instruction: 1aj(j/m) (s/o)(ooo) prrr prrrr
        CPU opcode: ? bits
        push
        pop
        arithmetic (add, sub, neg...): a, 1 bit
        jump
        jump if zero
        jump if neg
        move

    Register address: prrr 4 bits
        Value or pointer: p, 1 bit
        Select register: rrr, 3 bits

    push: lajm sxxx prrr xxxx
        Stack operation: lajm = 1000
        push: s = 1
        Register address: prrr
        push value from prrr to stack

    pop: lajm sxxx prrr xxxx
        Stack operation: lajm = 1000
        pop: s = 0
        Register address: prrr
        pop value from stack to prrr

    arithmetic: lajj oooo prrr prrr, 16 bits
        Perform ALU operation: lajj = 1100, 4 bits
        ALU opcode: oooo, 4 bits
        Register adresses; prrrprrr, 8 bits
        Outputs to second register

    jump: lajj oooo prrr xxxx
        l=1, 1 bit
        jump: ajj = 01x, oooo = xxxx
        jump if zero: ajj = 110, oooo = 0000 (pass)
        jump if neg: ajj = 111, oooo = 0001 (neg)

        jump to prrr

    move: lajm xxxx prrr prrr
        Perform move operation: lajm = 1001, 4 bits
        Register adresses; prrrprrr, 8 bits
    """
    pass