import sys

from bitarray import bitarray

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap, QPolygon
from PyQt5.QtCore import Qt, QTimer, QPoint, QObject, QThread, pyqtSignal

from computer.utility.status_gui import StatusWindow
from computer.emulator import make_emulator
from computer.utility.numbers import bin_to_dec


class Window(QMainWindow):
    def __init__(self, worker):
        super().__init__()

        left = 1200
        top = 400
        width = 512
        height = 256

        self.setGeometry(left, top, width, height)
        self.setWindowTitle("Computer Screen")

        self.setAutoFillBackground(True)
        self.set_background()

        self.screen = Screen(self, width, height, worker)
        self.screen.move(0, 0)
        self.screen.resize(width, height)

        self.show()

    def set_background(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)


class Screen(QLabel):
    request_screen_memory = pyqtSignal()

    def __init__(self, parent, width, height, worker):
        super().__init__(parent)
        self.screen_width = width
        self.screen_height = height
        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.request_screen_memory.connect(worker.send_screen_memory)
        worker.send_screen_memory_signal.connect(self.set_screen_memory)

        self.bits = bitarray()

        self.start_automatic_refresh()

    def start_automatic_refresh(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_screen)
        timer.start(1000)

    def update_screen(self):
        self.set_pixels()

    def set_screen_memory(self, bits):
        self.bits = bits

    def set_pixels(self):
        painter = QPainter(self.pixmap())
        self.clear_background(painter)

        painter.setPen(Qt.white)

        size_screen_ram = 8192  # self.screen_width * self.screen_height / 16

        x = y = 0
        points = []
        self.request_screen_memory.emit()
        for i in range(size_screen_ram):
            word = self.bits[i * 16:(i + 1) * 16]
            for bit in word:
                x += 1
                if x == self.screen_width:
                    x = 0
                    y += 1
                if bit:
                    points.append(QPoint(x, y))
                    # painter.drawPoint(x, y)
        painter.drawPoints(QPolygon(points))
        painter.end()
        self.update()

    def clear_background(self, painter):
        painter.setPen(Qt.black)
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                painter.drawPoint(x, y)


class Worker(QObject):
    finished = pyqtSignal()
    send_update = pyqtSignal()
    send_screen_memory_signal = pyqtSignal(bitarray)
    send_memory_signal = pyqtSignal(bitarray)
    send_registers_signal = pyqtSignal(dict)

    def __init__(self, file_name):
        super().__init__()
        self.emulator = make_emulator(file_name)
        self.running = False
        self.do_tick = False
        self.do_update = False
        self.stop_at = 0

    def start(self):
        self._run()

    def _run(self):
        while True:
            while (self.running or self.do_tick) and not self.emulator.shutdown:
                self.do_update = True
                self._tick(1)
                if self.stop_at:
                    current_instruction = bin_to_dec(self.emulator.cpu.pc.register.value)
                    if current_instruction == self.stop_at:
                        self.running = False
                        self.stop_at = 0
                if self.do_tick:
                    self.do_tick = False
            if self.emulator.shutdown:
                self.running = False
            if self.do_update:
                self.update()
                self.do_update = False

    def update(self):
        self.send_memory()
        self.send_registers()
        self.send_update.emit()

    def run(self):
        self.running = True

    def tick(self):
        self.do_tick = True

    def _tick(self, number):
        for i in range(number):
            self.emulator.tick()

    def run_until(self, instruction):
        self.stop_at = instruction
        self.running = True

    def reset(self):
        self.emulator.reset()
        self.update()

    def send_screen_memory(self):
        self.send_screen_memory_signal.emit(self.emulator.cpu.ram.screen.bits) #.copy())

    def send_memory(self):
        self.send_memory_signal.emit(self.emulator.cpu.ram.ram.bits.copy())

    def send_registers(self):
        registers = {'a': self.emulator.cpu.a.value.copy(),
                     'b': self.emulator.cpu.b.value.copy(),
                     'c': self.emulator.cpu.c.value.copy(),
                     'd': self.emulator.cpu.d.value.copy(),
                     'pc': self.emulator.cpu.pc.register.value.copy(),
                     'sp': self.emulator.cpu.sp.value.copy()}
        self.send_registers_signal.emit(registers)


def main():
    app = QApplication(sys.argv)

    worker = Worker('ball.bin')
    _window = Window(worker)
    status_window = StatusWindow(worker)

    status_window.run_thread_task()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
