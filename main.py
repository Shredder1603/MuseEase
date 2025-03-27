# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from MVP.Model.model import Model
from MVP.View import Main_Menu
from MVP.presenter import Presenter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.presenter = Presenter(stacked_widget=self.stacked_widget)
        self.setCentralWidget(self.stacked_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()