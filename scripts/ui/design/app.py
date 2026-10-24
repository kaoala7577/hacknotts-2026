import sys

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

from main_window import Ui_MainWindow


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    mainW = Ui_MainWindow()
    mainW.setupUi(window)
    window.show()
    sys.exit(app.exec())
