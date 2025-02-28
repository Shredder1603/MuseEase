from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QDialog
from PyQt6.QtGui import QPixmap
import os
from PyQt6 import uic


class Main_Menu(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        # Load the Main Menu UI
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/MainMenu.ui')
        uic.loadUi(ui_path, self)

        # Set up the exit button functionality
        self.exit_button = getattr(self, "exit_button")
        self.exit_button.clicked.connect(self.on_exit_requested)
        self.exit_requested_callback = None

        # Connect "Open File" button to opening SavedProjects UI
        self.open_file_button = getattr(self, "open_file_button")
        self.open_file_button.clicked.connect(self.on_open_saved_projects)

        # Track the Saved Projects UI window
        self.saved_projects_window = None  

        self.setWindowTitle("PyQt6 Background Image")
        self.setGeometry(100, 100, 800, 500)

        # Create QLabel for background
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Get the path of the background image relative to the UI file
        bg_image_path = os.path.join(os.path.dirname(ui_path), 'background.jpg')

        # Load and scale the background image
        self.bg_pixmap = QPixmap(bg_image_path)
        self.update_background()

        # Ensure the QLabel is behind all other widgets
        self.bg_label.lower()

    def on_open_saved_projects(self):
        """Open the SavedProjects UI when 'open_file_button' is clicked, but only if it is not already open."""
        if self.saved_projects_window is None or not self.saved_projects_window.isVisible():
            saved_projects_path = os.path.join(os.path.dirname(__file__), 'UI/SavedProjects.ui')
            self.saved_projects_window = QDialog(self)  # Create a new window for SavedProjects
            uic.loadUi(saved_projects_path, self.saved_projects_window)
            self.saved_projects_window.setWindowTitle("Saved Projects")
            self.saved_projects_window.show()  # Show the dialog without blocking execution

    # Handle window resizing
    def resizeEvent(self, event):
        """Resize the background dynamically when the window is resized."""
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        """Scale the background image to fit the window size."""
        self.bg_label.setGeometry(0, 0, self.width(), self.height())  # Match window size
        scaled_pixmap = self.bg_pixmap.scaled(self.width(), self.height())
        self.bg_label.setPixmap(scaled_pixmap)

    # Exit program call and response
    def set_exit_callback(self, callback):
        self.exit_requested_callback = callback

    def on_exit_requested(self):
        if self.exit_requested_callback:
            self.exit_requested_callback()

    def execute_exit(self):
        self.close()


class New_Project(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
