import sys
from PyQt6.QtWidgets import QApplication
from MVP.Model.model import Model
from MVP.View.view import Main_Menu
from MVP.presenter import Presenter


def main():
    app = QApplication(sys.argv)
    model = Model()
    view = Main_Menu()
    presenter = Presenter(model, view)
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    