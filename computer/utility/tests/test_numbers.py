import pytest

from bitarray import bitarray

from computer.utility.numbers import dec_to_bin, bin_to_dec


class TestNumbers:
    dec_bin = [(0, bitarray('0000000000000000')),
               (1, bitarray('0000000000000001')),
               (2, bitarray('0000000000000010')),
               (13, bitarray('0000000000001101')),
               (22, bitarray('0000000000010110')),
               (345, bitarray('0000000101011001')),
               (23567, bitarray('0101110000001111')),
               (65535, bitarray('1111111111111111'))
               ]

    @pytest.mark.parametrize('dec, binary', dec_bin)
    def test_dec_to_bin(self, dec, binary):
        assert dec_to_bin(dec) == binary

    @pytest.mark.parametrize('dec, binary', dec_bin)
    def test_bin_to_dec(self, dec, binary):
        assert bin_to_dec(binary) == dec
