from MVP.Model.model import Model
from MVP.View.view import Main_Menu, Saved_Projects, New_Project
from PyQt6.QtWidgets import QMessageBox, QStackedWidget
import os


class Presenter:
    def __init__(self, stacked_widget) -> None:
        self.stacked_widget = stacked_widget  # stack for holding all views (UIs) in memory
        self.model = Model()
        self.main_menu = Main_Menu()
        self.new_project = New_Project(self)
        self.saved_projects = Saved_Projects(self)

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
        
        if not self.saved_projects:
            print("Recreating Saved_Projects instance")
            self.saved_projects = Saved_Projects(self)
            self.stacked_widget.addWidget(self.saved_projects)
        
        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "MuseEase/Saves")
        os.makedirs(folder_path, exist_ok=True)

        # Debug: Check if the directory and files exist
        print(f"Looking for .muse files in: {folder_path}")
        try:
            files = os.listdir(folder_path)
            print(f"Found files: {files}")
        except PermissionError as e:
            print(f"Permission error accessing Saves directory: {e}")
            print(self.saved_projects, "Permission Error", f"Cannot access Saves directory: {str(e)}")
            return
        except FileNotFoundError as e:
            print(f"Saves directory not found: {e}")
            print(self.saved_projects, "Directory Error", f"Saves directory not found: {str(e)}")
            return

        muse_files = [f for f in files if f.lower().endswith('.muse')]  # Case-insensitive check
        if not muse_files:
            print("No .muse files found in the directory.")
            print(self.saved_projects, "No Projects", "No saved projects found in Saves directory.")
            return

        files = [os.path.splitext(f)[0] for f in muse_files]  # Extract base names (e.g., "autosave")
        print(f"Filtered .muse files (base names): {files}")

        # Populate the SavedProjects window
        if files and self.saved_projects:
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
        if not self.new_project:
            print("Recreating New_Project instance")
            self.new_project = New_Project(self)
            self.stacked_widget.addWidget(self.new_project)
            
        self.stacked_widget.setCurrentWidget(self.new_project)
        self.saved_projects_init()

    def on_exit_requested(self):
        """Exits the application with a confirmation message box."""
        do_exit = QMessageBox.question(self.main_menu, "Exit", "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if do_exit == QMessageBox.StandardButton.Yes:
            self.main_menu.execute_exit()
    
    def on_new_project_from_save_requested(self, project_name, project_path):
        """Handles loading a saved project and switching to New_Project."""
        # Close the existing New_Project if it exists
        if self.new_project:
            self.new_project.close()
            self.new_project = None
        
        # Create a new New_Project instance with the Presenter
        self.new_project = New_Project(self)
        self.new_project.load_project(project_path)  # Load the saved project
        
        # Add or update New_Project in the stacked widget (it’s already added in __init__, but ensure it’s current)
        self.stacked_widget.setCurrentWidget(self.new_project)
            
    def on_exit_to_menu_requested(self):
        """Handles the request to exit New_Project and return to Main_Menu."""
        
        #print("HANDLING REQUEST")
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
        """Reinitializes New_Project and Saved_Projects when needed."""
                
        if not self.new_project:
            self.new_project = New_Project(self)
            self.stacked_widget.addWidget(self.new_project) 
        
        if not self.saved_projects:
            self.saved_projects = Saved_Projects(self)
            self.stacked_widget.addWidget(self.saved_projects)  


            
            
        
            
            