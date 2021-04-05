from bitarray import bitarray

from computer.chips.memory import Register
from computer.utility.numbers import bin_to_dec


class HardDisk:
    def __init__(self, file_path):
        self.sector_size = 512

        self.data = bitarray()
        self.load_data(file_path)

        self.sector = Register()

    def load_data(self, file_path):
        with open(file_path, 'rb') as file:
            self.data.fromfile(file)

    def write_data(self, file_path):
        with open(file_path, 'wb') as file:
            self.data.tofile(file)

    def __call__(self, address, select_sector, value, write):
        sector = self.sector(address, select_sector)

        sector = bin_to_dec(sector)
        address = bin_to_dec(address)

        i = self.sector_size * sector + 16 * address

        if write:
            self.data[i:i+16] = value

        return self.data[i:i+16]

    def tick(self):
        self.sector.tick()
