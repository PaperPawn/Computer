import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap, QPolygon
from PyQt5.QtCore import Qt, QTimer, QPoint, QObject, QThread, pyqtSignal

from computer.utility.status_gui import StatusWindow
from computer.emulator import make_emulator


class Window(QMainWindow):
    def __init__(self, emulator):
        super().__init__()

        left = 1200
        top = 400
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
        # self.run_thread_task()
        # self.set_pixels()

        self.start_automatic_refresh()

    def start_automatic_refresh(self):
        timer = QTimer(self)
        # timer.timeout.connect(self.run_emulation)
        timer.timeout.connect(self.update_screen)
        timer.start(100)

    # def run_emulation(self):
    #     cycles = 10
    #     if not self.emulator.shutdown:
    #         print(f'running {cycles} cycles')
    #         for i in range(cycles):
    #             self.emulator.tick()
    #     print(f'shutdown: {self.emulator.shutdown}')
    #     self.set_pixels()

    def update_screen(self):
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

    def run_thread_task(self,):
        # Step 2: Create a QThread object
        self.thread = QThread()

        # Step 3: Create a worker object
        self.worker = Worker(self.emulator)

        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)

        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)

        # Step 6: Start the thread
        self.thread.start()


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, emulator):
        super().__init__()
        self.emulator = emulator

    def run(self):
        pass
        # print('running emulator')
        # self.emulator.run()


def main():
    app = QApplication(sys.argv)

    emulator = make_emulator('ball.bin')
    _window = Window(emulator)
    status_window = StatusWindow(emulator)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
