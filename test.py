import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel

class PopupWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Load the popup UI from popup.ui
        ui_path = os.path.join(os.path.dirname(__file__), 'UI\Popup.ui')
        uic.loadUi(ui_path, self)
        # Connect the popup button's clicked signal to a function
        self.button2.clicked.connect(self.on_popup_button_clicked)

    def on_popup_button_clicked(self):
        print("Working")
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the main UI from main.ui
        ui_path = os.path.join(os.path.dirname(__file__), 'UI\Test.ui')
        uic.loadUi(ui_path, self)
        # Connect the main button's clicked signal to open the popup
        self.button1.clicked.connect(self.open_popup)

    def open_popup(self):
        # Create an instance of the popup widget
        self.popup = PopupWidget()
        # Show the popup as a non-modal window. Adjust properties as needed.
        self.popup.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
