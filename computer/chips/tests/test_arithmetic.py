import pytest

from computer.chips.arithmetic import half_adder, full_adder


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