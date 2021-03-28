import pytest

from bitarray import bitarray

from computer.chips.arithmetic import half_adder, full_adder, ADD16, INC16

from computer.chips.tests import ZEROS, ONES, INT_ONE, INT_TWO, INT_THREE


class TestHalfAdder:
    truth_table = [(0, 0, 0, 0),
                   (0, 1, 1, 0),
                   (1, 0, 1, 0),
                   (1, 1, 0, 1)]

    @pytest.mark.parametrize('a, b, expected_sum, expected_carry', truth_table)
    def test_half_adder(self, a, b, expected_sum, expected_carry):
        assert half_adder(a, b) == (expected_sum, expected_carry)


class TestFullAdder:
    truth_table = [(0, 0, 0, 0, 0),
                   (0, 0, 1, 1, 0),
                   (0, 1, 0, 1, 0),
                   (0, 1, 1, 0, 1),
                   (1, 0, 0, 1, 0),
                   (1, 0, 1, 0, 1),
                   (1, 1, 0, 0, 1),
                   (1, 1, 1, 1, 1)]

    @pytest.mark.parametrize('a, b, c, expected_sum, expected_carry', truth_table)
    def test_full_adder(self, a, b, c, expected_sum, expected_carry):
        assert full_adder(a, b, c) == (expected_sum, expected_carry)


class TestAdd16:
    INT_OVERFLOW = bitarray('1' * 15 + '0')

    INT_A = bitarray('0000001011010010')
    INT_B = bitarray('0000000011001011')
    INT_C = bitarray('0000001110011101')

    truth_table = [(ZEROS, ZEROS, ZEROS),
                   (ZEROS, ONES, ONES),
                   (ONES, ZEROS, ONES),
                   (ONES, ONES, INT_OVERFLOW),
                   (ZEROS, INT_ONE, INT_ONE),
                   (INT_ONE, INT_ONE, INT_TWO),
                   (INT_TWO, INT_ONE, INT_THREE),
                   (INT_A, INT_B, INT_C)]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_add16(self, a, b, expected):
        assert ADD16(a, b) == expected


class TestInc16:
    INT_32767 = bitarray('0' + '1' * 15)
    INT_32768 = bitarray('1' + '0' * 15)
    INT_Ap0 = bitarray('0000001011010010')
    INT_Ap1 = bitarray('0000001011010011')
    INT_Ap2 = bitarray('0000001011010100')
    truth_table = [(ZEROS, INT_ONE),
                   (INT_ONE, INT_TWO),
                   (INT_32767, INT_32768),
                   (ONES, ZEROS),
                   (INT_Ap0, INT_Ap1),
                   (INT_Ap1, INT_Ap2)
                   ]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_inc16(self, a, expected):
        assert INC16(a) == expected
