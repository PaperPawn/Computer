import pytest
# import pytest_mock

from bitarray import bitarray

from computer.chips.memory import Register, RAM8, RAM64, RAM512, RAM4K, RAM8K, RAM32K, CombinedRAM, PC
from computer.utility.numbers import dec_to_bin

from computer.chips.tests import ZEROS, ONES, INT_ONE, INT_TWO, INT_THREE, INT_NEG_TWO, ALTERNATING_ONE_ZERO, ALTERNATING_ZERO_ONE

UNUSED = bitarray(16)


class TestRegister:

    def test_get_inital_value(self):
        register = Register()

        garbage = register(UNUSED, 0)
        assert register(UNUSED, 0) == garbage

        register.tick()
        garbage = register(UNUSED, 0)
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(UNUSED, 0) == garbage

    values = [ZEROS, ONES, INT_ONE, INT_TWO]

    @pytest.mark.parametrize('value', values)
    def test_set_then_get_value(self, value):
        register = Register()

        garbage = register(value, 1)
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(UNUSED, 0) == value

        register.tick()
        assert register(UNUSED, 0) == value

    def test_set_then_get_multiple_values(self):
        register = Register()

        garbage = register(ZEROS, 1)
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(ONES, 1) == ZEROS

        register.tick()
        assert register(INT_ONE, 1) == ONES

        register.tick()
        assert register(UNUSED, 0) == INT_ONE

        register.tick()
        assert register(UNUSED, 0) == INT_ONE

    def test_set_twice_in_same_tick(self):
        register = Register()

        garbage = register(ZEROS, 1)
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(ONES, 1) == ZEROS
        assert register(INT_ONE, 1) == ZEROS

        register.tick()
        assert register(UNUSED, 0) == INT_ONE

    def test_get_the_set_in_same_tick(self):
        register = Register()

        garbage = register(ZEROS, 1)
        assert register(UNUSED, 0) == garbage

        register.tick()
        assert register(UNUSED, 0) == ZEROS
        assert register(ONES, 1) == ZEROS

        register.tick()
        assert register(UNUSED, 0) == ONES


class TestRam8:

    values = [ZEROS, ONES, INT_ONE, INT_TWO]
    addresses = [bitarray('000'), bitarray('001'), bitarray('010'),
                 bitarray('011'), bitarray('100'), bitarray('101'),
                 bitarray('110'), bitarray('111')]

    @pytest.mark.parametrize('value', values)
    @pytest.mark.parametrize('address', addresses)
    def test_set_then_get_one_address(self, value, address):
        ram = RAM8()

        ram(value, address, 1)

        ram.tick()

        assert ram(UNUSED, address, 0) == value

    @pytest.mark.parametrize('address', addresses[1:])
    def test_set_then_get_two_addresses(self, address):
        ram = RAM8()

        ram(INT_ONE, self.addresses[0], 1)
        ram(INT_TWO, address, 1)

        ram.tick()

        assert ram(UNUSED, self.addresses[0], 0) == INT_ONE
        assert ram(UNUSED, address, 0) == INT_TWO

    def test_set_then_get_all_addresses(self):
        ram = RAM8()

        values = [ZEROS, ONES, INT_ONE, INT_TWO, INT_THREE, INT_NEG_TWO,
                  ALTERNATING_ONE_ZERO, ALTERNATING_ZERO_ONE]

        for value, adress, in zip(values, self.addresses):
            ram(value, adress, 1)

        ram.tick()

        for value, adress, in zip(values, self.addresses):
            assert ram(UNUSED, adress, 0) == value

    def test_set_then_get_multiple_values(self):
        ram = RAM8()

        ram(INT_ONE, self.addresses[0], 1)
        ram(INT_TWO, self.addresses[1], 1)

        ram.tick()

        assert ram(INT_THREE, self.addresses[0], 1) == INT_ONE
        assert ram(INT_NEG_TWO, self.addresses[1], 1) == INT_TWO

        ram.tick()

        assert ram(UNUSED, self.addresses[0], 0) == INT_THREE
        assert ram(UNUSED, self.addresses[1], 0) == INT_NEG_TWO


class TestRam64:

    values = [ZEROS, ONES, INT_ONE, INT_TWO]
    addresses = [bitarray('000'), bitarray('001'), bitarray('010'),
                 bitarray('011'), bitarray('100'), bitarray('101'),
                 bitarray('110'), bitarray('111')]

    class RAM8MOCK:
        def __init__(self):
            self.ticked = 0

        def __call__(self, value, address, load):
            self.received_value = value
            self.received_address = address
            self.received_load = load
            return value

        def tick(self):
            self.ticked += 1

    values = [# ZEROS, ONES,
              INT_ONE,
              # INT_TWO,
              ]
    addresses = [(0, bitarray('000000')),
                 (1, bitarray('001000')),
                 (2, bitarray('010000')),
                 (3, bitarray('011000')),
                 (4, bitarray('100000')),
                 (5, bitarray('101000')),
                 (6, bitarray('110000')),
                 (7, bitarray('111000'))]

    @pytest.mark.parametrize('value', values)
    @pytest.mark.parametrize('i, address', addresses)
    def test_set_then_get(self, monkeypatch, value, i, address):
        ram = RAM64()

        monkeypatch.setattr(ram, 'rams', [self.RAM8MOCK() for _ in range(8)])

        ram(value, address, 1)
        assert ram.rams[i].received_value == value
        assert ram.rams[i].received_address == bitarray('000')
        assert ram.rams[i].received_load == 1

        ram.tick()
        assert ram.rams[i].ticked == 1

        assert ram(UNUSED, address, 0) == UNUSED
        assert ram.rams[i].received_value == UNUSED
        assert ram.rams[i].received_address == bitarray('000')
        assert ram.rams[i].received_load == 0

    def test_set_then_get_no_mock(self):
        ram = RAM64()

        value_1 = INT_ONE
        address_1 = bitarray('100101')

        value_2 = INT_TWO
        address_2 = bitarray('001101')

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2


class TestRam512:
    def test_set_then_get_no_mock(self):
        ram = RAM512()

        value_1 = INT_ONE
        address_1 = bitarray('100101101')

        value_2 = INT_TWO
        address_2 = bitarray('001001101')

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2


class TestRam4K:
    def test_set_then_get_no_mock(self):
        ram = RAM4K()

        value_1 = INT_ONE
        address_1 = bitarray('110101011101')

        value_2 = INT_TWO
        address_2 = bitarray('100100011101')

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2


class TestRam8K:
    def test_set_then_get_no_mock(self):
        ram = RAM8K()

        value_1 = INT_ONE
        address_1 = bitarray('1101011011101')

        value_2 = INT_TWO
        address_2 = bitarray('1001010011101')

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2


class TestRam32K:
    def test_set_then_get_no_mock(self):
        ram = RAM32K()

        value_1 = INT_ONE
        address_1 = bitarray('011101010111101')

        value_2 = INT_TWO
        address_2 = bitarray('001100100011101')

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2


class TestCombinedRAM:
    def test_set_then_get_no_mock(self):
        ram = CombinedRAM()

        # Up to 32 767 -> 32K Ram
        # From 32768 to 40959 -> 8K Screen memory
        # 40960 -> Keyboard register
        # 40960+ -> Mapping?

        value_1 = INT_ONE
        value_2 = INT_TWO
        value_3 = dec_to_bin(48)
        value_4 = dec_to_bin(63)

        address_1 = dec_to_bin(4735)
        address_2 = dec_to_bin(32767)
        screen_address = dec_to_bin(32768)
        keyboard_address = dec_to_bin(40960)

        ram(value_1, address_1, 1)
        ram(value_2, address_2, 1)
        ram(value_3, screen_address, 1)
        ram(value_4, keyboard_address, 1)

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2
        assert ram(UNUSED, screen_address, 0) == value_3
        assert ram(UNUSED, keyboard_address, 0) == value_4

        ram.tick()

        assert ram(UNUSED, address_1, 0) == value_1
        assert ram(UNUSED, address_2, 0) == value_2
        assert ram(UNUSED, screen_address, 0) == value_3
        assert ram(UNUSED, keyboard_address, 0) == value_4

        assert ram.screen(UNUSED, ZEROS, 0) == value_3
        assert ram.keyboard(UNUSED, 0) == value_4


class TestProgramCounter:
    def test_no_change(self):
        pc = PC()

        load = 0
        inc = 0
        reset = 0

        assert pc(UNUSED, load, inc, reset) == ZEROS

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == ZEROS

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == ZEROS

    def test_inc(self):
        pc = PC()

        load = 0
        inc = 1
        reset = 0

        assert pc(UNUSED, load, inc, reset) == ZEROS

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == INT_ONE

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == INT_TWO

    def test_load(self):
        pc = PC()

        value = INT_TWO
        load = 1
        inc = 0
        reset = 0

        assert pc(value, load, inc, reset) == ZEROS

        pc.tick()
        assert pc(UNUSED, 0, inc, reset) == value

        pc.tick()
        assert pc(UNUSED, 0, inc, reset) == value

    def test_reset(self):
        pc = PC()

        value = INT_TWO
        load = 0
        inc = 0
        reset = 1

        assert pc(value, 1, inc, 0) == ZEROS

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == INT_TWO

        pc.tick()
        assert pc(UNUSED, load, inc, reset) == ZEROS

    def test_reset_priority(self):
        pc = PC()

        value = INT_TWO
        assert pc(value, 1, 0, 0) == ZEROS

        pc.tick()
        assert pc(UNUSED, 1, 1, 1) == INT_TWO

        pc.tick()
        assert pc(UNUSED, 1, 1, 1) == ZEROS
