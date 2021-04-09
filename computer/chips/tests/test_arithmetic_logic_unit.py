import pytest

from bitarray import bitarray
from computer.chips.arithmetic_logic_unit import ALU

from computer.chips.tests import (ZEROS, ONES, INT_ONE, INT_TWO,
                                  INT_NEG_ONE, INT_NEG_TWO,
                                  ALTERNATING_ONE_ZERO, ALTERNATING_ZERO_ONE)

UNUSED = bitarray(16)


class TestALU:
    truth_table_pass_through = [(INT_ONE, UNUSED, INT_ONE, (0, 0, 0)),
                                (ZEROS, UNUSED, ZEROS, (1, 0, 0)),
                                (INT_NEG_ONE, UNUSED, INT_NEG_ONE, (0, 1, 0)),
                                (INT_NEG_TWO, UNUSED, INT_NEG_TWO, (0, 1, 0)),
                                (INT_ONE, UNUSED, INT_ONE, (0, 0, 0)),
                                (INT_TWO, UNUSED, INT_TWO, (0, 0, 0))]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_pass_through)
    def test_alu_pass_through(self, a, b, expected_out, expected_status):
        opcode = bitarray('0000')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_negate = [(ZEROS, UNUSED, ZEROS, (1, 0, 0)),
                          (INT_ONE, UNUSED, INT_NEG_ONE, (0, 1, 0)),
                          (INT_TWO, UNUSED, INT_NEG_TWO, (0, 1, 0)),
                          (INT_NEG_ONE, UNUSED, INT_ONE, (0, 0, 0)),
                          (INT_NEG_TWO, UNUSED, INT_TWO, (0, 0, 0))]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_negate)
    def test_alu_negate(self, a, b, expected_out, expected_status):
        opcode = bitarray('0001')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_increment = [(ZEROS, UNUSED, INT_ONE, (0, 0, 0)),
                             (INT_ONE, UNUSED, INT_TWO, (0, 0, 0)),
                             (INT_NEG_ONE, UNUSED, ZEROS, (1, 0, 1)),
                             (INT_NEG_TWO, UNUSED, INT_NEG_ONE, (0, 1, 0)),
                             ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_increment)
    def test_alu_increment(self, a, b, expected_out, expected_status):
        opcode = bitarray('0010')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_decrement = [(INT_TWO, UNUSED, INT_ONE, (0, 0, 0)),
                             (INT_ONE, UNUSED, ZEROS, (1, 0, 0)),
                             (ZEROS, UNUSED, INT_NEG_ONE, (0, 1, 1)),
                             (INT_NEG_ONE, UNUSED, INT_NEG_TWO, (0, 1, 0)),
                             ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_decrement)
    def test_alu_decrement(self, a, b, expected_out, expected_status):
        opcode = bitarray('0011')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_add = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                       (INT_ONE, ZEROS, INT_ONE, (0, 0, 0)),
                       (ZEROS, INT_ONE, INT_ONE, (0, 0, 0)),
                       (INT_ONE, INT_ONE, INT_TWO, (0, 0, 0)),
                       (INT_NEG_ONE, INT_ONE, ZEROS, (1, 0, 1)),
                       (INT_NEG_TWO, INT_ONE, INT_NEG_ONE, (0, 1, 0)),
                       ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_add)
    def test_alu_add(self, a, b, expected_out, expected_status):
        opcode = bitarray('0100')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    # truth_table_sub = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
    #                    (INT_ONE, ZEROS, INT_NEG_ONE, (0, 1, 0)),
    #                    (ZEROS, INT_ONE, INT_ONE, (0, 0, 0)),
    #                    (INT_ONE, INT_ONE, ZEROS, (1, 0, 1)),
    #                    (INT_NEG_ONE, INT_ONE, INT_TWO, (0, 0, 0)),
    #                    (INT_ONE, INT_TWO, INT_ONE, (0, 0, 1)),
    #                    ]
    truth_table_sub = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                       (ZEROS, INT_ONE, INT_NEG_ONE, (0, 1, 0)),
                       (INT_ONE, ZEROS, INT_ONE, (0, 0, 0)),
                       (INT_ONE, INT_ONE, ZEROS, (1, 0, 1)),
                       (INT_ONE, INT_NEG_ONE, INT_TWO, (0, 0, 1)),
                       (INT_TWO, INT_ONE, INT_ONE, (0, 0, 0)),
                       ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_sub)
    def test_alu_sub(self, a, b, expected_out, expected_status):
        opcode = bitarray('0101')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    A = bitarray('0101101001100010')
    NOT_A = bitarray('1010010110011101')
    truth_table_bitflip = [(ZEROS, UNUSED, ONES, (0, 1, 0)),
                           (ONES, UNUSED, ZEROS, (1, 0, 0)),
                           (INT_ONE, UNUSED, INT_NEG_TWO, (0, 1, 0)),
                           (A, UNUSED, NOT_A, (0, 1, 0))
                           ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_bitflip)
    def test_alu_bitflip(self, a, b, expected_out, expected_status):
        opcode = bitarray('1001')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_and = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                       (ONES, ZEROS, ZEROS, (1, 0, 0)),
                       (ZEROS, ONES, ZEROS, (1, 0, 0)),
                       (ONES, ONES, ONES, (0, 1, 0)),
                       (INT_ONE, ONES, INT_ONE, (0, 0, 0)),
                       (A, ONES, A, (0, 0, 0)),
                       (A, NOT_A, ZEROS, (1, 0, 0))
                       ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_and)
    def test_alu_and(self, a, b, expected_out, expected_status):
        opcode = bitarray('1010')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_and_not_a = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                             (ONES, ZEROS, ZEROS, (1, 0, 0)),
                             (ZEROS, ONES, ONES, (0, 1, 0)),
                             (ONES, ONES, ZEROS, (1, 0, 0)),
                             (INT_ONE, ONES, INT_NEG_TWO, (0, 1, 0)),
                             ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_and_not_a)
    def test_alu_and_not_a(self, a, b, expected_out, expected_status):
        opcode = bitarray('1011')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_or = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                      (ONES, ZEROS, ONES, (0, 1, 0)),
                      (A, ZEROS, A, (0, 0, 0)),
                      (A, ONES, ONES, (0, 1, 0)),
                      (A, NOT_A, ONES, (0, 1, 0)),
                      ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_or)
    def test_alu_or(self, a, b, expected_out, expected_status):
        opcode = bitarray('1100')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_or_not_a = [(ZEROS, ZEROS, ONES, (0, 1, 0)),
                            (ONES, ZEROS, ZEROS, (1, 0, 0)),
                            (A, ZEROS, NOT_A, (0, 1, 0)),
                            (A, ONES, ONES, (0, 1, 0)),
                            (A, NOT_A, NOT_A, (0, 1, 0)),
                            ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_or_not_a)
    def test_alu_or_not_a(self, a, b, expected_out, expected_status):
        opcode = bitarray('1101')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_xor = [(ZEROS, ZEROS, ZEROS, (1, 0, 0)),
                       (ZEROS, ONES, ONES, (0, 1, 0)),
                       (ONES, ZEROS, ONES, (0, 1, 0)),
                       (ONES, ONES, ZEROS, (1, 0, 0)),
                       (ALTERNATING_ZERO_ONE, ONES, ALTERNATING_ONE_ZERO, (0, 1, 0)),
                       (ALTERNATING_ZERO_ONE, ZEROS, ALTERNATING_ZERO_ONE, (0, 0, 0)),
                       ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_xor)
    def test_alu_xor(self, a, b, expected_out, expected_status):
        opcode = bitarray('1110')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status

    truth_table_xor_not_a = [(ZEROS, ZEROS, ONES, (0, 1, 0)),
                             (ZEROS, ONES, ZEROS, (1, 0, 0)),
                             (ONES, ZEROS, ZEROS, (1, 0, 0)),
                             (ONES, ONES, ONES, (0, 1, 0)),
                             ]

    @pytest.mark.parametrize('a, b, expected_out, expected_status', truth_table_xor_not_a)
    def test_alu_xor_not_a(self, a, b, expected_out, expected_status):
        opcode = bitarray('1111')
        assert ALU(a, b, opcode) == (expected_out,) + expected_status
