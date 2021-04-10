from bitarray import bitarray

from computer.chips.central_processing_unit import CPU
from computer.chips.memory import RAM32K
from computer.io.harddisk import HardDisk
# from computer.io.screen import Screen

from computer.opcodes import *

from computer.utility.numbers import bin_to_dec, dec_to_bin

NULL = bitarray(16)


def get_bootloader():
    program_start = dec_to_bin(14)
    start_of_loop = dec_to_bin(6)
    instructions = [move_opcode + a_address + pc_address,
                    program_start,
                    move_opcode + b_address + pc_address,
                    dec_to_bin(0),
                    # Read length of binary
                    hdd_opcode + hdd_read + c_address + b_address,
                    alu_opcode + alu_inc + b_address + unused_opcode,
                    # Start of loop
                    hdd_opcode + hdd_read + ap_address + b_address,
                    alu_opcode + alu_inc + a_address + unused_opcode,
                    alu_opcode + alu_inc + b_address + unused_opcode,
                    # Check if entire binary is loaded
                    alu_no_move_opcode + alu_sub + c_address + b_address,
                    # Jump to program start if so
                    jump_zero_opcode + unused_opcode + pc_address,
                    program_start,
                    # If not jump back to start of loop
                    jump_opcode + unused_opcode + pc_address,
                    start_of_loop,
                    ]
    return instructions


def load_instructions(ram, instructions):
    for i, instruction in enumerate(instructions):
        address = dec_to_bin(i)
        ram(instruction, address[1:], 1)
    ram.tick()


def decode_instruction(instruction):
    opcode_1 = instruction[:4]
    opcode_2 = instruction[4:8]
    address_1 = instruction[8:12]
    address_2 = instruction[12:]

    return f'{decode_opcode(opcode_1, opcode_2)} {decode_address(address_1)} {decode_address(address_2)}'


def decode_opcode(opcode_1, opcode_2):
    if opcode_1 + opcode_2 == move_opcode:
        return 'move'
    elif opcode_1 == alu_opcode:
        if opcode_2 == alu_inc:
            return 'inc'
    elif opcode_1 == alu_no_move_opcode:
        if opcode_2 == alu_sub:
            return 'cmp'
    elif opcode_1 + opcode_2 == jump_opcode:
        return 'jump'
    elif opcode_1 + opcode_2 == jump_zero_opcode:
        return 'jumpzero'
    elif opcode_1 == hdd_opcode:
        if opcode_2 == hdd_read:
            return 'hddread'
    else:
        return f'Unable to decode opcode: {opcode_1+opcode_2}'


def decode_address(address):
    if address == a_address:
        return 'a'
    elif address == b_address:
        return 'b'
    elif address == c_address:
        return 'c'
    elif address == d_address:
        return 'd'
    elif address == sp_address:
        return 'sp'
    elif address == pc_address:
        return 'constant'
    elif address == ap_address:
        return '[a]'
    elif address == bp_address:
        return '[b]'
    elif address == cp_address:
        return '[c]'
    elif address == dp_address:
        return '[d]'
    elif address == spp_address:
        return '[sp]'
    elif address == pcp_address:
        return '[constant]'
    return f'Unable to decode address: {address}'


def print_status(cpu):
    pc = cpu.pc.register.value
    instruction = cpu.ram_bus(NULL, pc, 0)
    decoded = decode_instruction(instruction)
    status = f"""CPU status:
PC: {pc}, {bin_to_dec(pc)}
INSTRUCTION: {instruction}
{decoded}

A: {cpu.a.value}, {bin_to_dec(cpu.a.value)}
B: {cpu.b.value}, {bin_to_dec(cpu.b.value)}
C: {cpu.c.value}, {bin_to_dec(cpu.c.value)}
D: {cpu.d.value}, {bin_to_dec(cpu.d.value)}

SP: {cpu.sp.value}, {bin_to_dec(cpu.sp.value)}
"""
    print(status)


def main():
    ram = RAM32K()

    bootloader = get_bootloader()
    load_instructions(ram, bootloader)

    hdd = HardDisk()
    data = bitarray(512 * 10)
    data[:16] = dec_to_bin(4)
    data[16:32] = move_opcode + d_address + pc_address
    data[32:48] = dec_to_bin(52)
    data[48:64] = shutdown_opcode
    hdd.data = data

    cpu = CPU(ram, hdd)

    shutdown = False
    while not shutdown:
        print_status(cpu)
        shutdown = cpu()
        cpu.tick()

    print(cpu.ram_bus(NULL, dec_to_bin(14), 0))
    print(cpu.ram_bus(NULL, dec_to_bin(15), 0))
    print(cpu.ram_bus(NULL, dec_to_bin(16), 0))
    print(cpu.ram_bus(NULL, dec_to_bin(17), 0))
    print('Emulation completed')


if __name__ == '__main__':
    main()
