import sys
import random
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt, QTimer, QObject, QThread, pyqtSignal

from bitarray import bitarray


class Window(QMainWindow):
    def __init__(self, width, height):
        super().__init__()

        left = 300
        top = 300
        # width = 600
        # height = 400

        self.setGeometry(left, top, width, height)
        self.setWindowTitle("Computer Screen")

        self.setAutoFillBackground(True)
        self.set_background()

        self.screen = Screen(self, width, height)
        self.screen.move(0, 0)
        self.screen.resize(width, height)

        self.show()

    def set_background(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

    def run_thread_task(self, width, height):
        print('Starting long task')
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(self.screen.bits, width, height)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()
        print('Thread started')

    def reportProgress(self, n):
        print(f"Long-Running Step: {n}")


class Screen(QLabel):
    def __init__(self, parent, width, height):
        super().__init__(parent)
        canvas = QPixmap(width, height)
        self.setPixmap(canvas)

        self.colors = [Qt.red, Qt.darkYellow, Qt.yellow, Qt.green, Qt.blue, Qt.white]
        self.bits = bitarray(width*height)

        self.circle_maker = CircleMaker(self.bits, width, height)
        self.start_automatic_refresh()

    def start_automatic_refresh(self):
        timer = QTimer(self)
        timer.timeout.connect(self.paint_circle)
        timer.start(100)

    # def paintEvent(self, event):
#         print(f'paint event: {event}')
        # self.set_pixels()

    # def set_bit_view(self, bits):
        # self.bits = bits

    def set_random_pixels(self):
        size = self.size()
        width = size.width()
        height = size.height()

        painter = QPainter(self.pixmap())
        self.clear_background(painter)

        painter.setPen(self.colors[0])

        for i in range(1024):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            painter.drawPoint(x, y)
        painter.end()
        self.update()

    def set_pixels(self):
        size = self.size()
        width = size.width()
        height = size.height()

        painter = QPainter(self.pixmap())
        # self.clear_background(painter)

        painter.setPen(self.colors[0])
        self.colors = self.colors[1:] + self.colors[:1]

        for x in range(width):
            for y in range(height):
                if self.bits[x + width * y]:
                    # print(x, y, x + width * y)
                    painter.drawPoint(x, y)
        painter.end()
        self.update()

    def clear_background(self, painter):
        size = self.size()
        width = size.width()
        height = size.height()

        painter.setPen(Qt.black)
        for x in range(width):
            for y in range(height):
                painter.drawPoint(x, y)

    def paint_circle(self):
        # print('Painting circle')
        self.circle_maker.make_circle()
        self.set_pixels()

    # def mouseMoveEvent(self, e):
    #     print(f'Screen: mouse mode event: {e}')
    #     painter = QPainter(self.pixmap())
    #     painter.setPen(Qt.white)
    #     painter.drawPoint(e.x(), e.y())
    #     painter.end()
    #     self.update()


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, bits, width, height):
        super().__init__()
        self.bits = bits
        self.width = width
        self.height = height

        self.circle_maker = CircleMaker(bits, width, height)
    # def run(self):
    #     for i in range(5):
    #         time.sleep(1)
    #         self.progress.emit(i + 1)
    #     self.finished.emit()

    def run(self):
        center = (self.width / 2, self.height / 2)
        radius = 0
        while True:
            if radius > 300:
                radius = 0
            radius += 5
            self.circle_maker.make_circle(center, radius)

    def print_random_pixels(self):
        size = len(self.bits)
        while True:
            time.sleep(0.01)
            i = random.randint(0, size)
            self.bits[i] = not self.bits[i]
            # self.progress.emit(i + 1)
        self.finished.emit()


class CircleMaker:
    def __init__(self, bits, width, height):
        self.bits = bits
        self.width = width
        self.height = height

        self.x_center = width / 2
        self.y_center = height / 2
        self.radius = 0

    def make_circle(self):
        self.bits.setall(0)

        if self.radius > 300:
            self.radius = 0
        self.radius += 5
        half_thickness = 2
        for x in range(self.width):
            for y in range(self.height):
                inner = (self.radius - half_thickness) ** 2
                outer = (self.radius + half_thickness) ** 2
                if inner < (x - self.x_center) ** 2 + (y - self.y_center) ** 2 < outer:
                    self.bits[x + self.width * y] = 1


def main():
    # screen = Screen()
    # screen.show()

    app = QApplication(sys.argv)

    width = 600
    height = 400
    window = Window(width, height)
    # window.screen.bits.setall(0)
    # window.run_thread_task(width, height)

    # bits = window.screen.bits
    # bits = bitarray(width*height)
    # print('Setting bits to zero')
    # bits.setall(0)

    # window.screen.set_pixels()

    # window.screen.set_pixels()
    # window.screen.update()

    # for i in range(10):
#         window.screen.set_pixels()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
