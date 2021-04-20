import pytest
from computer.assembler.lexer import Lexer, LexerError
from computer.assembler.tokens import Token, Keyword, Delimiter, Literal, Name


class TestLexer:
    @pytest.fixture
    def lexer(self):
        return Lexer()

    def test_empty_string(self, lexer):
        line = ''
        tokens = lexer.scan(line)
        assert tokens == []

    def test_only_whitespace(self, lexer):
        line = ' '
        tokens = lexer.scan(line)
        assert tokens == []

    def test_shutdown(self, lexer):
        line = 'shutdown'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Shutdown, 'shutdown', 1)]

    def test_reset(self, lexer):
        line = 'reset'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Reset, 'reset', 1)]

    registers = [('a', Keyword.a),
                 ('b', Keyword.b),
                 ('c', Keyword.c),
                 ('d', Keyword.d),
                 ('sp', Keyword.sp)]
    literals = [1, 2, 3, 100, 543]

    @pytest.mark.parametrize('literal', literals)
    @pytest.mark.parametrize('register, register_token', registers)
    def test_move_literal_to_register(self, lexer, literal, register, register_token):
        line = f'move {register} {literal}'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(register_token, register, 1),
                          Token(Literal.Int, literal, 1)]

    def test_move_lots_of_whitespace(self, lexer):
        line = '    move       b         sp'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.b, 'b', 1),
                          Token(Keyword.sp, 'sp', 1)]

    def test_move_register_to_register(self, lexer):
        line = 'move c d'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.c, 'c', 1),
                          Token(Keyword.d, 'd', 1)]

    def test_move_pointer(self, lexer):
        line = 'move a [b]'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Delimiter.LeftBracket, '[', 1),
                          Token(Keyword.b, 'b', 1),
                          Token(Delimiter.RightBracket, ']', 1)]

    def test_move_pointer_second_line(self, lexer):
        line = 'inc b\nmove a [b]'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Inc, 'inc', 1),
                          Token(Keyword.b, 'b', 1),
                          Token(Keyword.Move, 'move', 2),
                          Token(Keyword.a, 'a', 2),
                          Token(Delimiter.LeftBracket, '[', 2),
                          Token(Keyword.b, 'b', 2),
                          Token(Delimiter.RightBracket, ']', 2)]

    def test_stack_ops(self, lexer):
        line = 'push 10 pop a'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Push, 'push', 1),
                          Token(Literal.Int, 10, 1),
                          Token(Keyword.Pop, 'pop', 1),
                          Token(Keyword.a, 'a', 1)]

    def test_jump(self, lexer):
        line = 'jump 2675'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Jump, 'jump', 1),
                          Token(Literal.Int, 2675, 1)]

    def test_jump_zero(self, lexer):
        line = 'jump_zero 345'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.JumpIfZero, 'jump_zero', 1),
                          Token(Literal.Int, 345, 1)]

    def test_jump_neg(self, lexer):
        line = 'jump_neg 123786432'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.JumpIfNeg, 'jump_neg', 1),
                          Token(Literal.Int, 123786432, 1)]

    def test_jump_overflow(self, lexer):
        line = 'jump_overflow 11'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.JumpIfOverflow, 'jump_overflow', 1),
                          Token(Literal.Int, 11, 1)]

    def test_line_break(self, lexer):
        line = '\nmove a b\n push a'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 2),
                          Token(Keyword.a, 'a', 2),
                          Token(Keyword.b, 'b', 2),
                          Token(Keyword.Push, 'push', 3),
                          Token(Keyword.a, 'a', 3)]

    def test_tab(self, lexer):
        line = '\tmove\t\ta\t\t\tb'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Keyword.b, 'b', 1)]

    alu_commands_2 = [('add', Keyword.Add),
                      ('sub', Keyword.Sub),
                      ('and', Keyword.And),
                      ('or', Keyword.Or),
                      ('xor', Keyword.Xor),
                      ('compare', Keyword.Compare)]

    @pytest.mark.parametrize('command, token', alu_commands_2)
    def test_arithmetic_two_parameters(self, lexer, command, token):
        line = f'{command} a 1'
        tokens = lexer.scan(line)
        assert tokens == [Token(token, command, 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Literal.Int, 1, 1)]

    alu_commands_1 = [('neg', Keyword.Negate),
                      ('inc', Keyword.Inc),
                      ('dec', Keyword.Dec),
                      ('not', Keyword.Not)]

    @pytest.mark.parametrize('command, token', alu_commands_1)
    def test_arithmetic_one_parameter(self, lexer, command, token):
        line = f'{command} a'
        tokens = lexer.scan(line)
        assert tokens == [Token(token, command, 1),
                          Token(Keyword.a, 'a', 1)]

    hdd_commands = [('hddread', Keyword.HddRead),
                    ('hddwrite', Keyword.HddWrite),
                    ('hddsector', Keyword.HddSector)]

    @pytest.mark.parametrize('command, token', hdd_commands)
    def test_hdd(self, lexer, command, token):
        line = f'{command} a b'
        tokens = lexer.scan(line)
        assert tokens == [Token(token, command, 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Keyword.b, 'b', 1)]

    def test_comment(self, lexer):
        line = '% move a b'
        tokens = lexer.scan(line)
        assert tokens == []

    def test_comment_one_line(self, lexer):
        line = 'move c b\n% move a b\nadd c 3'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.c, 'c', 1),
                          Token(Keyword.b, 'b', 1),
                          Token(Keyword.Add, 'add', 3),
                          Token(Keyword.c, 'c', 3),
                          Token(Literal.Int, 3, 3)]

    def test_comment_two_lines_1(self, lexer):
        line = 'move c b\n% move a b\n%add c 3'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.c, 'c', 1),
                          Token(Keyword.b, 'b', 1)]

    def test_comment_two_lines_2(self, lexer):
        line = 'move c b\n% move a b\n%add c 3\npop b'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Move, 'move', 1),
                          Token(Keyword.c, 'c', 1),
                          Token(Keyword.b, 'b', 1),
                          Token(Keyword.Pop, 'pop', 4),
                          Token(Keyword.b, 'b', 4)]

    invalid_lines = ['&', 'move # a b', 'move a b\n123)']

    @pytest.mark.parametrize('line', invalid_lines)
    def test_not_valid_lines(self, lexer, line):
        with pytest.raises(LexerError):
            lexer.scan(line)

    def test_declare_label(self, lexer):
        line = ':start move a b'
        tokens = lexer.scan(line)
        assert tokens == [Token(Delimiter.Colon, ':', 1),
                          Token(Name.Label, 'start', 1),
                          Token(Keyword.Move, 'move', 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Keyword.b, 'b', 1)]

    def test_jump_to_label(self, lexer):
        line = 'jump abc'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Jump, 'jump', 1),
                          Token(Name.Label, 'abc', 1)]

    def test_call_function_by_label(self, lexer):
        line = 'call func'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Call, 'call', 1),
                          Token(Name.Label, 'func', 1)]

    def test_call_function_by_literal(self, lexer):
        line = 'call 1024'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Call, 'call', 1),
                          Token(Literal.Int, 1024, 1)]

    def test_call_function_by_register(self, lexer):
        line = 'call a'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Call, 'call', 1),
                          Token(Keyword.a, 'a', 1)]

    def test_call_function_by_pointer(self, lexer):
        line = 'call [a]'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Call, 'call', 1),
                          Token(Delimiter.LeftBracket, '[', 1),
                          Token(Keyword.a, 'a', 1),
                          Token(Delimiter.RightBracket, ']', 1)]

    def test_return(self, lexer):
        line = 'return'
        tokens = lexer.scan(line)
        assert tokens == [Token(Keyword.Return, 'return', 1)]

    def test_declare_variable(self, lexer):
        line = ''

# Tests
# line counting with
# - comments
# - literals
# - delimeters

# variable declaration
# import

# Never implement?s
# not(a) and b
# not(a) or b
# not(a) xor b
