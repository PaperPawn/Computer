from bitarray import bitarray
from computer.utility.numbers import bin_to_dec

from computer.chips.memory import Register # RAM8K, RAM32K


# noinspection PyAttributeOutsideInit
class _RAM:
    def __call__(self, value, address, load):
        i = self.get_index(address)
        old_value = self.bits[i*16:(i+1)*16]
        if load:
            self.next.append((i, value))
        return old_value

    def tick(self):
        for i, value in self.next:
            self.bits[i*16:(i+1)*16] = value
        self.next = []


class RAM8K(_RAM):
    def __init__(self):
        self.bits = bitarray(2**13 * 16)
        self.next = []

    @staticmethod
    def get_index(address):
        return bin_to_dec(bitarray('000') + address)


class RAM32K(_RAM):
    def __init__(self):
        self.bits = bitarray(2**15 * 16)
        self.next = []

    @staticmethod
    def get_index(address):
        return bin_to_dec(bitarray('0') + address)


class CombinedRAM:
    def __init__(self):
        self.ram = RAM32K()
        self.screen = RAM8K()
        self.keyboard = Register()

    def __call__(self, value, address, load):
        if address[0]:
            if address[2]:
                old_value = self.keyboard(value, load)
            else:
                old_value = self.screen(value, address[3:], load)
        else:
            old_value = self.ram(value, address[1:], load)
        return old_value

    def tick(self):
        self.ram.tick()
        self.screen.tick()
        self.keyboard.tick()
