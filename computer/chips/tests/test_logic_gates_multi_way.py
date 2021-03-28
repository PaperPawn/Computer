import pytest

from bitarray import bitarray
from computer.chips.logic_gates_multi_way import OR8WAY, MUX4WAY16, MUX8WAY16, DMUX4WAY, DMUX8WAY

ZEROS = bitarray('0' * 16)
ONES = bitarray('1' * 16)
ALTERNATING_ONE_ZERO = bitarray('10' * 8)


class TestOr8Way:
    truth_table = [(bitarray('00000000'), 0),
                   (bitarray('11111111'), 1),
                   (bitarray('00000001'), 1),
                   (bitarray('00000010'), 1),
                   (bitarray('00000100'), 1),
                   (bitarray('00001000'), 1),
                   (bitarray('00010000'), 1),
                   (bitarray('00100000'), 1),
                   (bitarray('01000000'), 1),
                   (bitarray('10000000'), 1)]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_or8way(self, a, expected):
        assert OR8WAY(a) == expected


class TestMux4Way16:
    truth_table = [(ZEROS, ZEROS, ZEROS, ZEROS, bitarray('00'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS, bitarray('01'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS, bitarray('10'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS, bitarray('11'), ZEROS),
                   (ONES, ZEROS, ZEROS, ZEROS, bitarray('00'), ONES),
                   (ZEROS, ONES, ZEROS, ZEROS, bitarray('01'), ONES),
                   (ZEROS, ZEROS, ONES, ZEROS, bitarray('10'), ONES),
                   (ZEROS, ZEROS, ZEROS, ONES, bitarray('11'), ONES),
                   (ONES, ALTERNATING_ONE_ZERO, ONES, ONES, bitarray('01'), ALTERNATING_ONE_ZERO)]

    @pytest.mark.parametrize('a, b, c, d, sel, expected', truth_table)
    def test_mux4way16(self, a, b, c, d, sel, expected):
        assert MUX4WAY16(a, b, c, d, sel) == expected


class TestMux8Way16:
    truth_table = [(ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('000'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('001'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('010'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('011'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('100'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('101'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('110'), ZEROS),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('111'), ZEROS),
                   (ONES, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('000'), ONES),
                   (ZEROS, ONES, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('001'), ONES),
                   (ZEROS, ZEROS, ONES, ZEROS,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('010'), ONES),
                   (ZEROS, ZEROS, ZEROS, ONES,
                    ZEROS, ZEROS, ZEROS, ZEROS, bitarray('011'), ONES),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ONES, ZEROS, ZEROS, ZEROS, bitarray('100'), ONES),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ONES, ZEROS, ZEROS, bitarray('101'), ONES),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ONES, ZEROS, bitarray('110'), ONES),
                   (ZEROS, ZEROS, ZEROS, ZEROS,
                    ZEROS, ZEROS, ZEROS, ONES, bitarray('111'), ONES),
                   ]

    @pytest.mark.parametrize('a, b, c, d, e, f, g, h, sel, expected', truth_table)
    def test_mux8way16(self, a, b, c, d, e, f, g, h, sel, expected):
        assert MUX8WAY16(a, b, c, d, e, f, g, h, sel) == expected


class TestDMux4Way:
    truth_table = [(0, bitarray('00'), bitarray('0000')),
                   (0, bitarray('01'), bitarray('0000')),
                   (0, bitarray('10'), bitarray('0000')),
                   (0, bitarray('11'), bitarray('0000')),

                   (1, bitarray('00'), bitarray('1000')),
                   (1, bitarray('01'), bitarray('0100')),
                   (1, bitarray('10'), bitarray('0010')),
                   (1, bitarray('11'), bitarray('0001')),
                   ]

    @pytest.mark.parametrize('a, sel, expected', truth_table)
    def test_dmux4way(self, a, sel, expected):
        assert DMUX4WAY(a, sel) == expected


class TestDMux8Way:
    truth_table = [(0, bitarray('000'), bitarray('00000000')),
                   (0, bitarray('001'), bitarray('00000000')),
                   (0, bitarray('010'), bitarray('00000000')),
                   (0, bitarray('011'), bitarray('00000000')),
                   (0, bitarray('100'), bitarray('00000000')),
                   (0, bitarray('101'), bitarray('00000000')),
                   (0, bitarray('110'), bitarray('00000000')),
                   (0, bitarray('111'), bitarray('00000000')),

                   (1, bitarray('000'), bitarray('10000000')),
                   (1, bitarray('001'), bitarray('01000000')),
                   (1, bitarray('010'), bitarray('00100000')),
                   (1, bitarray('011'), bitarray('00010000')),
                   (1, bitarray('100'), bitarray('00001000')),
                   (1, bitarray('101'), bitarray('00000100')),
                   (1, bitarray('110'), bitarray('00000010')),
                   (1, bitarray('111'), bitarray('00000001')),
                   ]

    @pytest.mark.parametrize('a, sel, expected', truth_table)
    def test_dmux8way(self, a, sel, expected):
        assert DMUX8WAY(a, sel) == expected
