# MVP/presenter.py
from MVP.Model.model import Model
from MVP.View import Main_Menu, Saved_Projects, DAW, Tutorial  # Updated imports
from PyQt6.QtWidgets import QMessageBox, QStackedWidget
import os

class Presenter:
    def __init__(self, stacked_widget):
        self.stacked_widget = stacked_widget
        self.model = Model()
        self.main_menu = Main_Menu()
        self.new_project = DAW(self)  # Updated class name
        self.saved_projects = Saved_Projects(self)

        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.new_project)
        self.stacked_widget.addWidget(self.saved_projects)

        self.main_menu_init()
        self.saved_projects_init()
        self.new_project_init()

    def main_menu_init(self):
        self.main_menu.set_exit_callback(self.on_exit_requested)
        self.main_menu.set_open_saved_projects_callback(self.on_open_saved_projects_requested)
        self.main_menu.set_new_project_callback(self.on_new_project_requested)
        self.main_menu.tutorial_button.clicked.connect(self.on_tutorial_requested) 
        
    def on_tutorial_requested(self):
        self.tutorial = Tutorial(self)
        self.stacked_widget.addWidget(self.tutorial)
        self.stacked_widget.setCurrentWidget(self.tutorial)

    def on_tutorial_closed(self):
        if self.tutorial:
            self.stacked_widget.removeWidget(self.tutorial)
            self.tutorial = None
            self.stacked_widget.setCurrentWidget(self.main_menu)

    def saved_projects_init(self):
        if not self.saved_projects:
            print("Recreating Saved_Projects instance")
            self.saved_projects = Saved_Projects(self)
            self.stacked_widget.addWidget(self.saved_projects)

        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MuseEase/Saves")
        os.makedirs(folder_path, exist_ok=True)

        print(f"Looking for .muse files in: {folder_path}")
        try:
            files = os.listdir(folder_path)
            print(f"Found files: {files}")
        except (PermissionError, FileNotFoundError) as e:
            print(f"Error accessing Saves directory: {e}")
            return

        muse_files = [f for f in files if f.lower().endswith('.muse')]
        if not muse_files:
            print("No .muse files found in the directory.")
            return

        files = [os.path.splitext(f)[0] for f in muse_files]
        print(f"Filtered .muse files (base names): {files}")

        if files and self.saved_projects:
            self.saved_projects.populate_saved_projects(files)
            self.saved_projects.backButton.clicked.connect(self.on_exit_to_menu_requested)

    def new_project_init(self):
        pass

    def new_project(self):
        pass

    def saved_project(self):
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
        if not self.new_project:
            print("Recreating New_Project instance")
            self.new_project = DAW(self)  # Updated class name
            self.stacked_widget.addWidget(self.new_project)
            
        self.stacked_widget.setCurrentWidget(self.new_project)
        self.saved_projects_init()

    def on_exit_requested(self):
        do_exit = QMessageBox.question(self.main_menu, "Exit", "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if do_exit == QMessageBox.StandardButton.Yes:
            self.main_menu.execute_exit()
    
    def on_new_project_from_save_requested(self, project_name, project_path):
        if self.new_project:
            self.new_project.close()
            self.new_project = None
        
        self.new_project = DAW(self)  # Updated class name
        self.new_project.load_project(project_path)
        
        self.stacked_widget.setCurrentWidget(self.new_project)
            
    def on_exit_to_menu_requested(self):
        self.stacked_widget.setCurrentWidget(self.main_menu)
        
        if self.saved_projects:
            print("CLOSING SAVED PROJECTS")
            self.saved_projects.close()
            self.stacked_widget.removeWidget(self.saved_projects)
            self.saved_projects = None
            
        if self.new_project:
            self.new_project.close() 
            self.new_project = None 
        
        self.saved_projects_init()
        
    def reinitialize_project_views(self):
        if not self.new_project:
            self.new_project = DAW(self)  # Updated class name
            self.stacked_widget.addWidget(self.new_project) 
        
        if not self.saved_projects:
            self.saved_projects = Saved_Projects(self)
            self.stacked_widget.addWidget(self.saved_projects)