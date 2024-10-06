from PyQt6.QtCore import QObject, pyqtSignal
from compressStuff import process_files

class FileProcessingWorker(QObject):
    progress = pyqtSignal(dict)  # Signal to emit progress as a dictionary

    def __init__(self, input_folder, output_folder, load_progress):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.load_progress = load_progress
        self._is_running = True

    def run(self):
        # Call the process_files function and pass the worker itself to handle signaling
        process_files(self.input_folder, self.output_folder, self.load_progress, self)

    def stop(self):
        """Stop the file processing."""
        self._is_running = False  # Set flag to stop processing