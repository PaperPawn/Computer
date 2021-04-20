from enum import Enum
from collections import namedtuple
# TokenKeyword = Enum('TokenKeyword', 'Shutdown Reset Move Push Pop '
#                                     'Add Sub And Or Xor Negate Inc Dec '
#                                     'Jump JumpIfZero JumpIfNeg JumpIfOverflow '
#                                     'HddRead HddWrite HddSector '
#                                     'a b c d sp')
# TokenRegister = Enum('TokenRegister', 'a b c d sp')
# TokenDelimiter = Enum('TokenDelimiter', 'LeftBracket RightBracket Colon')

Token = namedtuple('Token', ('type', 'value', 'line'))


class Keyword(Enum):
    Shutdown = 'shutdown'
    Reset = 'reset'
    Move = 'move'
    Push = 'push'
    Pop = 'pop'
    Add = 'add'
    Sub = 'sub'
    And = 'and'
    Or = 'or'
    Xor = 'xor'
    Not = 'not'
    Negate = 'neg'
    Inc = 'inc'
    Dec = 'dec'
    Compare = 'compare'
    Jump = 'jump'
    JumpIfZero = 'jump_zero'
    JumpIfNeg = 'jump_neg'
    JumpIfOverflow = 'jump_overflow'
    Call = 'call'
    Return = 'return'
    HddRead = 'hddread'
    HddWrite = 'hddwrite'
    HddSector = 'hddsector'
    a = 'a'
    b = 'b'
    c = 'c'
    d = 'd'
    sp = 'sp'


class Delimiter(Enum):
    LeftBracket = '['
    RightBracket = ']'
    Colon = ':'


class Literal(Enum):
    Int = 'int'


class Name(Enum):
    Label = 'label'
