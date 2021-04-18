import pytest

from computer.assembler.parser import Parser, ParserError
from computer.assembler.tokens import (TokenKeyword, TokenDelimiter, TokenLiteral, TokenName)
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

    literal_register = [(TokenKeyword.a, a_address, 1),
                        (TokenKeyword.b, b_address, 10),
                        (TokenKeyword.c, c_address, 6452)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_register)
    def test_two_address_command_literal_to_register(self, parser, command_token, opcode,
                                                     token, address, value):
        tokens = [command_token, token, TokenLiteral.Int, value]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    literal_pregister = [(TokenKeyword.a, ap_address, 42),
                         (TokenKeyword.b, bp_address, 17),
                         (TokenKeyword.c, cp_address, 65535)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_pregister)
    def test_two_address_command_literal_to_pointer_register(self, parser, command_token, opcode,
                                                              token, address, value):
        tokens = [command_token, TokenDelimiter.LeftBracket, token,
                  TokenDelimiter.RightBracket, TokenLiteral.Int, value]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_register)
    def test_two_address_command_literal_pointer_to_register(self, parser, command_token, opcode,
                                                              token, address, value):
        tokens = [command_token, token, TokenDelimiter.LeftBracket,
                  TokenLiteral.Int, value, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constantp_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    def test_two_address_command_register_to_constant_pointer(self, parser, command_token, opcode):
        value = 125
        tokens = [command_token, TokenDelimiter.LeftBracket, TokenLiteral.Int, value,
                  TokenDelimiter.RightBracket, TokenKeyword.a]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + constantp_address + a_address,
                                dec_to_bin(value)]

    invalid_syntax = [[TokenKeyword.Move, TokenKeyword.a,
                       TokenDelimiter.RightBracket, TokenKeyword.b, TokenDelimiter.RightBracket],
                      [TokenKeyword.Move, TokenKeyword.a,
                       TokenDelimiter.LeftBracket, TokenKeyword.b, TokenDelimiter.LeftBracket],
                      [TokenLiteral.Int],
                      [TokenName.Label],
                      [TokenDelimiter.LeftBracket],
                      [TokenKeyword.Move, TokenKeyword.a, TokenLiteral.Int, TokenKeyword.Move],
                      [TokenDelimiter.Colon, TokenKeyword.Move, TokenKeyword.a, TokenKeyword.b],
                      [TokenDelimiter.Colon, TokenName.Label, TokenKeyword.Move,
                       TokenKeyword.Move, TokenKeyword.a, TokenKeyword.b]
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
    def test_target_address_command_should_not_accept_literals(self, parser, command_token, opcode):
        tokens = [command_token, TokenLiteral.Int, 10]
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

    literals = [10, 256, 5262]

    @pytest.mark.parametrize('command_token, opcode', source_address_commands)
    @pytest.mark.parametrize('literal', literals)
    def test_source_address_command_literal(self, parser, command_token, opcode, literal):
        tokens = [command_token, TokenLiteral.Int, literal]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + constant_address,
                                dec_to_bin(literal)]

    push_commands = [(TokenKeyword.Push, push_opcode),
                     (TokenKeyword.Call, call_opcode)]

    @pytest.mark.parametrize('keyword_token, opcode', push_commands)
    @pytest.mark.parametrize('register_token, address', registers)
    def test_push_or_call_register(self, parser, keyword_token, opcode,
                                   register_token, address):
        tokens = [keyword_token, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + spp_address + address]

    @pytest.mark.parametrize('keyword_token, opcode', push_commands)
    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_push_or_call_register_pointer(self, parser, keyword_token, opcode, register_token, address):
        tokens = [keyword_token, TokenDelimiter.LeftBracket, register_token, TokenDelimiter.RightBracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + spp_address + address]

    @pytest.mark.parametrize('keyword_token, opcode', push_commands)
    @pytest.mark.parametrize('literal', literals)
    def test_push_or_call_literal(self, parser, keyword_token, opcode, literal):
        tokens = [keyword_token, TokenLiteral.Int, literal]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + spp_address + constant_address,
                                dec_to_bin(literal)]

    def test_return(self, parser):
        tokens = [TokenKeyword.Return]
        instructions = parser.parse(tokens)
        assert instructions == [return_opcode + unused_opcode + spp_address]

    def test_jump_to_label_at_start(self, parser):
        tokens = [TokenDelimiter.Colon, TokenName.Label, 'start',
                  TokenKeyword.Jump, TokenName.Label, 'start']
        instructions = parser.parse(tokens)
        assert instructions == [jump_opcode + unused_opcode + constant_address,
                                dec_to_bin(0)]

    def test_jump_to_label_before_jump(self, parser):
        tokens = [TokenKeyword.Add, TokenKeyword.a, TokenKeyword.b,
                  TokenDelimiter.Colon, TokenName.Label, 'label',
                  TokenKeyword.Add, TokenKeyword.a, TokenKeyword.b,
                  TokenKeyword.Jump, TokenName.Label, 'label']
        instructions = parser.parse(tokens)
        assert instructions == [alu_opcode + alu_add + a_address + b_address,
                                alu_opcode + alu_add + a_address + b_address,
                                jump_opcode + unused_opcode + constant_address,
                                dec_to_bin(1)]

    def test_jump_to_label_after_jump(self, parser):
        tokens = [TokenKeyword.Jump, TokenName.Label, 'end',
                  TokenKeyword.Add, TokenKeyword.a, TokenKeyword.b,
                  TokenKeyword.Add, TokenKeyword.a, TokenKeyword.b,
                  TokenDelimiter.Colon, TokenName.Label, 'end',
                  TokenKeyword.Shutdown]
        instructions = parser.parse(tokens)
        assert instructions == [jump_opcode + unused_opcode + constant_address, dec_to_bin(4),
                                alu_opcode + alu_add + a_address + b_address,
                                alu_opcode + alu_add + a_address + b_address,
                                shutdown_opcode
                                ]

    def test_jump_to_label_no_linking(self, parser):
        tokens = [TokenDelimiter.Colon, TokenName.Label, 'start',
                  TokenKeyword.Jump, TokenName.Label, 'start']
        instructions = parser.parse(tokens, link=False)
        assert instructions == [jump_opcode + unused_opcode + constant_address,
                                'start']

# Add error checking for:
# -label at end of file
# -jump to non-existing label
# -label not following name token
# -value not following literal token

# not implemented in lexer
# variable declaration
# use variable as address/value
# import
#
# not(a) and b
# not(a) or b
# not(a) xor b
