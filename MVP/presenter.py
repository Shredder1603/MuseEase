from MVP.Model.model import Model
from MVP.View.view import View


class Presenter():

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.view.input_data_collected.connect(self.handle_input_data)

    def handle_input_data(self, input_string: str) -> None:
        self.model.set_input("IM IN THE PRESENTER CLASS!")
        print("IM IN THE PRESENTER CLASS PRINT STATEMENT NOW!")
