from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSignal


class View(QDialog):
    input_data_collected = pyqtSignal(str)
