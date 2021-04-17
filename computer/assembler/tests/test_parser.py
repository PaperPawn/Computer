import pytest

from computer.assembler.parser import Parser, ParserError
from computer.assembler.tokens import (TokenKeyword, TokenDelimiter, TokenConstant, TokenLabel)
from computer.opcodes import *
from computer.utility.numbers import dec_to_bin


class TestParser:
    @pytest.fixture
    def parser(self):
        return Parser()

    def test_no_tokens(self, parser):
        tokens = []
        instructions = parser.parse(tokens)

        assert instructions == []

    def test_shutdown(self, parser):
        tokens = [TokenKeyword.Shutdown]
        instructions = parser.parse(tokens)

        assert instructions == [shutdown_opcode]

    def test_reset(self, parser):
        tokens = [TokenKeyword.Reset]
        instructions = parser.parse(tokens)

        assert instructions == [reset_opcode]

    two_address_commands = [(TokenKeyword.Move, move_opcode),
                            (TokenKeyword.Add, alu_opcode + alu_add),
                            (TokenKeyword.Sub, alu_opcode + alu_sub),
                            (TokenKeyword.And, alu_opcode + alu_and),
                            (TokenKeyword.Or, alu_opcode + alu_or),
                            (TokenKeyword.Xor, alu_opcode + alu_xor),
                            (TokenKeyword.Compare, alu_no_move_opcode + alu_sub),
                            (TokenKeyword.HddWrite, hdd_opcode+hdd_write),
                            (TokenKeyword.HddRead, hdd_opcode + hdd_read)]

    two_registers = [([TokenKeyword.a, TokenKeyword.b], a_address + b_address),
                     ([TokenKeyword.c, TokenKeyword.d], c_address+d_address),
                     ([TokenKeyword.b, TokenKeyword.sp], b_address+sp_address)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_registers)
    def test_two_address_command_register_to_register(self, parser, command_token, opcode,
                                                      tokens, addresses):
        tokens = [command_token] + tokens
        instructions = parser.parse(tokens)

        assert instructions == [opcode + addresses]

    two_pregisters = [((TokenKeyword.a, TokenKeyword.b), (a_address, bp_address)),
                      ((TokenKeyword.a, TokenKeyword.c), (a_address, cp_address)),
                      ((TokenKeyword.a, TokenKeyword.d), (a_address, dp_address)),
                      ((TokenKeyword.a, TokenKeyword.sp), (a_address, spp_address)),
                      ((TokenKeyword.d, TokenKeyword.a), (d_address, ap_address))]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_pregisters)
    def test_two_address_command_register_pointer_to_register(self, parser, command_token, opcode,
                                                              tokens, addresses):
        tokens = [command_token, tokens[0],
                  TokenDelimiter.LeftBracket, tokens[1], TokenDelimiter.RightBracket]

        instructions = parser.parse(tokens)
        assert instructions == [opcode + addresses[0] + addresses[1]]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_pregisters)
    def test_two_address_command_register_to_register_pointer(self, parser, command_token, opcode, tokens, addresses):
        tokens = [command_token, TokenDelimiter.LeftBracket, tokens[1],
                  TokenDelimiter.RightBracket, tokens[0]]

        instructions = parser.parse(tokens)
        assert instructions == [opcode + addresses[1] + addresses[0]]

    constant_register = [(TokenKeyword.a, a_address, 1),
                         (TokenKeyword.b, b_address, 10),
                         (TokenKeyword.c, c_address, 6452)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', constant_register)
    def test_two_address_command_constant_to_register(self, parser, command_token, opcode,
                                                      token, address, value):
        tokens = [command_token, token, TokenConstant(value)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    constant_pregister = [(TokenKeyword.a, ap_address, 42),
                          (TokenKeyword.b, bp_address, 17),
                          (TokenKeyword.c, cp_address, 65535)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', constant_pregister)
    def test_two_address_command_constant_to_pointer_register(self, parser, command_token, opcode,
                                                              token, address, value):
        tokens = [command_token, TokenDelimiter.LeftBracket, token,
                  TokenDelimiter.RightBracket, TokenConstant(value)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', constant_register)
    def test_two_address_command_constant_pointer_to_register(self, parser, command_token, opcode,
                                                              token, address, value):
        tokens = [command_token, token, TokenDelimiter.LeftBracket,
                  TokenConstant(value), TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constantp_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    def test_two_address_command_register_to_constant_pointer(self, parser, command_token, opcode):
        value = 125
        tokens = [command_token, TokenDelimiter.LeftBracket, TokenConstant(value),
                  TokenDelimiter.RightBracket, TokenKeyword.a]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + constantp_address + a_address,
                                dec_to_bin(value)]

    invalid_syntax = [[TokenKeyword.Move, TokenKeyword.a,
                       TokenDelimiter.RightBracket, TokenKeyword.b, TokenDelimiter.RightBracket],
                      [TokenKeyword.Move, TokenKeyword.a,
                       TokenDelimiter.LeftBracket, TokenKeyword.b, TokenDelimiter.LeftBracket]
                      ]

    @pytest.mark.parametrize('tokens', invalid_syntax)
    def test_invalid_syntax(self, parser, tokens):
        with pytest.raises(ParserError):
            parser.parse(tokens)

    target_address_commands = [(TokenKeyword.Inc, alu_opcode+alu_inc),
                               (TokenKeyword.Dec, alu_opcode+alu_dec),
                               (TokenKeyword.Negate, alu_opcode+alu_neg),
                               (TokenKeyword.Not, alu_opcode+alu_not)
                               ]
    registers = [(TokenKeyword.a, a_address),
                 (TokenKeyword.b, b_address),
                 (TokenKeyword.c, c_address),
                 (TokenKeyword.d, d_address),
                 (TokenKeyword.sp, sp_address)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    @pytest.mark.parametrize('register_token, address', registers)
    def test_target_address_command_register(self, parser, command_token, opcode,
                                             register_token, address):
        tokens = [command_token, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + unused_opcode]

    p_registers = [(TokenKeyword.a, ap_address),
                   (TokenKeyword.b, bp_address),
                   (TokenKeyword.c, cp_address),
                   (TokenKeyword.d, dp_address),
                   (TokenKeyword.sp, spp_address)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_target_address_command_register_pointer(self, parser, command_token, opcode,
                                                     register_token, address):
        tokens = [command_token, TokenDelimiter.LeftBracket, register_token, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + unused_opcode]

    source_address_commands = [(TokenKeyword.Jump, jump_opcode),
                               (TokenKeyword.JumpIfZero, jump_zero_opcode),
                               (TokenKeyword.JumpIfNeg, jump_neg_opcode),
                               (TokenKeyword.JumpIfOverflow, jump_overflow_opcode),
                               (TokenKeyword.HddSector, hdd_opcode+hdd_set_sector)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    def test_target_address_command_should_not_accept_constant(self, parser, command_token, opcode):
        tokens = [command_token, TokenConstant(10)]
        with pytest.raises(ParserError):
            parser.parse(tokens)

    @pytest.mark.parametrize('register_token, address', registers)
    def test_pop_register(self, parser, register_token, address):
        tokens = [TokenKeyword.Pop, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [pop_opcode + address + spp_address]

    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_pop_register_pointer(self, parser, register_token, address):
        tokens = [TokenKeyword.Pop, TokenDelimiter.LeftBracket, register_token, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [pop_opcode + address + spp_address]

    @pytest.mark.parametrize('command_token, opcode', source_address_commands)
    @pytest.mark.parametrize('register_token, address', registers)
    def test_source_address_command_register(self, parser, command_token, opcode,
                                             register_token, address):
        tokens = [command_token, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + address]

    @pytest.mark.parametrize('command_token, opcode', source_address_commands)
    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_source_address_command_register_pointer(self, parser, command_token, opcode,
                                                     register_token, address):
        tokens = [command_token, TokenDelimiter.LeftBracket, register_token, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + address]

    constants = [10, 256, 5262]

    @pytest.mark.parametrize('command_token, opcode', source_address_commands)
    @pytest.mark.parametrize('constant', constants)
    def test_source_address_command_constant(self, parser, command_token, opcode, constant):
        tokens = [command_token, TokenConstant(constant)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + constant_address,
                                dec_to_bin(constant)]

    @pytest.mark.parametrize('register_token, address', registers)
    def test_push_register(self, parser, register_token, address):
        tokens = [TokenKeyword.Push, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [push_opcode + spp_address + address]

    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_push_register_pointer(self, parser, register_token, address):
        tokens = [TokenKeyword.Push, TokenDelimiter.LeftBracket, register_token, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [push_opcode + spp_address + address]

    @pytest.mark.parametrize('constant', constants)
    def test_push_constant(self, parser, constant):
        tokens = [TokenKeyword.Push, TokenConstant(constant)]
        instructions = parser.parse(tokens)
        assert instructions == [push_opcode + spp_address + constant_address,
                                dec_to_bin(constant)]

# not implemented in lexer
# import
# call
# return
# variable declaration
#
# not(a) and b
# not(a) or b
# not(a) xor b
