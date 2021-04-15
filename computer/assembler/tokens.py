from enum import Enum


class TokenKeyword(Enum):
    Shutdown = 1
    Reset = 2
    Move = 3
    Add = 4
    Sub = 5


class TokenRegister(Enum):
    a = 1
    b = 2
    c = 3
    d = 4
    sp = 5
    pc = 6


class TokenDelimiter(Enum):
    SemiColon = 1
    LeftBracket = 2
    RightBracket = 3


class TokenInt:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value
