import sys
import os
import subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWebEngineWidgets import QWebEngineView

version = "1.0"

class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_path = os.path.join('ui', 'main.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading UI file: {e}")
            sys.exit(1)

        settings_icon = QIcon("theme/default/application/settings.png")
        self.settings.setIcon(settings_icon)

        terminal_icon = QIcon("theme/default/application/terminal.png")
        self.terminal.setIcon(terminal_icon)

        wallpaper_pixmap = QPixmap("theme/default/wallpaper.jpg")
        self.wallpaper.setPixmap(wallpaper_pixmap)

        self.settings_widget = Settings(self)
        self.settings_widget.setVisible(False)

        self.terminal_widget = Terminal(self)
        self.terminal_widget.setVisible(False)

        self.mimc_widget = Mimc(self)
        self.mimc_widget.setVisible(True)

        self.main_layout = QVBoxLayout(self.centralWidget())
        self.main_layout.addWidget(self.settings_widget)

        self.settings.clicked.connect(self.toggle_settings)
        self.terminal.clicked.connect(self.toggle_terminal)

        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(1.3)
        self.taskbar.setGraphicsEffect(self.blur_effect)

    def toggle_settings(self):
        if self.settings_widget.isVisible():
            self.animate_close_settings()
        else:
            self.animate_open_settings()

    def animate_open_settings(self):
        self.settings_widget.setVisible(True)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.settings_widget.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setDuration(100)
        self.animation.start()

    def animate_close_settings(self):
        if not hasattr(self, 'opacity_effect'):
            self.opacity_effect = QGraphicsOpacityEffect()
            self.settings_widget.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setDuration(100)
        self.animation.finished.connect(self.finish_close_stop)
        self.animation.start()

    def finish_close_stop(self):
        self.settings_widget.setVisible(False)

    def toggle_terminal(self):
        if self.terminal_widget.isVisible():
            self.animate_close_terminal()
        else:
            self.animate_open_terminal()

    def animate_open_terminal(self):
        self.terminal_widget.setVisible(True)
        self.opacity_effect = QGraphicsOpacityEffect()
        self.terminal_widget.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setDuration(100)
        self.animation.start()

    def animate_close_terminal(self):
        if not hasattr(self, 'opacity_effect'):
            self.opacity_effect = QGraphicsOpacityEffect()
            self.terminal_widget.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.setDuration(100)
        self.animation.finished.connect(self.finish_close_terminal)
        self.animation.start()

    def finish_close_terminal(self):
        self.terminal_widget.setVisible(False)

class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        ui_path = os.path.join('ui', 'application', 'settings.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading widget UI: {e}")
            sys.exit(1)

        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(1.3)
        self.setGraphicsEffect(self.blur_effect)

        self.version.setText(f"Version: {version}")

        self.dragging = False
        self.offset = QPoint(0, 0)
        self.animation = None
        self.Close.clicked.connect(parent.toggle_settings)

        self.titlebar = self.findChild(QWidget, "titlebar")
        if self.titlebar:
            self.titlebar.setMouseTracking(True)
            self.titlebar.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.titlebar:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.dragging = True
                self.offset = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self.dragging:
                if self.animation:
                    self.animation.stop()
                new_pos = event.globalPos() - self.offset
                self.animation = QPropertyAnimation(self, b"pos")
                self.animation.setStartValue(self.pos())
                self.animation.setEndValue(new_pos)
                self.animation.setDuration(100)
                self.animation.start()
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.dragging = False
                return True
        return super().eventFilter(obj, event)

class Terminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        ui_path = os.path.join('ui', 'application', 'terminal.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading widget UI: {e}")
            sys.exit(1)

        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(1.3)
        self.setGraphicsEffect(self.blur_effect)

        self.terminal_output = self.findChild(QPlainTextEdit, "commands")
        self.terminal_input = self.findChild(QLineEdit, "commands_2")

        if not self.terminal_output or not self.terminal_input:
            print("Error: terminal UI elements not found.")
            sys.exit(1)

        self.terminal_output.setReadOnly(True)
        self.terminal_input.returnPressed.connect(self.execute_command)

        self.process = subprocess.Popen(
            ["cmd"] if sys.platform == "win32" else ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        self.Close.clicked.connect(parent.toggle_terminal)

        self.worker = QThread()
        self.worker.run = self.read_output
        self.worker.start()

        self.dragging = False
        self.offset = QPoint(0, 0)
        self.animation = None

        self.titlebar = self.findChild(QWidget, "titlebar")
        if self.titlebar:
            self.titlebar.setMouseTracking(True)
            self.titlebar.installEventFilter(self)

    def read_output(self):
        for line in iter(self.process.stdout.readline, ''):
            self.terminal_output.appendPlainText(line.strip())

    def execute_command(self):
        command = self.terminal_input.text().strip()
        if command:
            self.terminal_output.appendPlainText(f"> {command}")
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            self.terminal_input.clear()

    def eventFilter(self, obj, event):
        if obj == self.titlebar:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.dragging = True
                self.offset = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self.dragging:
                if self.animation:
                    self.animation.stop()
                new_pos = event.globalPos() - self.offset
                self.animation = QPropertyAnimation(self, b"pos")
                self.animation.setStartValue(self.pos())
                self.animation.setEndValue(new_pos)
                self.animation.setDuration(100)
                self.animation.start()
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.dragging = False
                return True
        return super().eventFilter(obj, event)

class Mimc(QWidget): # Browser
    def __init__(self, parent=None):
        super().__init__(parent)

        ui_path = os.path.join('ui', 'application', 'mimc.ui')
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            print(f"Error loading widget UI: {e}")
            sys.exit(1)

        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(1.3)
        self.setGraphicsEffect(self.blur_effect)

        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://www.google.com"))

        self.dragging = False
        self.offset = QPoint(0, 0)
        self.animation = None
        self.Close.clicked.connect(parent.toggle_settings)

        self.titlebar = self.findChild(QWidget, "titlebar")
        if self.titlebar:
            self.titlebar.setMouseTracking(True)
            self.titlebar.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.titlebar:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.dragging = True
                self.offset = event.globalPos() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.MouseMove and self.dragging:
                if self.animation:
                    self.animation.stop()
                new_pos = event.globalPos() - self.offset
                self.animation = QPropertyAnimation(self, b"pos")
                self.animation.setStartValue(self.pos())
                self.animation.setEndValue(new_pos)
                self.animation.setDuration(100)
                self.animation.start()
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.dragging = False
                return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Eye_OS = Main()
    Eye_OS.show()
    sys.exit(app.exec_())
