import pytest

from computer.assembler.parser import Parser, ParserError
from computer.assembler.tokens import (TokenKeyword, TokenRegister,
                                       TokenDelimiter, TokenInt, TokenLabel)
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

    registers = [([TokenRegister.a, TokenRegister.b], a_address+b_address),
                 ([TokenRegister.c, TokenRegister.d], c_address+d_address),
                 ([TokenRegister.b, TokenRegister.sp], b_address+sp_address)]

    @pytest.mark.parametrize('tokens, addresses', registers)
    def test_move_register_to_register(self, parser, tokens, addresses):
        tokens = [TokenKeyword.Move] + tokens
        instructions = parser.parse(tokens)

        assert instructions == [move_opcode + addresses]

    pregisters = [((TokenRegister.a, TokenRegister.b), (a_address, bp_address)),
                  ((TokenRegister.a, TokenRegister.c), (a_address, cp_address)),
                  ((TokenRegister.a, TokenRegister.d), (a_address, dp_address)),
                  ((TokenRegister.a, TokenRegister.sp), (a_address, spp_address)),
                  ((TokenRegister.d, TokenRegister.a), (d_address, ap_address))]

    @pytest.mark.parametrize('tokens, addresses', pregisters)
    def test_move_register_pointer_to_register(self, parser, tokens, addresses):
        tokens = [TokenKeyword.Move, tokens[0],
                  TokenDelimiter.LeftBracket, tokens[1], TokenDelimiter.RightBracket]

        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + addresses[0] + addresses[1]]

    @pytest.mark.parametrize('tokens, addresses', pregisters)
    def test_move_register_to_register_pointer(self, parser, tokens, addresses):
        tokens = [TokenKeyword.Move, TokenDelimiter.LeftBracket, tokens[1],
                  TokenDelimiter.RightBracket, tokens[0]]

        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + addresses[1] + addresses[0]]

    constant_register = [(TokenRegister.a, a_address, 1),
                         (TokenRegister.b, b_address, 10),
                         (TokenRegister.c, c_address, 6452)]

    @pytest.mark.parametrize('token, address, value', constant_register)
    def test_move_constant_to_register(self, parser, token, address, value):
        tokens = [TokenKeyword.Move, token, TokenInt(value)]
        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + address + constant_address,
                                dec_to_bin(value)]

    constant_pregister = [(TokenRegister.a, ap_address, 42),
                         (TokenRegister.b, bp_address, 17),
                         (TokenRegister.c, cp_address, 65535)]

    @pytest.mark.parametrize('token, address, value', constant_pregister)
    def test_move_constant_to_pointer_register(self, parser, token, address, value):
        tokens = [TokenKeyword.Move, TokenDelimiter.LeftBracket, token,
                  TokenDelimiter.RightBracket, TokenInt(value)]
        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + address + constant_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('token, address, value', constant_register)
    def test_move_constant_pointer_to_register(self, parser, token, address, value):
        tokens = [TokenKeyword.Move, token, TokenDelimiter.LeftBracket,
                  TokenInt(value), TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + address + constantp_address,
                                dec_to_bin(value)]

    def test_move_register_to_constant_pointer(self, parser):
        value = 125
        tokens = [TokenKeyword.Move, TokenDelimiter.LeftBracket, TokenInt(value),
                  TokenDelimiter.RightBracket, TokenRegister.a]
        instructions = parser.parse(tokens)
        assert instructions == [move_opcode + constantp_address + a_address,
                                dec_to_bin(value)]

    invalid_syntax = [[TokenKeyword.Move, TokenRegister.a,
                       TokenDelimiter.RightBracket, TokenRegister.b, TokenDelimiter.RightBracket],
                      [TokenKeyword.Move, TokenRegister.a,
                       TokenDelimiter.LeftBracket, TokenRegister.b, TokenDelimiter.LeftBracket]
                      ]

    @pytest.mark.parametrize('tokens', invalid_syntax)
    def test_move_with_invalid_syntax(self, parser, tokens):
        with pytest.raises(ParserError):
            parser.parse(tokens)

# push
# pop
# add
# sub
# neg
# inc
# dec
# and
# or
# xor
# jump
# jump if zero
# jump if neg
# jump if overflow
# hddwrite
# hddread
# hddsector

# not implemented in lexer
# bitflip
# not(a) and b
# not(a) or b
# not(a) xor b
# import
# call
# return
# variable declaration
