import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap, QPolygon
from PyQt5.QtCore import Qt, QTimer, QPoint  # QObject, QThread, pyqtSignal

from computer.emulator import make_emulator


class Window(QMainWindow):
    def __init__(self, emulator):
        super().__init__()

        left = 300
        top = 300
        width = 512
        height = 256

        self.setGeometry(left, top, width, height)
        self.setWindowTitle("Computer Screen")

        self.setAutoFillBackground(True)
        self.set_background()

        self.screen = Screen(self, width, height, emulator)
        self.screen.move(0, 0)
        self.screen.resize(width, height)

        self.show()

    def set_background(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)


class Screen(QLabel):
    def __init__(self, parent, width, height, emulator):
        super().__init__(parent)
        self.screen_width = width
        self.screen_height = height
        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.emulator = emulator
        # self.set_pixels()

        self.start_automatic_refresh()

    def start_automatic_refresh(self):
        timer = QTimer(self)
        timer.timeout.connect(self.run_emulation)
        timer.start(100)

    def run_emulation(self):
        cycles = 10
        if not self.emulator.shutdown:
            print(f'running {cycles} cycles')
            for i in range(cycles):
                self.emulator.tick()
        print(f'shutdown: {self.emulator.shutdown}')
        self.set_pixels()

    def set_pixels(self):
        painter = QPainter(self.pixmap())
        self.clear_background(painter)

        painter.setPen(Qt.white)

        size_screen_ram = 8192  # self.screen_width * self.screen_height / 16

        x = y = 0
        # unused = bitarray(16)
        # print('Drawing pixels')
        points = []
        for i in range(size_screen_ram):
            # word = self.emulator.cpu.ram.screen(unused, dec_to_bin(i), load=0)
            word = self.emulator.cpu.ram.screen.bits[i*16:(i+1)*16]
            for bit in word:
                x += 1
                if x == self.screen_width:
                    x = 0
                    y += 1
                if bit:
                    points.append(QPoint(x, y))
                    # painter.drawPoint(x, y)
        painter.drawPoints(QPolygon(points))
        # print('finished')
        painter.end()
        self.update()

    def clear_background(self, painter):
        painter.setPen(Qt.black)
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                painter.drawPoint(x, y)


def main():
    app = QApplication(sys.argv)

    emulator = make_emulator()
    _window = Window(emulator)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
