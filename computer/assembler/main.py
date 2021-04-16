from computer.assembler.lexer import Lexer
from computer.assembler.parser import Parser
from computer.utility.numbers import dec_to_bin


def main():
    in_file_path = 'test.eas'
    out_file_path = 'test.bin'

    lexer = Lexer()
    parser = Parser()

    with open(in_file_path, 'r') as file:
        tokens = []
        for line in file:
            tokens.extend(lexer.scan(line))

    print(f'Tokens: {tokens}')
    instructions = parser.parse(tokens)
    print(f'Instructions: {instructions}')
    binary = dec_to_bin(len(instructions) + 1)
    for instruction in instructions:
        binary += instruction

    with open(out_file_path, 'wb') as file:
        binary.tofile(file)


if __name__ == '__main__':
    main()
