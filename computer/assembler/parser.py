from computer.assembler.tokens import TokenKeyword, TokenRegister, TokenDelimiter, TokenInt, TokenLabel
from computer.opcodes import *

from computer.utility.numbers import dec_to_bin

instruction_map = {TokenKeyword.Shutdown: shutdown_opcode,
                   TokenKeyword.Reset: reset_opcode}
registers = {TokenRegister.a: a_address,
             TokenRegister.b: b_address,
             TokenRegister.c: c_address,
             TokenRegister.d: d_address,
             TokenRegister.sp: sp_address}
pointer_registers = {TokenRegister.a: ap_address,
                     TokenRegister.b: bp_address,
                     TokenRegister.c: cp_address,
                     TokenRegister.d: dp_address,
                     TokenRegister.sp: spp_address,
                     }


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
        if token == TokenKeyword.Move:
            instruction = self.parse_move_command()
        else:
            instruction = [instruction_map[token]]
        return instruction

    def parse_move_command(self):
        address_1, value_1 = self.parse_address()
        address_2, value_2 = self.parse_address()
        instruction = [move_opcode + address_1 + address_2]
        if value_1 is not None:
            instruction.append(dec_to_bin(value_1))
        elif value_2 is not None:
            instruction.append(dec_to_bin(value_2))
        return instruction

    def parse_address(self):
        token = self.get_next_token()
        value = None
        if isinstance(token, TokenInt):
            address = constant_address
            value = token.value
        elif token in TokenRegister:
            address = registers[token]
        elif token == TokenDelimiter.LeftBracket:
            address, value = self.parse_pointer(value)
        else:
            raise ParserError(f"Got invalid token: {token} while parsing address.\n"
                              f"Expected {TokenInt}, {TokenRegister} or {TokenDelimiter.LeftBracket}")
        return address, value

    def parse_pointer(self, value):
        token = self.get_next_token()
        if isinstance(token, TokenInt):
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
