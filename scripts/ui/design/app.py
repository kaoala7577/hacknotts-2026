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

        self.camera_preview = QLabel()
        self.camera_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_preview.setText("Camera Preview")
        self.camera_preview.setMinimumSize(0, 240)
        self.central_layout.addWidget(self.camera_preview, stretch=1)

        self.camera_worker = CameraWorker(camera_index=1)
        self.camera_worker.frame_ready.connect(self.show_frame)
        self.camera_worker.start()

    def show_frame(self, image):
        pixmap = QPixmap.fromImage(image)

        self.camera_preview.setPixmap(pixmap.scaled(self.camera_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def closeEvent(self, event):
        if self.camera_worker.isRunning():
            self.camera_worker.stop()
            event.accept()

        super().closeEvent(event)




