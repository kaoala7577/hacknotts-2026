# import everything
import os
import sys
from ui.design.app import Window
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


def setup_app_directories(): pass # make sure folders exist 

# def apply_global_styles(app: QApplication): pass 

def main(): 
	setup_app_directories() 
	app = QApplication(sys.argv)
	main_window = Window()
	main_window.show()

	sys.exit(app.exec())

# set up qt application loop 

# initialise database 

# initialise cv engine 

# instantiate main window 

if __name__ == "__main__": 
	main() 