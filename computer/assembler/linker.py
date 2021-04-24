from computer.opcodes import *
from computer.assembler.tokens import Token
from computer.utility.numbers import dec_to_bin


def link(instructions, labels, variables, mode='loadable'):
    """
    :param instructions:
    :param labels:
    :param variables:
    :param mode: boot, loadable, (library)
    :return:
    """

    relative_locations = update_relative_locations(instructions, labels, variables, mode)

    if mode == 'loadable':
        loader = make_loader(relative_locations) if labels or variables else []
        header = make_header(len(loader + instructions), sum(variables.values()))
        instructions = header + loader + instructions
    return instructions


def update_relative_locations(instructions, labels, variables, mode):
    access_locations = []

    header_size = 2 if mode == 'loadable' else 0
    loader_size = 1 + 2*(len(variables)+len(labels)) if mode == 'loadable' else 0
    free_memory = header_size + loader_size + len(instructions) - 1

    for i, instruction in enumerate(instructions):
        if type(instruction) == Token:
            if instruction.value in labels:
                location = labels[instruction.value]
            else:
                var_size = variables[instruction.value]
                location = free_memory + 1
                free_memory += var_size
            instructions[i] = dec_to_bin(location)
            access_locations.append(i)
    return access_locations


def make_loader(relative_locations):
    loader = [pop_opcode + a_address + spp_address]
    header_size = 2
    offset = header_size + len(loader) + 2 * len(relative_locations)
    for access_location in relative_locations:
        loader.append(alu_opcode + alu_add + constantp_address + a_address)
        loader.append(dec_to_bin(access_location + offset))
    return loader


def make_header(num_instructions, allocated_memory):
    length_header = 2
    program_length = num_instructions + length_header
    program_length = dec_to_bin(program_length)
    allocated_space = dec_to_bin(allocated_memory)
    return [program_length, allocated_space]
