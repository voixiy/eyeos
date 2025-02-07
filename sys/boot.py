import sys
import os
import subprocess # Module to run multiple python codes
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import time
import json

print("Loading EyeOS")

with open('config.json', 'r') as file:
    config = json.load(file)

class BootScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join('ui', 'boot.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading UI file: {e}")
            sys.exit(1)

        boot_icon = QPixmap("theme/boot/icon.png")
        self.booticon.setPixmap(boot_icon)

        QTimer.singleShot(3000, self.load)

    def load(self):
        if config["dev_mode"] != "true":
            subprocess.Popen(["python", "main.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(["python", "main.py"])

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    boot_screen = BootScreen()
    boot_screen.show()
    sys.exit(app.exec_())
