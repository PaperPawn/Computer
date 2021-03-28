from bitarray import bitarray

ZEROS = bitarray('0' * 16)
ONES = bitarray('1' * 16)

ALTERNATING_ZERO_ONE = bitarray('01' * 8)
ALTERNATING_ONE_ZERO = bitarray('10' * 8)

INT_ONE = bitarray('0000000000000001')
INT_TWO = bitarray('0000000000000010')
INT_THREE = bitarray('0000000000000011')

INT_NEG_ONE = ONES
INT_NEG_TWO = bitarray('1111111111111110')

