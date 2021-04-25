from bitarray import bitarray
from computer.assembler.lexer import Lexer, LexerError
from computer.assembler.parser import Parser, ParserError
from computer.assembler.linker import link

from computer.utility.numbers import bin_to_dec
from computer.utility.status import decode_instruction


def main():
    file_name = 'draw_square'
    # file_name = 'test'
    # file_name = 'bootloader'
    in_file_path = f'{file_name}.eas'
    out_file_path = f'{file_name}.bin'

    lexer = Lexer()
    parser = Parser()

    print(f'>> Building: {in_file_path}')
    print('>> Scanning file')
    with open(in_file_path, 'r') as file:
        tokens = []
        for line in file:
            tokens.extend(lexer.scan(line))

    print('>> Parsing')
    instructions = parser.parse(tokens)
    # print(instructions)
    print('>> Linking')
    instructions = link(instructions, parser.labels, parser.variables) #, mode='boot')
    # print(instructions)
    print(f'>> Building binary: {out_file_path}')
    binary = bitarray()
    # old_decoded = ''
    for instruction in instructions:
        # decoded = decode_instruction(instruction)
        # if 'constant' in old_decoded:
        #     print(bin_to_dec(instruction))
        # else:
        #     print(decoded)
        # old_decoded = decoded
        binary += instruction

    with open(out_file_path, 'wb') as file:
        binary.tofile(file)
    print('>> done')


if __name__ == '__main__':
    try:
        main()
    except (LexerError, ParserError) as e:
        print(f'{type(e)}: {e}')
