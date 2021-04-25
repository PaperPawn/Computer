from bitarray import bitarray

from computer.chips.arithmetic import INC16
from computer.chips.logic_gates import AND, DMUX
from computer.chips.logic_gates_16bit import MUX16
from computer.chips.logic_gates_multi_way import DMUX8WAY, MUX8WAY16
from computer.io import screen_demo


class Register:
    def __init__(self):
        self.value = bitarray(16)
        self.next_value = bitarray(16)

    def __call__(self, value, load):
        self.next_value = MUX16(self.next_value, value, load)
        return self.value.copy()

    def tick(self):
        self.value = self.next_value.copy()


class RAM8:
    def __init__(self):
        self.registers = [Register() for _ in range(8)]

    def __call__(self, value, address, load):
        dmux_load = DMUX8WAY(load, address)

        out0 = self.registers[0](value, dmux_load[0])
        out1 = self.registers[1](value, dmux_load[1])
        out2 = self.registers[2](value, dmux_load[2])
        out3 = self.registers[3](value, dmux_load[3])
        out4 = self.registers[4](value, dmux_load[4])
        out5 = self.registers[5](value, dmux_load[5])
        out6 = self.registers[6](value, dmux_load[6])
        out7 = self.registers[7](value, dmux_load[7])

        return MUX8WAY16(out0, out1, out2, out3, out4, out5, out6, out7, address)

    def tick(self):
        for register in self.registers:
            register.tick()


class RAM8X:
    def __init__(self):
        ram_type = self.get_ram_type()
        self.rams = [(ram_type()) for _ in range(8)]

    def _call_slower(self, value, address, load):
        dmux_load = DMUX8WAY(load, address)

        out = []
        for i in range(8):
            out.append(self.rams[i](value, address[3:], dmux_load[i]))

        return MUX8WAY16(out[0], out[1], out[2], out[3],
                         out[4], out[5], out[6], out[7], address)

    def _call_faster(self, value, address, load):
        dmux_load = DMUX8WAY(1, address)
        i = dmux_load.index(1)
        return self.rams[i](value, address[3:], load)
    __call__ = _call_faster

    def tick(self):
        for ram in self.rams:
            ram.tick()


class RAM2X:
    def __init__(self):
        ram_type = self.get_ram_type()
        self.rams = [(ram_type()) for _ in range(2)]

    def _call_slower(self, value, address, load):
        dmux_load = DMUX(load, address)

        out = []
        for i in range(2):
            out.append(self.rams[i](value, address[1:], dmux_load[i]))

        return MUX16(out[0], out[1], address)

    def _call_faster(self, value, address, load):
        # dmux_load = DMUX(1, address)
        # i = dmux_load.index(1)
        return self.rams[address[0]](value, address[1:], load)
    __call__ = _call_faster

    def tick(self):
        for ram in self.rams:
            ram.tick()


class RAM64(RAM8X):
    @staticmethod
    def get_ram_type():
        return RAM8


class RAM512(RAM8X):
    @staticmethod
    def get_ram_type():
        return RAM64


class RAM4K(RAM8X):
    @staticmethod
    def get_ram_type():
        return RAM512


class RAM8K(RAM2X):
    @staticmethod
    def get_ram_type():
        return RAM4K


class RAM32K(RAM8X):
    @staticmethod
    def get_ram_type():
        return RAM4K


class CombinedRAM:
    def __init__(self):
        self.ram = RAM32K()
        self.screen = RAM8K()
        self.keyboard = Register()

    def __call__(self, value, address, load):
        screen_keyboard_or_ram = DMUX(1, address[0])
        is_ram = screen_keyboard_or_ram[0]
        screen_keyboard = screen_keyboard_or_ram[1]

        screen_or_keyboard = DMUX(screen_keyboard, address[2])
        is_screen = screen_or_keyboard[0]
        is_keyboard = screen_or_keyboard[1]

        ram_load = AND(load, is_ram)
        screen_load = AND(load, is_screen)
        keyboard_load = AND(load, is_keyboard)

        ram_value = self.ram(value, address[1:], ram_load)
        screen_value = self.screen(value, address[3:], screen_load)
        keyboard_value = self.keyboard(value, keyboard_load)

        screen_keyboard_value = MUX16(keyboard_value, screen_value, is_screen)
        value = MUX16(screen_keyboard_value, ram_value, is_ram)
        return value

    def tick(self):
        self.ram.tick()
        self.screen.tick()
        self.keyboard.tick()


class PC:
    def __init__(self):
        self.register = Register()
        self.init_value = bitarray('0' * 16)
        self.register(self.init_value, 1)
        self.register.tick()

    def __call__(self, value, load, inc, reset):
        out = self.register(value, load)

        out_inc, _ = INC16(out)
        self.register(out_inc, inc)
        self.register(self.init_value, reset)
        return out

    def tick(self):
        self.register.tick()