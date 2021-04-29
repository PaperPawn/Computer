import os

from computer.chips.central_processing_unit import CPU
from computer.chips.optimized.memory import CombinedRAM
from computer.io.harddisk import HardDisk
# from computer.io.screen import Screen

from computer.opcodes import *

from computer.utility.numbers import bin_to_dec, dec_to_bin
from computer.utility.status import print_status


def get_bootloader():
    # program_start = dec_to_bin(14)
    # start_of_loop = dec_to_bin(6)
    # instructions = [move_opcode + a_address + constant_address,
    #                 program_start,
    #                 move_opcode + b_address + constant_address,
    #                 dec_to_bin(0),
    #                 # Read length of bootloader
    #                 hdd_opcode + hdd_read + c_address + b_address,
    #                 alu_opcode + alu_inc + b_address + unused_opcode,
    #                 # Start of loop
    #                 hdd_opcode + hdd_read + ap_address + b_address,
    #                 alu_opcode + alu_inc + a_address + unused_opcode,
    #                 alu_opcode + alu_inc + b_address + unused_opcode,
    #                 # Check if entire bootloader is loaded
    #                 alu_no_move_opcode + alu_sub + c_address + b_address,
    #                 # Jump to program start if so
    #                 jump_zero_opcode + unused_opcode + constant_address,
    #                 program_start,
    #                 # If not jump back to start of loop
    #                 jump_opcode + unused_opcode + constant_address,
    #                 start_of_loop,
    #                 ]
    path = r'D:\Programmering\python\computer\computer\assembler\bootloader.bin'
    bootloader = bitarray()
    with open(path, 'rb') as file:
        bootloader.fromfile(file)
    return bootloader


class Emulator:
    def __init__(self, cpu, verbose=False):
        self.cpu = cpu
        self.verbose = verbose
        self.shutdown = False

    def load_instructions(self, instructions):
        for i, instruction in enumerate(instructions):
            address = dec_to_bin(i)
            self.cpu.ram(instruction, address[1:], 1)
        self.cpu.ram.tick()

    def load_binary(self, binary):
        size = int(len(binary) / 16)
        for i in range(size):
            instruction = binary[i*16:(i+1)*16]
            address = dec_to_bin(i)
            self.cpu.ram(instruction, address, 1)
        self.cpu.ram.tick()

    def run(self):
        while not self.shutdown:
            self.tick()

    def tick(self):
        if not self.shutdown:
            self.shutdown = self.cpu()
            if self.verbose:
                print_status(self.cpu)
            self.cpu.tick()

    def reset(self):
        self.cpu(reset=1)
        self.shutdown = False
        self.cpu.tick()


def main():
    emulator = make_emulator(verbose=True)

    emulator.run()
    print('Emulation completed')


def make_emulator(binary_file, verbose=False):
    ram = CombinedRAM()
    hdd = get_hdd_with_loaded_program(binary_file)
    cpu = CPU(ram, hdd)
    emulator = Emulator(cpu, verbose)
    bootloader = get_bootloader()
    emulator.load_binary(bootloader)
    return emulator


def get_hdd_with_loaded_program(file_name='test.bin'):
    hdd = HardDisk()
    file_path = os.path.join(r'D:\Programmering\python\computer\computer\assembler',
                             file_name)
    hdd.load_data(file_path)
    return hdd


if __name__ == '__main__':
    main()
