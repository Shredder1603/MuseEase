# MVP/View/saved_projects.py
from PyQt6.QtWidgets import QDialog, QWidget, QMessageBox, QListView
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Saved_Projects(QDialog, QWidget):
    def __init__(self, presenter=None):
        super().__init__()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ui_path = os.path.join(project_root, 'MVP', 'View', 'UI', 'SavedProjects.ui')
        print(f"UI Path: {ui_path}")  # Debug print
        if not os.path.exists(ui_path):
            raise FileNotFoundError(f"UI file not found at: {ui_path}")
        try:
            uic.loadUi(ui_path, self)
        except Exception as e:
            raise RuntimeError(f"Failed to load UI file {ui_path}: {str(e)}")

        self.presenter = presenter
        self.openProjectButton = getattr(self, "openProjectButton")
        self.openProjectButton.clicked.connect(self.open_selected_project)

        self.deleteProjectButton = getattr(self, "deleteProjectButton")
        self.deleteProjectButton.clicked.connect(self.delete_selected_project)

        self.backButton = getattr(self, "backButton")
        self.backButton.clicked.connect(self.on_back_button_clicked)

        self.savedProjectsListView = getattr(self, "savedProjectsListView")
        self.savedProjectsListView.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

    def on_back_button_clicked(self):
        """Handles the back button click event to return to the main menu."""
        if self.presenter:
            self.presenter.on_exit_to_menu_requested()

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
        project_path = os.path.join(project_root, "Saves", f"{selected_file}.muse")
        QMessageBox.information(self, "Open Project", f"Opening project: {selected_file}")
        
        if self.presenter:
            self.presenter.stacked_widget.removeWidget(self.presenter.saved_projects)
            self.presenter.saved_projects = None

        # Force the UI to switch to Main Menu before loading the project
        self.presenter.stacked_widget.setCurrentWidget(self.presenter.main_menu)

        # Open New_Project as usual
        from .daw import DAW
        daw = DAW(self.presenter)
        self.presenter.new_project = daw
        self.presenter.stacked_widget.addWidget(daw)
        self.presenter.stacked_widget.setCurrentWidget(daw)
        daw.load_project(project_path)

    def delete_selected_project(self):
        """Deletes the selected project."""
        selected_indexes = self.savedProjectsListView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Delete Project", "No project selected.")
            return
        
        selected_file = str(selected_indexes[0].data()) + ".muse"
        folder_path = os.path.join(project_root, "Saves")
        file_path = os.path.join(folder_path, selected_file)

        confirm = QMessageBox.question(self, "Delete Project", f"Are you sure you want to delete {selected_file}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            os.remove(file_path)
            QMessageBox.information(self, "Delete Project", f"Deleted: {selected_file}")
            self.populate_saved_projects([os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.muse')])