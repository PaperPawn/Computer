import sys
import os

from bitarray import bitarray

from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QPushButton)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot # QTimer, QObject, QThread, pyqtSignal,

from computer.emulator import Emulator, get_hdd_with_test_program, get_bootloader
from computer.chips.central_processing_unit import CPU
from computer.chips.memory import RAM32K

from computer.utility.status import decode_instruction
from computer.utility.strings import get_bitarray_string
from computer.utility.numbers import dec_to_bin, bin_to_dec

NULL = bitarray(16)


class StatusWindow(QMainWindow):
    def __init__(self, emulator):
        super().__init__()

        self.emulator = emulator
        left = 300
        top = 300
        width = 800
        height = 600

        self.setGeometry(left, top, width, height)
        self.setWindowTitle('Emulator status')

        self.registers = QLabel(self)
        self.instructions = QListWidget(self)
        self.decoded = QListWidget(self)

        self.instructions_shown = 100# 20
        self.instructions_label = QLabel(self)
        self.decoded_label = QLabel(self)

        self.load_button = QPushButton(self)
        self.run_button = QPushButton(self)
        self.run_until_button = QPushButton(self)
        self.until_input = QLineEdit(self)
        self.next_button = QPushButton(self)
        self.reset_button = QPushButton(self)

        self.setup_registers_label()
        self.setup_instructions_list()
        self.setup_buttons()

        # label.setAlignment(Qt.AlignCenter)
        # vbox = QVBoxLayout()
        # vbox.addWidget(label)
        # vbox.addStretch()

        # self.setLayout(vbox)
        self.set_instructions()
        self.update()
        self.show()

    def setup_buttons(self):
        self.load_button.setText('Load')

        self.reset_button.setText('Reset')
        self.reset_button.move(100, 0)
        self.reset_button.clicked.connect(self.on_reset)

        self.run_button.setText('Run')
        self.run_button.move(200, 0)
        self.run_button.clicked.connect(self.on_run)

        self.next_button.setText('Next')
        self.next_button.move(300, 0)
        self.next_button.clicked.connect(self.on_next)

        self.run_until_button.setText('Run until')
        self.run_until_button.move(400, 0)
        self.run_until_button.clicked.connect(self.on_run_until)

        self.until_input.setText('0')
        self.until_input.move(500, 0)

    def setup_instructions_list(self):
        instructions_x = 400
        instructions_y = 40
        instructions_width = 150
        instructions_height = 350

        font_size = 12
        gap = 20

        self.instructions_label.setText('Instructions')
        self.instructions_label.setFont(QFont('MS Shell Dlg', font_size))
        self.instructions_label.move(instructions_x, instructions_y)

        self.instructions_label.resize(instructions_width, gap)
        self.instructions.move(instructions_x, instructions_y + gap)
        self.instructions.resize(instructions_width, instructions_height)

        decoded_x = instructions_x + instructions_width + 10
        decoded_y = instructions_y
        decoded_width = 150
        decoded_heigh = instructions_height

        self.decoded_label.setText('Decoded')
        self.decoded_label.setFont(QFont('MS Shell Dlg', font_size))
        self.decoded_label.move(decoded_x, decoded_y)
        self.decoded_label.resize(decoded_width, gap)

        self.decoded.move(decoded_x, decoded_y + gap)
        self.decoded.resize(decoded_width, decoded_heigh)

    def setup_registers_label(self):
        # self.fill_background(self.registers)
        # self.set_register_values()
        # print(self.label.font().toString())
        # MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0
        self.registers.setFont(QFont('MS Shell Dlg', 16))
        self.registers.setAlignment(Qt.AlignTop)
        x = 10
        y = 40
        height = 500
        width = 400
        self.registers.move(x, y)
        self.registers.resize(width, height)

    def set_register_values(self):
        registers = {'a': self.emulator.cpu.a.value,
                     'b': self.emulator.cpu.b.value,
                     'c': self.emulator.cpu.c.value,
                     'd': self.emulator.cpu.d.value,
                     'pc': self.emulator.cpu.pc.register.value,
                     'sp': self.emulator.cpu.sp.value}
        bins = {}
        dec = {}
        pointers = {}
        p_dec = {}
        for register in registers:
            value = registers[register]
            bins[register] = get_bitarray_string(value)
            dec[register] = bin_to_dec(value)

            memory = self.emulator.cpu.ram_bus(NULL, value, 0)
            pointers[register] = get_bitarray_string(memory)
            p_dec[register] = bin_to_dec(memory)

        pc = f"pc:\t{bins['pc']}, {dec['pc']}"
        sp = f"sp:\t{bins['sp']}, {dec['sp']}"
        general_registers = '\n'.join([f'{register}:\t{bins[register]}, {dec[register]}'
                                       for register in ['a', 'b', 'c', 'd']])
        pcp = f"[pc]:\t{pointers['pc']}, {p_dec['pc']}"
        spp = f"[sp]:\t{pointers['sp']}, {p_dec['sp']}"
        gr_pointers = '\n'.join([f'[{register}]:\t{pointers[register]}, {p_dec[register]}'
                                 for register in ['a', 'b', 'c', 'd']])
        text = f'Registers:\n{pc}\n{sp}\n{general_registers}' \
               f'\n\nPointers:\n{pcp}\n{spp}\n{gr_pointers}'
        self.registers.setText(text)

    def set_instructions(self):
        last_decoded = ''
        for i in range(self.instructions_shown):
            address = dec_to_bin(i)
            instruction = self.emulator.cpu.ram_bus(NULL, address, 0)
            if 'constant' in last_decoded:
                decoded = str(bin_to_dec(instruction))
            else:
                decoded = decode_instruction(instruction)

            self.add_instruction(f'{i}: {get_bitarray_string(instruction)}')
            self.add_decoded(f'{i}: {decoded}')
            last_decoded = decoded

    def update_instructions(self):
        last_decoded = ''
        for i in range(self.instructions_shown):
            address = dec_to_bin(i)
            instruction = self.emulator.cpu.ram_bus(NULL, address, 0)
            if 'constant' in last_decoded:
                decoded = str(bin_to_dec(instruction))
            else:
                decoded = decode_instruction(instruction)
            self.instructions.item(i).setText(f'{i}: {get_bitarray_string(instruction)}')
            self.decoded.item(i).setText(f'{i}: {decoded}')
            last_decoded = decoded

    def highlight_current_instruction(self):
        pc = bin_to_dec(self.emulator.cpu.pc.register.value)
        self.instructions.item(pc).setSelected(True)
        self.decoded.item(pc).setSelected(True)

    def add_instruction(self, instruction):
        item = QListWidgetItem(instruction)
        self.instructions.addItem(item)

    def add_decoded(self, decoded):
        item = QListWidgetItem(decoded)
        self.decoded.addItem(item)

    def fill_background(self, widget):
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        widget.setPalette(p)
        widget.setAutoFillBackground(True)

    def update(self):
        self.set_register_values()
        self.update_instructions()
        self.highlight_current_instruction()

    @pyqtSlot()
    def on_next(self):
        self.emulator.tick()
        self.update()

    @pyqtSlot()
    def on_run(self):
        self.emulator.run()
        self.update()

    @pyqtSlot()
    def on_run_until(self):
        instruction = int(self.until_input.text())
        current_instruction = 0
        shutdown = False
        while not shutdown and current_instruction != instruction:
            shutdown = self.emulator.tick()
            current_instruction = bin_to_dec(self.emulator.cpu.pc.register.value)
        self.update()

    @pyqtSlot()
    def on_reset(self):
        self.emulator.reset()
        self.update()


def main():
    app = QApplication(sys.argv)

    ram = RAM32K()

    hdd = get_hdd_with_test_program()

    cpu = CPU(ram, hdd)
    emulator = Emulator(cpu)

    bootloader = get_bootloader()
    emulator.load_binary(bootloader)
    # emulator.load_instructions(bootloader)

    # file_name = 'test.bin'
    # file_path = os.path.join(r'D:\Programmering\python\computer\computer\assembler',
    #                          file_name)
    # binary = bitarray(0)
    # with open(file_path, 'rb') as file:
    #     binary.fromfile(file)
    # instructions=[]
    # for i in range(int(len(binary)/16)):
    #     instruction = binary[i * 16:(i + 1) * 16]
    #     instructions.append(instruction)
    # emulator.load_instructions(instructions[1:])

    window = StatusWindow(emulator)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
