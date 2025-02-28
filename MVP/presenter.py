from MVP.Model.model import Model
from MVP.View.view import Main_Menu, SavedProjects
from PyQt6.QtWidgets import QMessageBox
import os


class Presenter:
    def __init__(self, model: Model, view: Main_Menu) -> None:
        self.model = model
        self.view = view
        self.view.set_exit_callback(self.on_exit_requested)
        self.view.set_open_saved_projects_callback(self.saved_project)

    def new_project(self):
        """Creates a new project"""

    def saved_project(self):
        """Opens the 'Saved Projects' UI and loads saved `.muse` files."""
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Saves")
        os.makedirs(folder_path, exist_ok=True)

        files = [f for f in os.listdir(folder_path) if f.endswith('.muse')]
        files = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.muse')]
        if not self.view.saved_projects_window:
            self.view.saved_projects_window = SavedProjects()

        self.view.saved_projects_window.populate_saved_projects(files)
        self.view.saved_projects_window.show()

    def on_exit_requested(self):
        """Exits the application with a confirmation message box."""
        do_exit = QMessageBox.question(self.view, "Exit", "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if do_exit == QMessageBox.StandardButton.Yes:
            self.view.execute_exit()