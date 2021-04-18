from computer.assembler.tokens import (TokenKeyword, TokenDelimiter,
                                       TokenLiteral, TokenName)
from computer.opcodes import *

from computer.utility.numbers import dec_to_bin

no_address_commands = {TokenKeyword.Shutdown: shutdown_opcode,
                       TokenKeyword.Reset: reset_opcode,
                       TokenKeyword.Return: return_opcode+unused_opcode+spp_address}
two_address_commands = {TokenKeyword.Move: move_opcode,
                        TokenKeyword.Add: alu_opcode+alu_add,
                        TokenKeyword.Sub: alu_opcode+alu_sub,
                        TokenKeyword.And: alu_opcode+alu_and,
                        TokenKeyword.Or: alu_opcode+alu_or,
                        TokenKeyword.Xor: alu_opcode+alu_xor,
                        TokenKeyword.Compare: alu_no_move_opcode+alu_sub,
                        TokenKeyword.HddWrite: hdd_opcode+hdd_write,
                        TokenKeyword.HddRead: hdd_opcode+hdd_read}
target_address_commands = {TokenKeyword.Inc: alu_opcode+alu_inc,
                           TokenKeyword.Dec: alu_opcode+alu_dec,
                           TokenKeyword.Negate: alu_opcode+alu_neg,
                           TokenKeyword.Not: alu_opcode+alu_not,
                           TokenKeyword.Pop: pop_opcode}
source_address_commands = {TokenKeyword.Jump: jump_opcode,
                           TokenKeyword.JumpIfZero: jump_zero_opcode,
                           TokenKeyword.JumpIfNeg: jump_neg_opcode,
                           TokenKeyword.JumpIfOverflow: jump_overflow_opcode,
                           TokenKeyword.HddSector: hdd_opcode+hdd_set_sector,
                           TokenKeyword.Push: push_opcode,
                           TokenKeyword.Call: call_opcode}
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
    def __init__(self, debug=False):
        self.tokens = None
        self.labels = {}
        self.instructions = []
        self.debug = debug

    def parse(self, tokens, link=True):
        self.tokens = tokens
        while self.tokens:
            instruction = self.parse_next_instruction()
            if self.debug:
                print(instruction)
            self.instructions.extend(instruction)
        if link:
            self.link_labels()
        return self.instructions

    def link_labels(self):
        for i, instruction in enumerate(self.instructions):
            if type(instruction) == str:
                self.instructions[i] = self.labels[instruction]

    def parse_next_instruction(self):
        token = self.get_next_token()
        if token == TokenDelimiter.Colon:
            self.parse_label()
            token = self.get_next_token()

        if token in two_address_commands:
            instruction = self.parse_two_address_command(token)
        elif token in target_address_commands:
            instruction = self.parse_target_address_command(token)
        elif token in source_address_commands:
            instruction = self.parse_source_address_command(token)
        elif token in no_address_commands:
            instruction = self.parse_no_address_command(token)
        else:
            raise ParserError(f"Expected a valid command.\nGot: '{token.value}'.")
        return instruction

    def parse_label(self):
        self.eat_token(TokenName.Label)
        label = self.get_next_token()
        if type(label) != str:
            raise ParserError(f'{TokenName.Label} must be followed by a name.\n'
                              f"Got: '{label}'")
        self.labels[label] = dec_to_bin(len(self.instructions))

    def parse_two_address_command(self, token):
        opcode = two_address_commands[token]
        address_1, value_1 = self.parse_address()
        address_2, value_2 = self.parse_address()
        instruction = [opcode + address_1 + address_2]
        if value_1 is not None:
            instruction.append(value_1)
        elif value_2 is not None:
            instruction.append(value_2)
        return instruction

    def parse_target_address_command(self, token):
        opcode = target_address_commands[token]
        address_1, value = self.parse_address()
        if value is not None:
            raise ParserError(f"Command '{token.value}'' does not accept constants.\n"
                              f"Got: '{value}'.")
        address_2 = spp_address if token == TokenKeyword.Pop else unused_opcode
        return [opcode + address_1 + address_2]

    def parse_source_address_command(self, token):
        opcode = source_address_commands[token]
        address_1, value = self.parse_address()
        address_2 = spp_address if token in [TokenKeyword.Push, TokenKeyword.Call] else unused_opcode
        instruction = [opcode + address_2 + address_1]
        if value is not None:
            instruction.append(value)
        return instruction

    @staticmethod
    def parse_no_address_command(token):
        return [no_address_commands[token]]

    def parse_address(self):
        token = self.get_next_token()
        value = None
        is_pointer = False
        if token == TokenDelimiter.LeftBracket:
            is_pointer = True
            token = self.get_next_token()

        if token == TokenName.Label:
            value = self.get_next_token()
            address = constant_address
        elif token == TokenLiteral.Int:
            address = constantp_address if is_pointer else constant_address
            value = self.get_next_token()
            if type(value) != int:
                raise ParserError(f"Expected literal int value.\nGot '{value}'")
            value = dec_to_bin(value)
        elif token in registers:
            _registers = pointer_registers if is_pointer else registers
            address = _registers[token]
        else:
            raise ParserError(f"Got unexpected token while parsing address.\n"
                              f"Expected: constant, register or [.\n"
                              f"Got: '{token.value}'.")
        if is_pointer:
            self.eat_token(TokenDelimiter.RightBracket)
        return address, value

    def eat_token(self, expected):
        token = self.get_next_token()
        if token != expected:
            raise ParserError(f"Expected: {expected.value}\nGot {token.value}")

    def get_next_token(self):
        token = self.tokens.pop(0)
        if self.debug:
            print(token)
        return token


class ParserError(Exception):
    pass
