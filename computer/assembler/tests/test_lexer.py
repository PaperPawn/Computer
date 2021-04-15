import pytest
from computer.assembler.lexer import Lexer
from computer.assembler.tokens import TokenKeyword, TokenRegister, TokenDelimiter, TokenInt


class TestLexer:
    @pytest.fixture
    def lexer(self):
        return Lexer()

    def test_empty_string(self, lexer):
        line = ''
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

    registers = [('a', TokenRegister.a),
                 ('b', TokenRegister.b),
                 ('c', TokenRegister.c),
                 ('d', TokenRegister.d),
                 ('sp', TokenRegister.sp),
                 ('pc', TokenRegister.pc)]
    constants = [1, 2, 3, 100, 543]

    @pytest.mark.parametrize('constant', constants)
    @pytest.mark.parametrize('register, register_token', registers)
    def test_move_constant_to_register(self, lexer, constant, register, register_token):
        line = f'move {register} {constant};'
        tokens = lexer.scan(line)

        assert tokens == [TokenKeyword.Move,
                          register_token,
                          TokenInt(constant),
                          TokenDelimiter.SemiColon
                          ]

    def test_move_register_to_register(self, lexer):
        line = 'move c d;'
        tokens = lexer.scan(line)

        assert tokens == [TokenKeyword.Move,
                          TokenRegister.c,
                          TokenRegister.d,
                          TokenDelimiter.SemiColon
                          ]

    def test_move_pointer(self, lexer):
        line = 'move a [b];'
        tokens = lexer.scan(line)

        assert tokens == [TokenKeyword.Move,
                          TokenRegister.a,
                          TokenDelimiter.LeftBracket,
                          TokenRegister.b,
                          TokenDelimiter.RightBracket,
                          TokenDelimiter.SemiColon
                          ]
