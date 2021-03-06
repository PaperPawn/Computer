from computer.assembler.tokens import (Token, Keyword, Delimiter,
                                       Literal, Label)
from computer.opcodes import *

from computer.utility.numbers import dec_to_bin

no_address_commands = {Keyword.Shutdown: shutdown_opcode,
                       Keyword.Reset: reset_opcode,
                       Keyword.Return: return_opcode + unused_opcode + spp_address}
two_address_commands = {Keyword.Move: move_opcode,
                        Keyword.Add: alu_opcode + alu_add,
                        Keyword.Sub: alu_opcode + alu_sub,
                        Keyword.And: alu_opcode + alu_and,
                        Keyword.Or: alu_opcode + alu_or,
                        Keyword.Xor: alu_opcode + alu_xor,
                        Keyword.Compare: alu_no_move_opcode + alu_sub,
                        Keyword.HddWrite: hdd_opcode + hdd_write,
                        Keyword.HddRead: hdd_opcode + hdd_read}
target_address_commands = {Keyword.Inc: alu_opcode + alu_inc,
                           Keyword.Dec: alu_opcode + alu_dec,
                           Keyword.Negate: alu_opcode + alu_neg,
                           Keyword.Not: alu_opcode + alu_not,
                           Keyword.Pop: pop_opcode}
source_address_commands = {Keyword.Jump: jump_opcode,
                           Keyword.JumpIfZero: jump_zero_opcode,
                           Keyword.JumpIfNeg: jump_neg_opcode,
                           Keyword.JumpIfOverflow: jump_overflow_opcode,
                           Keyword.HddSector: hdd_opcode + hdd_set_sector,
                           Keyword.Push: push_opcode,
                           Keyword.Call: call_opcode}
registers = {Keyword.a: a_address,
             Keyword.b: b_address,
             Keyword.c: c_address,
             Keyword.d: d_address,
             Keyword.sp: sp_address}
pointer_registers = {Keyword.a: ap_address,
                     Keyword.b: bp_address,
                     Keyword.c: cp_address,
                     Keyword.d: dp_address,
                     Keyword.sp: spp_address}


class Parser:
    def __init__(self, debug=False):
        self.tokens = None
        self.instructions = []
        self.debug = debug

        self.labels = {}
        self.variables = {}
        self.built_ins = {'KEYBOARD': 40960, 'SCREEN': 32768, 'BP': 32767}

    def parse(self, tokens):
        self.tokens = tokens
        while self.tokens:
            instruction = self.parse_next_instruction()
            if self.debug:
                print(instruction)
            self.instructions.extend(instruction)
        self.check_labels()
        return self.instructions

    def check_labels(self):
        for instruction in self.instructions:
            if type(instruction) == Token and instruction.value not in self.declared_labels:
                raise ParserError(f"Refering to undeclared label '{instruction.value}' in line {instruction.line}")

    @property
    def declared_labels(self):
        return list(self.labels) + list(self.variables) + list(self.built_ins)

    def parse_next_instruction(self):
        token = self.get_next_token()
        if token.type == Delimiter.Colon:
            self.parse_declare_label()
            return []

        if token.type == Keyword.Alloc:
            label = self.get_next_token(Label.Name)
            size = self.get_next_token(Literal.Int)
            if label.value in self.declared_labels:
                raise ParserError(f"Allocating to existing label '{label.value}' on line {token.line}")
            self.variables[label.value] = size.value
            return []

        if token.type in two_address_commands:
            instruction = self.parse_two_address_command(token)
        elif token.type in target_address_commands:
            instruction = self.parse_target_address_command(token)
        elif token.type in source_address_commands:
            instruction = self.parse_source_address_command(token)
        elif token.type in no_address_commands:
            instruction = self.parse_no_address_command(token)
        else:
            raise ParserError(f"Expected a valid command on line {token.line}.\nGot: '{token.value}'.")
        return instruction

    def parse_declare_label(self):
        token = self.get_next_token(Label.Name)
        label = token.value
        if label in self.declared_labels:
            raise ParserError(f"Declaring existing label '{label}' on line {token.line}")
        self.labels[label] = len(self.instructions)

    def parse_two_address_command(self, token):
        opcode = two_address_commands[token.type]
        address_1, value_1 = self.parse_address()
        address_2, value_2 = self.parse_address()
        instruction = [opcode + address_1 + address_2]
        self.add_literal_instruction(instruction, value_1, value_2)
        return instruction

    @staticmethod
    def add_literal_instruction(instruction, value_1, value_2):
        if value_1 is not None and value_2 is not None:
            raise ParserError('Can\'t move from literal/label to literal/label')
        elif value_1 is not None:
            instruction.append(value_1)
        elif value_2 is not None:
            instruction.append(value_2)

    def parse_target_address_command(self, token):
        opcode = target_address_commands[token.type]
        address_1, value = self.parse_address()
        if value is not None:
            raise ParserError(f"Command '{token.value}'' does not accept constants.\n"
                              f"Got: '{value}'.")
        address_2 = spp_address if token.type == Keyword.Pop else unused_opcode
        return [opcode + address_1 + address_2]

    def parse_source_address_command(self, token):
        opcode = source_address_commands[token.type]
        address_1, value = self.parse_address()
        address_2 = spp_address if token.type in [Keyword.Push, Keyword.Call] else unused_opcode
        instruction = [opcode + address_2 + address_1]
        if value is not None:
            instruction.append(value)
        return instruction

    @staticmethod
    def parse_no_address_command(token):
        return [no_address_commands[token.type]]

    def parse_address(self):
        if not self.tokens:
            raise ParserError('Expected an address. Got end of file.')
        token = self.get_next_token()
        value = None
        is_pointer = False
        if token.type == Delimiter.LeftBracket:
            is_pointer = True
            token = self.get_next_token()

        if token.type in [Label.Name, Literal.Int]:
            address = constantp_address if is_pointer else constant_address
            if token.type == Label.Name:
                if token.value in self.built_ins:
                    value = dec_to_bin(self.built_ins[token.value])
                else:
                    value = token
            if token.type == Literal.Int:
                if type(token.value) != int:
                    raise ParserError(f"Expected literal int value.\nGot '{token.value}'")
                value = dec_to_bin(token.value)
        elif token.type in registers:
            _registers = pointer_registers if is_pointer else registers
            address = _registers[token.type]
        else:
            raise ParserError(f"Got unexpected token on line {token.line} while parsing address.\n"
                              f"Expected: 'constant', 'register' or '['.\n"
                              f"Got: '{token.value}'.")
        if is_pointer:
            self.eat_token(Delimiter.RightBracket)
        return address, value

    def eat_token(self, expected):
        self.get_next_token(expected)

    def get_next_token(self, expected=None):
        token = self.tokens.pop(0)
        if expected is not None and token.type != expected:
            raise ParserError(f"Expected '{expected.value}' on line {token.line}\n"
                              f"Got '{token.value}'" )
        if self.debug:
            print(token)
        return token


class ParserError(Exception):
    pass
