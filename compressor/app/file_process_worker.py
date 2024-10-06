from PyQt6.QtCore import QObject, pyqtSignal
from compressStuff import process_files

class FileProcessingWorker(QObject):
    progress = pyqtSignal(dict)  # Signal to emit progress as a dictionary

    def __init__(self, input_folder, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        # Call the process_files function and pass the worker itself to handle signaling
        process_files(self.input_folder, self.output_folder, self)
