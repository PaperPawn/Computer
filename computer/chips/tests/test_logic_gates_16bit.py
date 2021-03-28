import pytest
from bitarray import bitarray

from computer.chips.logic_gates_16bit import NOT16, AND16, OR16, XOR16, MUX16

from computer.chips.tests import ZEROS, ONES, ALTERNATING_ZERO_ONE, ALTERNATING_ONE_ZERO


class TestNot16:
    truth_table = [(ZEROS, ONES),
                   (ONES, ZEROS),
                   (ALTERNATING_ZERO_ONE, ALTERNATING_ONE_ZERO),
                   (bitarray('0010110111011100'),
                    bitarray('1101001000100011'))]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_not16(self, a, expected):
        assert NOT16(a) == expected


class TestAnd16:
    truth_table = [(ZEROS, ZEROS, ZEROS),
                   (ZEROS, ONES, ZEROS),
                   (ONES, ZEROS, ZEROS),
                   (ONES, ONES, ONES),
                   (ALTERNATING_ZERO_ONE, ONES, ALTERNATING_ZERO_ONE),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_and16(self, a, b, expected):
        assert AND16(a, b) == expected


class TestOr16:
    truth_table = [(ZEROS, ZEROS, ZEROS),
                   (ZEROS, ONES, ONES),
                   (ONES, ZEROS, ONES),
                   (ONES, ONES, ONES),
                   (ALTERNATING_ZERO_ONE, ONES, ONES),
                   (ALTERNATING_ZERO_ONE, ZEROS, ALTERNATING_ZERO_ONE),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_or16(self, a, b, expected):
        assert OR16(a, b) == expected


class TestXOr16:
    truth_table = [(ZEROS, ZEROS, ZEROS),
                   (ZEROS, ONES, ONES),
                   (ONES, ZEROS, ONES),
                   (ONES, ONES, ZEROS),
                   (ALTERNATING_ZERO_ONE, ONES, ALTERNATING_ONE_ZERO),
                   (ALTERNATING_ZERO_ONE, ZEROS, ALTERNATING_ZERO_ONE),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_xor16(self, a, b, expected):
        assert XOR16(a, b) == expected


class TestMux16:
    truth_table = [(ZEROS, ZEROS, 0, ZEROS),
                   (ZEROS, ZEROS, 1, ZEROS),
                   (ONES, ZEROS, 0, ONES),
                   (ONES, ZEROS, 1, ZEROS),
                   (ALTERNATING_ZERO_ONE, ONES, 0, ALTERNATING_ZERO_ONE),
                   (ALTERNATING_ZERO_ONE, ONES, 1, ONES)]

    @pytest.mark.parametrize('a, b, sel, expected', truth_table)
    def test_mux16(self, a, b, sel, expected):
        assert MUX16(a, b, sel) == expected
