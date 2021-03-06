import pytest

from computer.assembler.parser import Parser, ParserError
from computer.assembler.tokens import Token, Keyword, Delimiter, Literal, Label
from computer.opcodes import *
from computer.utility.numbers import dec_to_bin

token_alloc = Token(Keyword.Alloc, 'alloc', 1)
token_move = Token(Keyword.Move, 'move', 1)
token_add = Token(Keyword.Add, 'add', 1)
token_pop = Token(Keyword.Pop, 'pop', 1)
token_jump = Token(Keyword.Jump, 'jump', 1)

token_a = Token(Keyword.a, 'a', 1)
token_b = Token(Keyword.b, 'b', 1)
token_c = Token(Keyword.c, 'c', 1)
token_d = Token(Keyword.d, 'd', 1)
token_sp = Token(Keyword.sp, 'sp', 1)

token_colon = Token(Delimiter.Colon, ':', 1)
token_left_bracket = Token(Delimiter.LeftBracket, '[', 1)
token_right_bracket = Token(Delimiter.RightBracket, ']', 1)


class TestParser:
    @pytest.fixture
    def parser(self):
        return Parser()

    def test_no_tokens(self, parser):
        tokens = []
        instructions = parser.parse(tokens)

        assert instructions == []

    def test_shutdown(self, parser):
        tokens = [Token(Keyword.Shutdown, 'shutdown', 1)]
        instructions = parser.parse(tokens)

        assert instructions == [shutdown_opcode]

    def test_reset(self, parser):
        tokens = [Token(Keyword.Reset, 'reset', 1)]
        instructions = parser.parse(tokens)

        assert instructions == [reset_opcode]

    two_address_commands = [(token_move, move_opcode),
                            (token_add, alu_opcode + alu_add),
                            (Token(Keyword.Sub, 'sub', 1), alu_opcode + alu_sub),
                            (Token(Keyword.And, 'and', 1), alu_opcode + alu_and),
                            (Token(Keyword.Or, 'or', 1), alu_opcode + alu_or),
                            (Token(Keyword.Xor, 'xor', 1), alu_opcode + alu_xor),
                            (Token(Keyword.Compare, 'compare', 1), alu_no_move_opcode + alu_sub),
                            (Token(Keyword.HddWrite, 'hddwrite', 1), hdd_opcode + hdd_write),
                            (Token(Keyword.HddRead, 'hddread', 1), hdd_opcode + hdd_read)]

    two_registers = [([token_a, token_b], a_address + b_address),
                     ([token_c, token_d], c_address + d_address),
                     ([token_b, token_sp], b_address + sp_address)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_registers)
    def test_two_address_command_register_to_register(self, parser, command_token, opcode,
                                                      tokens, addresses):
        tokens = [command_token] + tokens
        instructions = parser.parse(tokens)

        assert instructions == [opcode + addresses]

    two_pregisters = [((token_a, token_b), (a_address, bp_address)),
                      ((token_a, token_c), (a_address, cp_address)),
                      ((token_a, token_d), (a_address, dp_address)),
                      ((token_a, token_sp), (a_address, spp_address)),
                      ((token_d, token_a), (d_address, ap_address))]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_pregisters)
    def test_two_address_command_register_pointer_to_register(self, parser, command_token, opcode,
                                                              tokens, addresses):
        tokens = [command_token, tokens[0], token_left_bracket,
                  tokens[1], token_right_bracket]

        instructions = parser.parse(tokens)
        assert instructions == [opcode + addresses[0] + addresses[1]]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('tokens, addresses', two_pregisters)
    def test_two_address_command_register_to_register_pointer(self, parser, command_token, opcode, tokens, addresses):
        tokens = [command_token, token_left_bracket, tokens[1],
                  token_right_bracket, tokens[0]]

        instructions = parser.parse(tokens)
        assert instructions == [opcode + addresses[1] + addresses[0]]

    literal_register = [(token_a, a_address, 1),
                        (token_b, b_address, 10),
                        (token_c, c_address, 6452)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_register)
    def test_two_address_command_literal_to_register(self, parser, command_token, opcode,
                                                     token, address, value):
        tokens = [command_token, token, Token(Literal.Int, value, 1)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    literal_pregister = [(token_a, ap_address, 42),
                         (token_b, bp_address, 17),
                         (token_c, cp_address, 65535)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_pregister)
    def test_two_address_command_literal_to_pointer_register(self, parser, command_token, opcode,
                                                             token, address, value):
        tokens = [command_token, token_left_bracket, token,
                  token_right_bracket, Token(Literal.Int, value, 1)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constant_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    @pytest.mark.parametrize('token, address, value', literal_register)
    def test_two_address_command_literal_pointer_to_register(self, parser, command_token, opcode,
                                                             token, address, value):
        tokens = [command_token, token, token_left_bracket,
                  Token(Literal.Int, value, 1), token_right_bracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + constantp_address,
                                dec_to_bin(value)]

    @pytest.mark.parametrize('command_token, opcode', two_address_commands)
    def test_two_address_command_register_to_constant_pointer(self, parser, command_token, opcode):
        value = 125
        tokens = [command_token, token_left_bracket, Token(Literal.Int, value, 1),
                  token_right_bracket, token_a]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + constantp_address + a_address,
                                dec_to_bin(value)]

    target_address_commands = [(Token(Keyword.Inc, 'inc', 1), alu_opcode + alu_inc),
                               (Token(Keyword.Dec, 'dec', 1), alu_opcode + alu_dec),
                               (Token(Keyword.Negate, 'neg', 1), alu_opcode + alu_neg),
                               (Token(Keyword.Not, 'not', 1), alu_opcode + alu_not)
                               ]
    registers = [(token_a, a_address),
                 (token_b, b_address),
                 (token_c, c_address),
                 (token_d, d_address),
                 (token_sp, sp_address)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    @pytest.mark.parametrize('register_token, address', registers)
    def test_target_address_command_register(self, parser, command_token, opcode,
                                             register_token, address):
        tokens = [command_token, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + unused_opcode]

    p_registers = [(token_a, ap_address),
                   (token_b, bp_address),
                   (token_c, cp_address),
                   (token_d, dp_address),
                   (token_sp, spp_address)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_target_address_command_register_pointer(self, parser, command_token, opcode,
                                                     register_token, address):
        tokens = [command_token, token_left_bracket, register_token, token_right_bracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + address + unused_opcode]

    source_address_commands = [(token_jump, jump_opcode),
                               (Token(Keyword.JumpIfZero, 'jump_zero', 1), jump_zero_opcode),
                               (Token(Keyword.JumpIfNeg, 'jump_neg', 1), jump_neg_opcode),
                               (Token(Keyword.JumpIfOverflow, 'jump_overflow', 1), jump_overflow_opcode),
                               (Token(Keyword.HddSector, 'hddsector', 1), hdd_opcode + hdd_set_sector)]

    @pytest.mark.parametrize('command_token, opcode', target_address_commands)
    def test_target_address_command_should_not_accept_literals(self, parser, command_token, opcode):
        tokens = [command_token, Token(Literal.Int, 10, 1)]
        with pytest.raises(ParserError):
            parser.parse(tokens)

    @pytest.mark.parametrize('register_token, address', registers)
    def test_pop_register(self, parser, register_token, address):
        tokens = [token_pop, register_token]
        instructions = parser.parse(tokens)
        assert instructions == [pop_opcode + address + spp_address]

    @pytest.mark.parametrize('register_token, address', p_registers)
    def test_pop_register_pointer(self, parser, register_token, address):
        tokens = [token_pop, token_left_bracket, register_token, token_right_bracket]
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
        tokens = [command_token, token_left_bracket, register_token, token_right_bracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + address]

    literals = [10, 256, 5262]

    @pytest.mark.parametrize('command_token, opcode', source_address_commands)
    @pytest.mark.parametrize('literal', literals)
    def test_source_address_command_literal(self, parser, command_token, opcode, literal):
        tokens = [command_token, Token(Literal.Int, literal, 1)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + unused_opcode + constant_address,
                                dec_to_bin(literal)]

    push_commands = [(Token(Keyword.Push, 'push', 1), push_opcode),
                     (Token(Keyword.Call, 'call', 1), call_opcode)]

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
        tokens = [keyword_token, token_left_bracket, register_token, token_right_bracket]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + spp_address + address]

    @pytest.mark.parametrize('keyword_token, opcode', push_commands)
    @pytest.mark.parametrize('literal', literals)
    def test_push_or_call_literal(self, parser, keyword_token, opcode, literal):
        tokens = [keyword_token, Token(Literal.Int, literal, 1)]
        instructions = parser.parse(tokens)
        assert instructions == [opcode + spp_address + constant_address,
                                dec_to_bin(literal)]

    def test_return(self, parser):
        tokens = [Token(Keyword.Return, 'return', 1)]
        instructions = parser.parse(tokens)
        assert instructions == [return_opcode + unused_opcode + spp_address]

    def test_bare_label(self, parser):
        tokens = [token_colon, Token(Label.Name, 'start', 1)]
        instructions = parser.parse(tokens)
        assert instructions == []
        assert parser.labels == {'start': 0}

    def test_jump_to_label_at_start(self, parser):
        tokens = [token_colon, Token(Label.Name, 'start', 1),
                  token_jump, Token(Label.Name, 'start', 2)]
        instructions = parser.parse(tokens)
        assert instructions == [jump_opcode + unused_opcode + constant_address,
                                Token(Label.Name, 'start', 2)
                                ]

    def test_jump_to_label_before_jump(self, parser):
        tokens = [token_add, token_a, token_b,
                  token_colon, Token(Label.Name, 'label', 2),
                  token_add, token_a, token_b,
                  token_jump, Token(Label.Name, 'label', 4)]
        instructions = parser.parse(tokens)
        assert instructions == [alu_opcode + alu_add + a_address + b_address,
                                alu_opcode + alu_add + a_address + b_address,
                                jump_opcode + unused_opcode + constant_address,
                                Token(Label.Name, 'label', 4)
                                ]

    def test_jump_to_label_after_jump(self, parser):
        tokens = [token_jump, Token(Label.Name, 'end', 1),
                  token_add, token_a, token_b,
                  token_add, token_a, token_b,
                  token_colon, Token(Label.Name, 'end', 4),
                  Token(Keyword.Shutdown, 'shutdown', 5)]
        instructions = parser.parse(tokens)
        assert instructions == [jump_opcode + unused_opcode + constant_address,
                                Token(Label.Name, 'end', 1),
                                alu_opcode + alu_add + a_address + b_address,
                                alu_opcode + alu_add + a_address + b_address,
                                shutdown_opcode
                                ]

    names = ['variable', 'abc']
    sizes = [1, 2, 3]

    @pytest.mark.parametrize('size', sizes)
    @pytest.mark.parametrize('name', names)
    def test_alloc(self, parser, name, size):
        tokens = [Token(Keyword.Alloc, 'alloc', 1),
                  Token(Label.Name, name, 1),
                  Token(Literal.Int, size, 1)]
        instructions = parser.parse(tokens)
        assert instructions == []
        assert parser.variables[name] == size

    def test_use_alloc_data(self, parser):
        tokens = [token_alloc,
                  Token(Label.Name, 'var', 1),
                  Token(Literal.Int, 1, 1),
                  token_move, token_a, Token(Literal.Int, 0, 2),
                  token_move,
                  token_left_bracket, Token(Label.Name, 'var', 3), token_right_bracket,
                  token_a
                  ]
        instructions = parser.parse(tokens)
        assert instructions == [move_opcode+a_address+constant_address,
                                dec_to_bin(0),
                                move_opcode+constantp_address+a_address,
                                Token(Label.Name, 'var', 3)]

    def test_KEYBOARD_label(self, parser):
        token_keyboard_label = Token(Label.Name, 'KEYBOARD', 1)
        tokens = [token_move, token_a, token_left_bracket,
                  token_keyboard_label, token_right_bracket]
        instructions = parser.parse(tokens)
        keyboard_address = dec_to_bin(40960)
        assert instructions == [move_opcode + a_address + constantp_address,
                                keyboard_address]

    def test_SCREEN_label(self, parser):
        token_screen_label = Token(Label.Name, 'SCREEN', 1)
        tokens = [token_move, token_a, token_left_bracket,
                  token_screen_label, token_right_bracket]
        instructions = parser.parse(tokens)
        screen_address = dec_to_bin(32768)
        assert instructions == [move_opcode + a_address + constantp_address,
                                screen_address]

    def test_BP_label(self, parser):
        token_bp_label = Token(Label.Name, 'BP', 1)
        tokens = [token_move, token_sp, token_bp_label]
        instructions = parser.parse(tokens)
        base_pointer_address = dec_to_bin(32767)
        assert instructions == [move_opcode + sp_address + constant_address,
                                base_pointer_address]

    msg_invalid_syntax = [['Double right brackets', [token_move, token_a, token_right_bracket,
                                                     token_b, token_right_bracket]],
                          ['double left brackets', [token_move, token_a, token_left_bracket,
                                                    token_b, token_left_bracket]],
                          ['Literal as first token', [Token(Literal.Int, 1, 1)]],
                          ['Label as first token', [Token(Label.Name, 'abc', 1)]],
                          ['Bare left bracket', [token_left_bracket]],
                          ['Bare move command', [token_move, token_a, Token(Literal.Int, 1, 1), token_move]],
                          ['No label after colon', [token_colon, token_move, token_a, token_b]],
                          ['Two move keywords', [token_move, token_move, token_a, token_b]],
                          ['Jump to missing label', [token_jump, Token(Label.Name, 'missing', 1)]],
                          ['Missing label after alloc', [token_alloc, token_a]],
                          ['Missing size after alloc', [token_alloc, Token(Label.Name, 'var', 1), token_move]],
                          ['Moving literal to label', [token_alloc, Token(Label.Name, 'var', 1), Token(Literal.Int, 1, 1),
                                                       token_move, token_left_bracket,
                                                       Token(Label.Name, 'var', 1), token_right_bracket,
                                                       Token(Literal.Int, 1, 1)]],
                          ['Declaring two labels with same name', [token_colon, Token(Label.Name, 'abc', 1),
                                                                   token_colon, Token(Label.Name, 'abc', 1)]],
                          ['Alloc to same label twice', [token_alloc, Token(Label.Name, 'abc', 1),
                                                         Token(Literal.Int, 1, 1),
                                                         token_alloc, Token(Label.Name, 'abc', 1),
                                                         Token(Literal.Int, 1, 1)]],
                          ['Declaring allocated label', [token_alloc, Token(Label.Name, 'abc', 1),
                                                         Token(Literal.Int, 1, 1),
                                                         token_colon, Token(Label.Name, 'abc', 1)]],
                          ['Allocating declated label', [token_colon, Token(Label.Name, 'abc', 1),
                                                         token_alloc, Token(Label.Name, 'abc', 1),
                                                         Token(Literal.Int, 1, 1)]]
                          ]
    ids = [syn[0] for syn in msg_invalid_syntax]
    invalid_syntax = [syn[1] for syn in msg_invalid_syntax]

    @pytest.mark.parametrize('tokens', invalid_syntax, ids=ids)
    def test_invalid_syntax(self, parser, tokens):
        with pytest.raises(ParserError):
            parser.parse(tokens)

# not implemented in lexer
# import
#
# not(a) and b
# not(a) or b
# not(a) xor b
