# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from screenshot_app import ScreenshotApp

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ScreenshotApp()
    ex.show()
    sys.exit(app.exec_())
