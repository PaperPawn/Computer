from bitarray import bitarray

from computer.chips.arithmetic import INC16
from computer.opcodes import *
from computer.utility.numbers import bin_to_dec, dec_to_bin
from computer.assembler.parser import (no_address_commands, two_address_commands,
                                       target_address_commands, source_address_commands)

NULL = bitarray(16)


def get_instruction(cpu):
    pc = cpu.pc.register.value
    instruction = cpu.ram_bus(NULL, pc, 0)
    decoded = decode_instruction(instruction)

    if 'constant' in decoded:
        pc, _ = INC16(pc)
        constant = cpu.ram_bus(NULL, pc, 0)
        constant = bin_to_dec(constant)
        decoded = decoded.replace('constant', str(constant))

    return instruction, decoded


def decode_instruction(instruction):
    for token in no_address_commands:
        if instruction == no_address_commands[token]:
            return token.value

    command = instruction[:8]
    address_1 = instruction[8:12]
    address_2 = instruction[12:]
    decoded_address_1 = decode_address(address_1)
    decoded_address_2 = decode_address(address_2)

    for token in two_address_commands:
        if command == two_address_commands[token]:
            return f'{token.value} {decoded_address_1} {decoded_address_2}'

    for token in target_address_commands:
        if command == target_address_commands[token]:
            return f'{token.value} {decoded_address_1}'

    for token in source_address_commands:
        if command == source_address_commands[token]:
            return f'{token.value} {decoded_address_2}'
    return f'Can\'t decode instruction {instruction}'


def _decode_instruction(instruction):
    opcode_1 = instruction[:4]
    opcode_2 = instruction[4:8]
    address_1 = instruction[8:12]
    address_2 = instruction[12:]

    decoded_address_1 = decode_address(address_1)
    decoded_address_2 = decode_address(address_2)
    addresses = f'{decoded_address_1} {decoded_address_2}'
    command = f'Unable to decode opcode: {opcode_1 + opcode_2}'
    if instruction == reset_opcode:
        command = 'reset'
        addresses = ''
    elif instruction == shutdown_opcode:
        command = 'shutdown'
        addresses = ''
    elif opcode_1 + opcode_2 == move_opcode:
        command = 'move'
    elif opcode_1 == alu_opcode:
        if opcode_2 == alu_inc:
            command = 'inc'
            addresses = decoded_address_1
    elif opcode_1 == alu_no_move_opcode:
        if opcode_2 == alu_sub:
            command = 'cmp'
    elif opcode_1 + opcode_2 == jump_opcode:
        command = 'jump'
        addresses = decoded_address_2
    elif opcode_1 + opcode_2 == jump_zero_opcode:
        command = 'jumpzero'
        addresses = decoded_address_2
    elif opcode_1 == hdd_opcode:
        if opcode_2 == hdd_read:
            command = 'hddread'
    return f'{command} {addresses}'


def decode_address(address):
    if address[1:] == a_address[1:]:
        value = 'a'
    elif address[1:] == b_address[1:]:
        value = 'b'
    elif address[1:] == c_address[1:]:
        value = 'c'
    elif address[1:] == d_address[1:]:
        value = 'd'
    elif address[1:] == sp_address[1:]:
        value = 'sp'
    elif address[1:] == constant_address[1:]:
        value = 'constant'
    else:
        return f'Unable to decode address: {address}'
    if address[0]:
        value = f'[{value}]'
    return value


def print_status(cpu):
    instruction, decoded = get_instruction(cpu)
    status = f"""CPU status:
PC: {cpu.pc.register.value}, {bin_to_dec(cpu.pc.register.value)}\t--> {cpu.pc.register.next_value}, {bin_to_dec(cpu.pc.register.next_value)}
INSTRUCTION: {instruction}
{decoded}

A: {cpu.a.value}, {bin_to_dec(cpu.a.value)}\t--> {cpu.a.next_value}, {bin_to_dec(cpu.a.next_value)}
B: {cpu.b.value}, {bin_to_dec(cpu.b.value)}\t--> {cpu.b.next_value}, {bin_to_dec(cpu.b.next_value)}
C: {cpu.c.value}, {bin_to_dec(cpu.c.value)}\t--> {cpu.c.next_value}, {bin_to_dec(cpu.c.next_value)}
D: {cpu.d.value}, {bin_to_dec(cpu.d.value)}\t--> {cpu.d.next_value}, {bin_to_dec(cpu.d.next_value)}

SP: {cpu.sp.value}, {bin_to_dec(cpu.sp.value)}\t--> {cpu.sp.next_value}, {bin_to_dec(cpu.sp.next_value)}

=============================================================================================================
"""
    print(status)
