import sys
from PyQt6.QtWidgets import QApplication
from MVP.Model.model import Model
from MVP.View.view import View
from MVP.presenter import Presenter


def main():
    app = QApplication(sys.argv)
    model = Model()
    view = View()
    presenter = Presenter(model, view)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    