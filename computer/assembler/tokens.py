from enum import Enum

TokenKeyword = Enum('TokenKeyword', 'Shutdown Reset Move Push Pop '
                                    'Add Sub And Or Xor Negate Inc Dec '
                                    'Jump JumpIfZero JumpIfNeg JumpIfOverflow '
                                    'HddRead HddWrite HddSector')
TokenRegister = Enum('TokenRegister', 'a b c d sp')
TokenDelimiter = Enum('TokenDelimiter', 'LeftBracket RightBracket Colon')


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
