import pytest
from computer.assembler.lexer import Lexer, LexerError
from computer.assembler.tokens import TokenKeyword, TokenDelimiter, TokenLiteral, TokenName


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
    literals = [1, 2, 3, 100, 543]

    @pytest.mark.parametrize('literal', literals)
    @pytest.mark.parametrize('register, register_token', registers)
    def test_move_literal_to_register(self, lexer, literal, register, register_token):
        line = f'move {register} {literal}'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Move,
                          register_token,
                          TokenLiteral.Int, literal]

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
                          TokenLiteral.Int, 10,
                          TokenKeyword.Pop,
                          TokenKeyword.a]

    def test_jump(self, lexer):
        line = 'jump 2675'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Jump,
                          TokenLiteral.Int, 2675]

    def test_jump_zero(self, lexer):
        line = 'jump_zero 345'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfZero,
                          TokenLiteral.Int, 345]

    def test_jump_neg(self, lexer):
        line = 'jump_neg 123786432'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfNeg,
                          TokenLiteral.Int, 123786432]

    def test_jump_overflow(self, lexer):
        line = 'jump_overflow 11'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.JumpIfOverflow,
                          TokenLiteral.Int, 11]

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
                      ('xor', TokenKeyword.Xor),
                      ('compare', TokenKeyword.Compare)]

    @pytest.mark.parametrize('command, token', alu_commands_2)
    def test_arithmetic_two_parameters(self, lexer, command, token):
        line = f'{command} a 1'
        tokens = lexer.scan(line)
        assert tokens == [token,
                          TokenKeyword.a,
                          TokenLiteral.Int, 1]

    alu_commands_1 = [('neg', TokenKeyword.Negate),
                      ('inc', TokenKeyword.Inc),
                      ('dec', TokenKeyword.Dec),
                      ('not', TokenKeyword.Not)]

    @pytest.mark.parametrize('command, token', alu_commands_1)
    def test_arithmetic_one_parameter(self, lexer, command, token):
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
                          TokenLiteral.Int, 3]

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
                          TokenName.Label, 'start',
                          TokenKeyword.Move,
                          TokenKeyword.a,
                          TokenKeyword.b]

    def test_jump_to_label(self, lexer):
        line = 'jump abc'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Jump, TokenName.Label, 'abc']

    def test_call_function_by_label(self, lexer):
        line = 'call func'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Call, TokenName.Label, 'func']

    def test_call_function_by_literal(self, lexer):
        line = 'call 1024'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Call, TokenLiteral.Int, 1024]

    def test_call_function_by_register(self, lexer):
        line = 'call a'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Call, TokenKeyword.a]

    def test_call_function_by_pointer(self, lexer):
        line = 'call [a]'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Call, TokenDelimiter.LeftBracket,
                          TokenKeyword.a, TokenDelimiter.RightBracket]

    def test_return(self, lexer):
        line = 'return'
        tokens = lexer.scan(line)
        assert tokens == [TokenKeyword.Return]

    def test_declare_variable(self, lexer):
        line = ''

# variable declaration
# import

# Never implement?s
# not(a) and b
# not(a) or b
# not(a) xor b
