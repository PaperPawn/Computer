from computer.assembler.tokens import TokenKeyword, TokenDelimiter, TokenConstant, TokenLabel

variable = 'abcdefghijklmnopqrstuvwqxyz_'
numbers = '1234567890'
whitespace = ' \n\t'
comment = '%'

command_tokens = {'shutdown':  TokenKeyword.Shutdown,
                  'reset': TokenKeyword.Reset,
                  'move': TokenKeyword.Move,
                  'push': TokenKeyword.Push,
                  'pop': TokenKeyword.Pop,
                  'add': TokenKeyword.Add,
                  'sub': TokenKeyword.Sub,
                  'and': TokenKeyword.And,
                  'or': TokenKeyword.Or,
                  'xor': TokenKeyword.Xor,
                  'neg': TokenKeyword.Negate,
                  'inc': TokenKeyword.Inc,
                  'dec': TokenKeyword.Dec,
                  'jump': TokenKeyword.Jump,
                  'jump_zero': TokenKeyword.JumpIfZero,
                  'jump_neg': TokenKeyword.JumpIfNeg,
                  'jump_overflow': TokenKeyword.JumpIfOverflow,
                  'hddread': TokenKeyword.HddRead,
                  'hddwrite': TokenKeyword.HddWrite,
                  'hddsector': TokenKeyword.HddSector}
register_tokens = {'a': TokenKeyword.a,
                   'b': TokenKeyword.b,
                   'c': TokenKeyword.c,
                   'd': TokenKeyword.d,
                   'sp': TokenKeyword.sp}
delimiter_tokens = {'[': TokenDelimiter.LeftBracket,
                    ']': TokenDelimiter.RightBracket,
                    ':': TokenDelimiter.Colon
                    }

delimiters = ''.join(delimiter_tokens)
valid_token_characters = variable + numbers + delimiters
valid_characters = valid_token_characters + whitespace + comment


class Lexer:
    def __init__(self):
        self.characters = []

    def scan(self, line):
        self.characters = [char for char in line]
        tokens = []
        while self.characters:
            self.strip_whitespace()
            self.strip_comment()

            if self.characters and self.peek_next() in valid_token_characters:
                token = self.scan_token()
                tokens.append(token)
        return tokens

    def strip_whitespace(self):
        while self.characters and self.peek_next() in whitespace:
            self.get_next_character()

    def strip_comment(self):
        if self.characters and self.peek_next() == comment:
            while self.characters and self.get_next_character() != '\n':
                pass

    def scan_token(self):
        next_character = self.peek_next()

        if next_character in variable:
            token = self.scan_name()
        elif next_character in numbers:
            token = self.scan_number()
        elif next_character in delimiter_tokens:
            token = self.scan_delimiter()
        return token

    def scan_label(self):
        self.get_next_character()
        name = self.scan_generic(variable)
        return TokenLabel(name)

    def scan_number(self):
        name = self.scan_generic(numbers)
        return TokenConstant(int(name))

    def scan_name(self):
        name = self.scan_generic(variable)
        return self.get_token(name)

    def scan_delimiter(self):
        return delimiter_tokens[self.get_next_character()]

    def scan_generic(self, token_type):
        name = ''
        while self.characters and self.peek_next() in token_type:
            character = self.get_next_character()
            name += character
        return name

    def peek_next(self):
        character = self.characters[0]
        if character not in valid_characters:
            raise LexerError(f'{character} not a valid character')
        return character

    def get_next_character(self):
        return self.characters.pop(0)

    @staticmethod
    def get_token(name):
        if name in command_tokens:
            token = command_tokens[name]
        elif name in register_tokens:
            token = register_tokens[name]
        else:
            token = TokenLabel(name)
        return token


class LexerError(Exception):
    pass


def main():
    path = 'test3.eas'

    with open(path, 'r') as file:
        for line in file:
            for char in line:
                print(repr(char))


if __name__ == '__main__':
    main()