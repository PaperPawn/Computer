from computer.assembler.tokens import TokenKeyword, TokenRegister, TokenDelimiter, TokenInt

letters = 'abcdefghijklmnopqrstuvwqyz'
numbers = '1234567890'
delimiters = ';[]'
whitespace = ' '

keywords = {'shutdown':  TokenKeyword.Shutdown,
            'reset': TokenKeyword.Reset,
            'move': TokenKeyword.Move,}
registers = {'a': TokenRegister.a,
             'b': TokenRegister.b,
             'c': TokenRegister.c,
             'd': TokenRegister.d,
             'sp': TokenRegister.sp,
             'pc': TokenRegister.pc}
delimiters = {';': TokenDelimiter.SemiColon,
              '[': TokenDelimiter.LeftBracket,
              ']': TokenDelimiter.RightBracket
              }


class Lexer:
    def __init__(self):
        self.line = ''

    def scan(self, line):
        self.line = iter(line)
        tokens = []
        for character in self.line:
            name = ''
            name += character

            if character in letters:
                character, name = self.lex_token(character, name, letters)
                tokens.append(self.get_token(name))

            elif character in numbers:
                character, name = self.lex_token(character, name, numbers)
                tokens.append(TokenInt(int(name)))

            if character in delimiters:
                tokens.append(delimiters[character])
        return tokens

    def lex_token(self, character, name, token_type):
        try:
            character = next(self.line)
            while character in token_type:
                name += character
                character = next(self.line)
        except StopIteration:
            pass
        return character, name

    @staticmethod
    def get_token(name):
        token = ''
        if name in keywords:
            token = keywords[name]
        if name in registers:
            token = registers[name]
        if name in delimiters:
            token = delimiters[name]
        return token


def main():
    path = 'test3.eas'

    with open(path, 'r') as file:
        for line in file:
            for char in line:
                print(repr(char))


if __name__ == '__main__':
    main()