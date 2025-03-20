# MVP/View/tutorial.py
from PyQt6.QtWidgets import QDialog, QWidget, QPushButton
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
import os

class Tutorial(QDialog, QWidget):
    def __init__(self, presenter=None):
        super().__init__()
        
        # Store a reference to the presenter
        self.presenter = presenter
        
        # Load the UI from the .ui file
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ui_path = os.path.join(project_root, 'MVP', 'View', 'UI', 'Tutorial.ui')
        print(f"UI Path: {ui_path}")  # Debug print
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found at: {ui_path}")
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            raise RuntimeError(f"Failed to load UI file {ui_path}: {str(e)}")
        
        icons_dir = os.path.join(project_root, 'MVP', 'View', 'Icons', 'Tutorial_Icons')
        forward_path = os.path.join(icons_dir, 'FastForward.png')
        forward_png = QPixmap(forward_path)
        self.forward.setPixmap(forward_png)
        
        rewind_path = os.path.join(icons_dir, 'Rewind.png')
        rewind_png = QPixmap(rewind_path)
        self.rewind.setPixmap(rewind_png)
        
        record_path = os.path.join(icons_dir, 'Record.png')
        record_png = QPixmap(record_path)
        self.record.setPixmap(record_png)
        
        play_path = os.path.join(icons_dir, 'Play.png')
        play_png = QPixmap(play_path)
        self.play.setPixmap(play_png)
        
        metro_path = os.path.join(icons_dir, 'Metronome.png')
        metro_png = QPixmap(metro_path)
        self.metro.setPixmap(metro_png)
        
        drag_path = os.path.join(icons_dir, 'Drag_drop.png')
        drag_png = QPixmap(drag_path)
        self.Drag.setPixmap(drag_png)

        # Find buttons and labels in the UI
        self.close_button = self.findChild(QPushButton, 'back')

        # Connect the buttons to their respective methods
        self.close_button.clicked.connect(self.close_tutorial)

    def close_tutorial(self):
        """Close the tutorial window and notify the presenter."""
        if self.presenter:
            self.presenter.on_tutorial_closed()
        self.close()