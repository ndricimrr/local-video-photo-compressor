# This can be extended as needed
class FolderController:
    def __init__(self):
        self.input_folder = ""
        self.output_folder = ""

    def set_input_folder(self, folder_path):
        self.input_folder = folder_path

    def set_output_folder(self, folder_path):
        self.output_folder = folder_path
