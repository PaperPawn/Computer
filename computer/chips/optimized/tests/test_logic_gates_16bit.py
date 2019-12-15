import pytest

from computer.chips.optimized.logic_gates_16bit import NOT16, AND16, OR16, MUX16


class TestNot16:
    truth_table = [([0]*16, [1]*16),
                   ([1]*16, [0]*16),
                   ([0, 1]*8, [1, 0]*8),
                   ([0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0],
                    [1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1])]

    @pytest.mark.parametrize('a, expected', truth_table)
    def test_not16(self, a, expected):
        assert NOT16(a) == expected


class TestAnd16:
    truth_table = [([0]*16, [0]*16, [0]*16),
                   ([0]*16, [1]*16, [0]*16),
                   ([1]*16, [0]*16, [0]*16),
                   ([1]*16, [1]*16, [1]*16),
                   ([0, 1]*8, [1]*16, [0, 1]*8),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_and16(self, a, b, expected):
        assert AND16(a, b) == expected


class TestOr16:
    truth_table = [([0]*16, [0]*16, [0]*16),
                   ([0]*16, [1]*16, [1]*16),
                   ([1]*16, [0]*16, [1]*16),
                   ([1]*16, [1]*16, [1]*16),
                   ([0, 1]*8, [1]*16, [1]*16),
                   ([0, 1]*8, [0]*16, [0, 1]*8),
                   ]

    @pytest.mark.parametrize('a, b, expected', truth_table)
    def test_or16(self, a, b, expected):
        assert OR16(a, b) == expected


class TestMux16:
    truth_table = [([0]*16, [0]*16, 0, [0]*16),
                   ([0]*16, [0]*16, 1, [0]*16),
                   ([1]*16, [0]*16, 0, [1]*16),
                   ([1]*16, [0]*16, 1, [0]*16),
                   ([0, 1]*8, [1]*16, 0, [0, 1]*8),
                   ([0, 1]*8, [1]*16, 1, [1]*16)]

    @pytest.mark.parametrize('a, b, sel, expected', truth_table)
    def test_mux16(self, a, b, sel, expected):
        assert MUX16(a, b, sel) == expected
