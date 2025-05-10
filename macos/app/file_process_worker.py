from PyQt6.QtCore import QObject, pyqtSignal
from compressStuff import process_files

class FileProcessingWorker(QObject):
    progress = pyqtSignal(dict)  # Signal to emit progress as a dictionary

    def __init__(self, input_folder, output_folder, load_progress, video_compression_speed, selected_image_quality):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.load_progress = load_progress
        self.video_compression_speed = video_compression_speed
        self.selected_image_quality = selected_image_quality
        
        self._is_running = True

    def run(self):
        # Call the process_files function and pass the worker itself to handle signaling
        process_files(self.input_folder, self.output_folder, self.load_progress, self, self.video_compression_speed, self.selected_image_quality )

    def stop(self):
        """Stop the file processing."""
        self._is_running = False  # Set flag to stop processing