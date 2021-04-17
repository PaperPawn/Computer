import pytest
from computer.assembler.lexer import Lexer, LexerError
from computer.assembler.tokens import TokenKeyword, TokenDelimiter, TokenConstant, TokenLabel


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
        assert tokens == [TokenKeyword.Shutdown]

    def test_reset(self, lexer):
        line = 'reset'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Reset]

    registers = [('a', TokenKeyword.a),
                 ('b', TokenKeyword.b),
                 ('c', TokenKeyword.c),
                 ('d', TokenKeyword.d),
                 ('sp', TokenKeyword.sp)]
    constants = [1, 2, 3, 100, 543]

    @pytest.mark.parametrize('constant', constants)
    @pytest.mark.parametrize('register, register_token', registers)
    def test_move_constant_to_register(self, lexer, constant, register, register_token):
        line = f'move {register} {constant}'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          register_token,
                          TokenConstant(constant)]

    def test_move_lots_of_whitespace(self, lexer):
        line = '    move       b         sp'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.b,
                          TokenKeyword.sp]

    def test_move_register_to_register(self, lexer):
        line = 'move c d'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.c,
                          TokenKeyword.d]

    def test_move_pointer(self, lexer):
        line = 'move a [b]'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.a,
                          TokenDelimiter.LeftBracket,
                          TokenKeyword.b,
                          TokenDelimiter.RightBracket]

    def test_stack_ops(self, lexer):
        line = 'push 10 pop a'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Push,
                          TokenConstant(10),
                          TokenKeyword.Pop,
                          TokenKeyword.a]

    def test_jump(self, lexer):
        line = 'jump 2675'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Jump,
                          TokenConstant(2675)]

    def test_jump_zero(self, lexer):
        line = 'jump_zero 345'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfZero,
                          TokenConstant(345)]

    def test_jump_neg(self, lexer):
        line = 'jump_neg 123786432'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfNeg,
                          TokenConstant(123786432)]

    def test_jump_overflow(self, lexer):
        line = 'jump_overflow 11'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfOverflow,
                          TokenConstant(11)]

    def test_line_break(self, lexer):
        line = '\nmove a b\n push a'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.a,
                          TokenKeyword.b,
                          TokenKeyword.Push,
                          TokenKeyword.a]

    def test_tab(self, lexer):
        line = '\tmove\t\ta\t\t\tb'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.a,
                          TokenKeyword.b]

    alu_commands_2 = [('add', TokenKeyword.Add),
                      ('sub', TokenKeyword.Sub),
                      ('and', TokenKeyword.And),
                      ('or', TokenKeyword.Or),
                      ('xor', TokenKeyword.Xor)]

    @pytest.mark.parametrize('command, token', alu_commands_2)
    def test_arithmetic_two_parameters(self, lexer, command, token):
        line = f'{command} a 1'
        tokens = lexer.scan(line)
        assert tokens == [token,
                          TokenKeyword.a,
                          TokenConstant(1)]

    alu_commands_1 = [('neg', TokenKeyword.Negate),
                      ('inc', TokenKeyword.Inc),
                      ('dec', TokenKeyword.Dec)]

    @pytest.mark.parametrize('command, token', alu_commands_1)
    def test_arithmetic_two_parameters(self, lexer, command, token):
        line = f'{command} a'
        tokens = lexer.scan(line)
        assert tokens == [token,
                          TokenKeyword.a]

    hdd_commands = [('hddread', TokenKeyword.HddRead),
                    ('hddwrite', TokenKeyword.HddWrite),
                    ('hddsector', TokenKeyword.HddSector)]

    @pytest.mark.parametrize('command, token', hdd_commands)
    def test_hdd(self, lexer, command, token):
        line = f'{command} a b'
        tokens = lexer.scan(line)
        assert tokens == [token,
                          TokenKeyword.a,
                          TokenKeyword.b]

    def test_comment(self, lexer):
        line = '% move a b'
        tokens = lexer.scan(line)
        assert tokens == []

    def test_comment_one_line(self, lexer):
        line = 'move c b\n% move a b\nadd c 3'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.c,
                          TokenKeyword.b,
                          TokenKeyword.Add,
                          TokenKeyword.c,
                          TokenConstant(3)]

    def test_comment_two_lines_1(self, lexer):
        line = 'move c b\n% move a b\n%add c 3'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.c,
                          TokenKeyword.b]

    def test_comment_two_lines_2(self, lexer):
        line = 'move c b\n% move a b\n%add c 3\npop b'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          TokenKeyword.c,
                          TokenKeyword.b,
                          TokenKeyword.Pop,
                          TokenKeyword.b]

    invalid_lines = ['&', 'move # a b', 'move a b\n123)']

    @pytest.mark.parametrize('line', invalid_lines)
    def test_not_valid_lines(self, lexer, line):
        with pytest.raises(LexerError):
            lexer.scan(line)

    def test_declare_label(self, lexer):
        line = ':start move a b'
        tokens = lexer.scan(line)
        assert tokens == [TokenDelimiter.Colon,
                          TokenLabel('start'),
                          TokenKeyword.Move,
                          TokenKeyword.a,
                          TokenKeyword.b]

    def test_jump_to_label(self, lexer):
        line = 'jump abc'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Jump,
                          TokenLabel('abc')]

# compare
# not
# import
# call
# return
# variable declaration

# Never implement?s
# not(a) and b
# not(a) or b
# not(a) xor b
