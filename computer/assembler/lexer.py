from computer.assembler.tokens import (Token, Keyword, Delimiter,
                                       Literal, Label)

variable_chars = 'abcdefghijklmnopqrstuvwqxyz_'
numbers = '1234567890'
whitespace = ' \n\t'
comment = '%'

keyword_tokens = {token.value: token for token in Keyword}
delimiter_tokens = {token.value: token for token in Delimiter}

delimiters = ''.join(delimiter_tokens)
valid_token_characters = variable_chars + numbers + delimiters
valid_characters = valid_token_characters + whitespace + comment


class Lexer:
    def __init__(self):
        self.characters = []
        self.line = 1

    def scan(self, line):
        self.characters = [char for char in line]
        self.line = 1
        tokens = []
        while self.characters:
            self.strip_whitespace()
            self.strip_comment()

            if self.characters and self.peek_next() in valid_token_characters:
                token = self.scan_token()
                if type(token) == tuple:
                    tokens.extend(token)
                else:
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

        if next_character in variable_chars:
            token = self.scan_name()
        elif next_character in numbers:
            token = self.scan_number()
        elif next_character in delimiter_tokens:
            token = self.scan_delimiter()
        return token

    def scan_name(self):
        name = self.scan_generic(variable_chars)
        return self.get_token(name)

    def scan_number(self):
        name = self.scan_generic(numbers)
        return self.make_token(Literal.Int, int(name))

    def scan_delimiter(self):
        character = self.get_next_character()
        return self.make_token(delimiter_tokens[character], character)

    def scan_generic(self, characters):
        name = ''
        while self.characters and self.peek_next() in characters:
            character = self.get_next_character()
            name += character
        return name

    def peek_next(self):
        character = self.characters[0]
        if character not in valid_characters:
            raise LexerError(f'Unexpected character in line {self.line}'
                             f'{character} is not a valid character')
        return character

    def get_next_character(self):
        character = self.characters.pop(0)
        if character == '\n':
            self.line += 1
        return character

    def get_token(self, name):
        if name in keyword_tokens:
            token = keyword_tokens[name]
        else:
            token = Label.Name
        return self.make_token(token, name)

    def make_token(self, token_type, value):
        return Token(token_type, value, self.line)


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