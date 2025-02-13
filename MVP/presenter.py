from MVP.Model.model import Model
from MVP.View.view import View
from PyQt6.QtWidgets import QMessageBox


class Presenter:

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.view.set_exit_callback(self.on_exit_requested)
    
    def new_project(self):
        '''
        Opens New Project UI when User Clicks on "New Project"
        '''
    
    def saved_project(self):
        '''
        Opens View Saved Projects UI when User clicks on "View Saved"
        '''

    def on_exit_requested(self):
        '''
        Exits Application via Message Box
        '''
        do_exit = QMessageBox.question(self.view, "Exit", "Are you sure you want to exit?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if do_exit == QMessageBox.StandardButton.Yes:
            self.view.execute_exit()
