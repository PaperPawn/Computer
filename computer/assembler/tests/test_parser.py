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
                            (TokenKeyword.Xor, alu_opcode + alu_xor)]

    registers = [([TokenKeyword.a, TokenKeyword.b], a_address+b_address),
                 ([TokenKeyword.c, TokenKeyword.d], c_address+d_address),
                 ([TokenKeyword.b, TokenKeyword.sp], b_address+sp_address)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', registers)
    def test_two_address_command_register_to_register(self, parser, command_token, opcode,
                                                      tokens, addresses):
        tokens = [command_token] + tokens
        instructions = parser.parse(tokens)

        assert instructions == [opcode + addresses]

    pregisters = [((TokenKeyword.a, TokenKeyword.b), (a_address, bp_address)),
                  ((TokenKeyword.a, TokenKeyword.c), (a_address, cp_address)),
                  ((TokenKeyword.a, TokenKeyword.d), (a_address, dp_address)),
                  ((TokenKeyword.a, TokenKeyword.sp), (a_address, spp_address)),
                  ((TokenKeyword.d, TokenKeyword.a), (d_address, ap_address))]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', pregisters)
    def test_two_address_command_register_pointer_to_register(self, parser, command_token, opcode,
                                                              tokens, addresses):
        tokens = [command_token, tokens[0],
                  TokenDelimiter.LeftBracket, tokens[1], TokenDelimiter.RightBracket]

        instructions = parser.parse(tokens)
        assert instructions == [opcode + addresses[0] + addresses[1]]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', pregisters)
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

# target address
# inc
# dec
# neg
# pop

# source address
# push
# jump
# jump if zero
# jump if neg
# jump if overflow

# two address
# hddwrite
# hddread
# hddsector

# not implemented in lexer
# compare
# not (bitflip)
# import
# call
# return
# variable declaration
#
# not(a) and b
# not(a) or b
# not(a) xor b
