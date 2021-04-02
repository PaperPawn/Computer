import os
import pytest
import filecmp

from bitarray import bitarray
from computer.io.harddisk import HardDisk

from computer.chips.tests import ZEROS, INT_ONE, INT_TWO

UNUSED = bitarray(16)


class TestHardDisk:
    @pytest.fixture
    def folder(self):
        return r'D:\Programmering\python\computer\computer\io\tests\data'

    files = [('test_16bits.bin', bitarray('1001000010001011')),
             ('test_16bits_zeros.bin', bitarray('0'*16))]

    @pytest.mark.parametrize('file_name, expected', files)
    def test_load_disk(self, folder, file_name, expected):
        file_path = os.path.join(folder, file_name)
        hd = HardDisk(file_path)

        assert hd.data == expected

    @pytest.mark.parametrize('file_name, expected', files)
    def test_read(self, folder, file_name, expected):
        file_path = os.path.join(folder, file_name)
        hd = HardDisk(file_path)

        address = bitarray('0'*16)
        select_sector = 1
        value = UNUSED
        write = 0
        hd(address, select_sector, value, write)

        hd.tick()
        select_sector = 0
        assert hd(address, select_sector, value, write) == expected

    read = [(ZEROS, ZEROS, bitarray('1011000011010100')),
            (ZEROS, INT_ONE, bitarray('0000001000010110')),
            (INT_ONE, ZEROS, bitarray('0101010010110010')),
            (INT_ONE, INT_ONE, bitarray('0000000000000000'))]

    @pytest.mark.parametrize('sector_address, data_address, expected', read)
    def test_read_sector(self, folder, sector_address, data_address, expected):
        file_name = 'test_2sectors.bin'
        file_path = os.path.join(folder, file_name)

        hd = HardDisk(file_path)

        select_sector = 1
        value = UNUSED
        write = 0
        hd(sector_address, select_sector, value, write)

        hd.tick()

        select_sector = 0
        assert hd(data_address, select_sector, value, write) == expected

    write = [('test_16bits.bin', ZEROS, ZEROS, INT_ONE, 1, INT_ONE),
             ('test_32bits.bin', ZEROS, ZEROS, INT_ONE, 1, INT_ONE + bitarray('0011000001100101')),
             ('test_32bits.bin', ZEROS, INT_ONE, INT_TWO, 1, bitarray('1000000010000110') + INT_TWO),
             ('test_32bits.bin', ZEROS, INT_ONE, INT_TWO, 0, bitarray('10000000100001100011000001100101'))]

    @pytest.mark.parametrize('file_name, sector_address, data_address, value, write, expected', write)
    def test_write(self, folder, file_name, sector_address, data_address, value, write, expected):
        file_path = os.path.join(folder, file_name)

        hd = HardDisk(file_path)
        select_sector = 1
        hd(sector_address, select_sector, UNUSED, 0)

        hd.tick()

        select_sector = 0
        hd(data_address, select_sector, value, write)

        assert hd.data == expected

    def test_write_disk(self, folder):
        file_name = 'test_16bits.bin'
        file_path = os.path.join(folder, file_name)

        out_file_name = 'test_16bits_out.bin'
        out_file_path = os.path.join(folder, out_file_name)

        hd = HardDisk(file_path)
        hd.write_data(out_file_path)

        assert os.path.exists(out_file_path)
        assert filecmp.cmp(file_path, out_file_path)
        os.remove(out_file_path)
