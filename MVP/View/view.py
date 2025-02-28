from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QDialog, QPushButton, QListView, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
from MVP.View.daw_test import DAWTest
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Main_Menu(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()

        # Load the Main Menu UI
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/MainMenu.ui')
        uic.loadUi(ui_path, self)

        # Initialize the background label
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Set up button functionality
        self.exit_button.clicked.connect(self.on_exit_requested)
        self.exit_requested_callback = None

        self.open_file_button.clicked.connect(self.on_open_saved_projects)
        self.open_saved_projects_callback = None

        # Track the Saved Projects UI window
        self.saved_projects_window = None  

        self.setWindowTitle("MuseEase")

        # Set the window to fullscreen
        self.showFullScreen()  # This makes the window fullscreen upon opening

        # Background setup
        bg_image_path = os.path.join(os.path.dirname(ui_path), 'background.jpg')

        # Check if the background image file exists
        if os.path.exists(bg_image_path):
            self.bg_pixmap = QPixmap(bg_image_path)
            self.update_background()
        else:
            print(f"Error: Background image '{bg_image_path}' not found.")

        # Ensure background is placed behind all widgets
        self.bg_label.lower()

    def resizeEvent(self, event):
        """Resize the background dynamically when the window is resized."""
        if hasattr(self, 'bg_pixmap'):  # Check if bg_pixmap is initialized
            self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        """Scale the background image to fit the window size."""
        if hasattr(self, 'bg_pixmap'):  # Ensure bg_pixmap is available before using it
            self.bg_label.setGeometry(0, 0, self.width(), self.height())  
            scaled_pixmap = self.bg_pixmap.scaled(self.width(), self.height())
            self.bg_label.setPixmap(scaled_pixmap)

    def set_exit_callback(self, callback):
        self.exit_requested_callback = callback

    def on_exit_requested(self):
        if self.exit_requested_callback:
            self.exit_requested_callback()

    def execute_exit(self):
        self.close()

<<<<<<< HEAD

class New_Project(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
=======
    def set_open_saved_projects_callback(self, callback):
        self.open_saved_projects_callback = callback

    def on_open_saved_projects(self):
        if self.open_saved_projects_callback:
            self.open_saved_projects_callback()


class SavedProjects(QDialog):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/SavedProjects.ui')
        uic.loadUi(ui_path, self)

        self.openProjectButton.clicked.connect(self.open_selected_project)
        self.deleteProjectButton.clicked.connect(self.delete_selected_project)

        # Prevent user from editing the QListView
        self.savedProjectsListView.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

    def populate_saved_projects(self, files):
        """Populates the saved projects list."""
        model = QStringListModel()
        model.setStringList(files)
        self.savedProjectsListView.setModel(model)

    def open_selected_project(self):
        """Opens the selected project."""
        selected_indexes = self.savedProjectsListView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Open Project", "No project selected.")
            return
        
        selected_file = selected_indexes[0].data()
        project_path = os.path.join(project_root, "Saves", f"{selected_file}.muse")  # Full path to .muse file
        QMessageBox.information(self, "Open Project", f"Opening project: {selected_file}")
        daw = DAWTest()
        daw.show()
        daw.load_project(project_path)

    def delete_selected_project(self):
        """Deletes the selected project."""
        selected_indexes = self.savedProjectsListView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Delete Project", "No project selected.")
            return
        
        selected_file = str(selected_indexes[0].data()) + ".muse"
        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Saves")
        file_path = os.path.join(folder_path, selected_file)

        confirm = QMessageBox.question(self, "Delete Project", f"Are you sure you want to delete {selected_file}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            os.remove(file_path)
            QMessageBox.information(self, "Delete Project", f"Deleted: {selected_file}")
            self.populate_saved_projects([os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.muse')])

>>>>>>> df9794c35acff4d76b6253f66f44da2e8d4ab009
