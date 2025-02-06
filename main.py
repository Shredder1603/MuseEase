import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My PyQt App")
        self.setGeometry(100, 100, 400, 300)  # Window position & size

        label = QLabel("Hello, PyQt!", self)
        label.move(150, 130)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
    