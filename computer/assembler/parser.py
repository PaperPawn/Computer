from computer.assembler.tokens import TokenKeyword, TokenDelimiter, TokenConstant, TokenLabel
from computer.opcodes import *

from computer.utility.numbers import dec_to_bin

system_commands = {TokenKeyword.Shutdown: shutdown_opcode,
                   TokenKeyword.Reset: reset_opcode}
two_address_commands = {TokenKeyword.Move: move_opcode,
                        TokenKeyword.Add: alu_opcode+alu_add,
                        TokenKeyword.Sub: alu_opcode+alu_sub,
                        TokenKeyword.And: alu_opcode+alu_and,
                        TokenKeyword.Or: alu_opcode+alu_or,
                        TokenKeyword.Xor: alu_opcode+alu_xor}
registers = {TokenKeyword.a: a_address,
             TokenKeyword.b: b_address,
             TokenKeyword.c: c_address,
             TokenKeyword.d: d_address,
             TokenKeyword.sp: sp_address}
pointer_registers = {TokenKeyword.a: ap_address,
                     TokenKeyword.b: bp_address,
                     TokenKeyword.c: cp_address,
                     TokenKeyword.d: dp_address,
                     TokenKeyword.sp: spp_address}


class Parser:
    def __init__(self):
        self.tokens = None

    def parse(self, tokens):
        instructions = []
        self.tokens = tokens
        while self.tokens:
            instruction = self.parse_next_instruction()
            instructions.extend(instruction)
        return instructions

    def parse_next_instruction(self):
        token = self.get_next_token()
        if token in two_address_commands:
            opcode = two_address_commands[token]
            instruction = self.parse_two_address_command(opcode)
        else:
            instruction = [system_commands[token]]
        return instruction

    def parse_two_address_command(self, opcode):
        address_1, value_1 = self.parse_address()
        address_2, value_2 = self.parse_address()
        instruction = [opcode + address_1 + address_2]
        if value_1 is not None:
            instruction.append(dec_to_bin(value_1))
        elif value_2 is not None:
            instruction.append(dec_to_bin(value_2))
        return instruction

    def parse_address(self):
        token = self.get_next_token()
        value = None
        if isinstance(token, TokenConstant):
            address = constant_address
            value = token.value
        elif token in registers:
            address = registers[token]
        elif token == TokenDelimiter.LeftBracket:
            address, value = self.parse_pointer(value)
        else:
            raise ParserError(f"Got unexpected token while parsing address.\n"
                              f"Expected 'constant', 'register' or '['\n"
                              f"Got: {token}")
        return address, value

    def parse_pointer(self, value):
        token = self.get_next_token()
        if isinstance(token, TokenConstant):
            address = constantp_address
            value = token.value
        else:
            address = pointer_registers[token]
        self.eat_token(TokenDelimiter.RightBracket)
        return address, value

    def eat_token(self, expected):
        token = self.get_next_token()
        if token != expected:
            raise ParserError(f"Expected {expected} got {token}")

    def get_next_token(self):
        return self.tokens.pop(0)


class ParserError(Exception):
    pass
