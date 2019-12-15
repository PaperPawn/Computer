import pytest

from computer.chips.arithmetic import half_adder, full_adder, ADD16, INC16


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
    truth_table = [([0]*16, [0]*16, [0]*16),
                   ([0]*16, [1]*16, [1]*16),
                   ([1]*16, [0]*16, [1]*16),
                   ([1]*16, [1]*16, [1]*15 + [0]),
                   ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]),

                   ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]),

                   ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]),

                   ([0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1],
                    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1])]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_add16(self, a, b, expected):
        assert ADD16(a, b) == expected


class TestInc16:
    truth_table = [([0]*16, [0]*15 + [1]),
                   ([0]*15 + [1], [0]*14 + [1, 0]),
                   ([0] + [1]*15, [1] + [0]*15),
                   ([1]*16, [0]*16),

                   ([0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1]),

                   ([0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1],
                    [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0])
                   ]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_add16(self, a, expected):
        assert INC16(a) == expected
