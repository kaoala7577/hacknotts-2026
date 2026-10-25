import sys

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout

from PyQt6.QtGui import QPixmap

from PyQt6.QtCore import Qt

from ui.design.main_window import Ui_MainWindow

from workers import CameraWorker


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.central_layout = QVBoxLayout(self.ui.centralwidget)
        self.central_layout.addWidget(self.ui.widget)

    def closeEvent(self, event):
        if self.camera_worker.isRunning():
            self.camera_worker.stop()
            event.accept()

        super().closeEvent(event)




