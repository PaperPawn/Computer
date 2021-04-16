from enum import Enum, auto


class TokenKeyword(Enum):
    Shutdown = auto()
    Reset = auto()
    Move = auto()
    Push = auto()
    Pop = auto()
    Jump = auto()
    Add = auto()
    Sub = auto()
    And = auto()
    Or = auto()
    Xor = auto()
    Negate = auto()
    Inc = auto()
    Dec = auto()
    JumpIfZero = auto()
    JumpIfNeg = auto()
    JumpIfOverflow = auto()
    HddRead = auto()
    HddWrite = auto()
    HddSector = auto()


class TokenRegister(Enum):
    a = auto()
    b = auto()
    c = auto()
    d = auto()
    sp = auto()


class TokenDelimiter(Enum):
    LeftBracket = auto()
    RightBracket = auto()
    Colon = auto()


class TokenInt:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value


class TokenLabel:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value
