from PyQt6.QtCore import QObject


class Model(QObject):

    def __init__(self):
        super().__init__()
        self.input_str = "Nothing to see here..."

    def set_input_str(self, input: str):
        self.input_str = input

    def get_input_str(self):
        return self.input_str
