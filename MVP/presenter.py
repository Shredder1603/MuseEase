from MVP.Model.model import Model
from MVP.View.view import Main_Menu, Saved_Projects, New_Project
from PyQt6.QtWidgets import QMessageBox, QStackedWidget
import os


class Presenter:
    def __init__(self, stacked_widget) -> None:
        self.stacked_widget = stacked_widget  # stack for holding all views (UIs) in memory
        self.model = Model()
        self.main_menu = Main_Menu()
        self.new_project = New_Project()
        self.saved_projects = Saved_Projects()

        # add views to widget stack #
        # ------------------------------------------ #
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.new_project)
        self.stacked_widget.addWidget(self.saved_projects)
        # ------------------------------------------ #

        # initialize views #
        # ------------------------------------------ #
        self.main_menu_init()
        self.saved_projects_init()
        self.new_project_init()
        # ------------------------------------------ #

    def main_menu_init(self):
        self.main_menu.set_exit_callback(self.on_exit_requested)
        self.main_menu.set_open_saved_projects_callback(self.on_open_saved_projects_requested)
        self.main_menu.set_new_project_callback(self.on_new_project_requested)

    def saved_projects_init(self):
        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MuseEase/Saves")
        os.makedirs(folder_path, exist_ok=True)
        
        muse_files = [f for f in files if f.lower().endswith('.muse')]  # Case-insensitive check
        if not muse_files:
            print("No .muse files found in the directory.")
            QMessageBox.warning(self.saved_projects, "No Projects", "No saved projects found in Saves directory.")
            return

        files = [os.path.splitext(f)[0] for f in muse_files]  # Extract base names (e.g., "autosave")

        # Populate the SavedProjects window
        self.saved_projects.populate_saved_projects(files)

    def new_project_init(self):
        pass

    def new_project(self):
        """Creates a new project"""

    def saved_project(self):
        """Opens the 'Saved Projects' UI and loads saved `.muse` files."""
        folder_path = os.path.join((os.path.dirname(__file__)), "MuseEase/Saves")
        os.makedirs(folder_path, exist_ok=True)

        files = [f for f in os.listdir(folder_path) if f.endswith('.muse')]
        files = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.muse')]
        if not self.view.saved_projects_window:
            self.view.saved_projects_window = Saved_Projects()

        self.view.saved_projects_window.populate_saved_projects(files)
        self.view.saved_projects_window.show()

    def on_open_saved_projects_requested(self):
        self.stacked_widget.setCurrentWidget(self.saved_projects)

    def on_new_project_requested(self):
        self.stacked_widget.setCurrentWidget(self.new_project)

    def on_exit_requested(self):
        """Exits the application with a confirmation message box."""
        do_exit = QMessageBox.question(self.main_menu, "Exit", "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if do_exit == QMessageBox.StandardButton.Yes:
            self.main_menu.execute_exit()