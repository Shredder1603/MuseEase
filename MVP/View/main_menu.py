# MVP/View/main_menu.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QApplication
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from paths import resource_path 
import os

class Main_Menu(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()

        # Construct the path to the UI file
        ui_path = resource_path('MVP/View/UI/MainMenu.ui')  
        print(f"UI Path: {ui_path}")  # Debug print to confirm the path
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found at: {ui_path}")
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            raise RuntimeError(f"Failed to load UI file {ui_path}: {str(e)}")

        # Initialize the background label
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Set up button functionality
        self.exit_button = getattr(self, "exit_button")
        self.exit_button.clicked.connect(self.on_exit_requested)
        self.exit_requested_callback = None

        self.open_file_button = getattr(self, "open_file_button")
        self.open_file_button.clicked.connect(self.on_open_saved_projects_requested)
        self.open_saved_projects_callback = None

        self.new_project_button = getattr(self, "new_project_button")
        self.new_project_button.clicked.connect(self.on_new_project_requested)
        self.new_project_callback = None

        # Track the Saved Projects UI window
        self.saved_projects_window = None  

        self.setWindowTitle("MuseEase")

        # Set the window to fullscreen
        self.showFullScreen()

        # Background setup
        bg_image_path = resource_path('MVP/View/UI/background.jpg')  
        print(f"Background Image Path: {bg_image_path}")  # Debug print

        # Check if the background image file exists
        if os.path.exists(bg_image_path):
            self.bg_pixmap = QPixmap(bg_image_path)
            self.update_background()
        else:
            print(f"Warning: Background image '{bg_image_path}' not found.")

        # Ensure background is placed behind all widgets
        self.bg_label.lower()

    def resizeEvent(self, event):
        """Resize the background dynamically when the window is resized."""
        if hasattr(self, 'bg_pixmap'):
            self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        """Scale the background image to fit the window size."""
        if hasattr(self, 'bg_pixmap'):
            self.bg_label.setGeometry(0, 0, self.width(), self.height())  
            scaled_pixmap = self.bg_pixmap.scaled(self.width(), self.height())
            self.bg_label.setPixmap(scaled_pixmap)

    def set_exit_callback(self, callback):
        self.exit_requested_callback = callback

    def on_exit_requested(self):
        if self.exit_requested_callback:
            self.exit_requested_callback()

    def execute_exit(self):
        QApplication.quit()

    def set_open_saved_projects_callback(self, callback):
        self.open_saved_projects_callback = callback

    def on_open_saved_projects_requested(self):
        if self.open_saved_projects_callback:
            self.open_saved_projects_callback()

    def set_new_project_callback(self, callback):
        self.new_project_callback = callback

    def on_new_project_requested(self):
        if self.new_project_callback:
            self.new_project_callback()
