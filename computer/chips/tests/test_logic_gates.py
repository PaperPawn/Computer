import pytest

from bitarray import bitarray
from computer.chips.logic_gates import NAND, NOT, AND, OR, XOR, MUX, DMUX


class TestNand:
    truth_table = [(0, 0, 1),
                   (0, 1, 1),
                   (1, 0, 1),
                   (1, 1, 0)]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_nand(self, a, b, expected):
        assert NAND(a, b) == expected


class TestNot:
    truth_table = [(0, 1),
                   (1, 0)]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_not(self, a, expected):
        assert NOT(a) == expected


class TestAnd:
    truth_table = [(0, 0, 0),
                   (0, 1, 0),
                   (1, 0, 0),
                   (1, 1, 1)]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_and(self, a, b, expected):
        assert AND(a, b) == expected


class TestOr:
    truth_table = [(0, 0, 0),
                   (0, 1, 1),
                   (1, 0, 1),
                   (1, 1, 1),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_or(self, a, b, expected):
        assert OR(a, b) == expected


class TestXOr:
    truth_table = [(0, 0, 0),
                   (0, 1, 1),
                   (1, 0, 1),
                   (1, 1, 0)]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_xor(self, a, b, expected):
        assert XOR(a, b) == expected


class TestMux:
    truth_table = [(0, 0, 0, 0),
                   (0, 1, 0, 0),
                   (1, 0, 0, 1),
                   (1, 1, 0, 1),
                   (0, 0, 1, 0),
                   (0, 1, 1, 1),
                   (1, 0, 1, 0),
                   (1, 1, 1, 1)]

    @pytest.mark.parametrize('a, b, sel, expected', truth_table)
    def test_mux(self, a, b, sel, expected):
        assert MUX(a, b, sel) == expected


class TestDMux:
    truth_table = [(0, 0, bitarray('00')),
                   (0, 1, bitarray('00')),
                   (1, 0, bitarray('10')),
                   (1, 1, bitarray('01')),
                   ]

    @pytest.mark.parametrize('a, sel, expected', truth_table)
    def test_dmux(self, a, sel, expected):
        assert DMUX(a, sel) == expected
