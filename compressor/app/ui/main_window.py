from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit
from PyQt6.QtCore import Qt
from ui.drag_drop_area import DragDropArea
from ui.progress_bar_widget import ProgressBarWidget  # Import the progress bar widget
from compressStuff import analyze_compression_time, process_files
from publisher import Publisher
import math 
from PyQt6.QtCore import QThread
from file_process_worker import FileProcessingWorker

from ui.filter_widget import FilterWidget  # Import the FilterWidget

class MainWindow(QWidget):
    

    def __init__(self):
        super().__init__()
        self.analysisResult = None

        self.setWindowTitle("Folder Compression Tool")
        self.setGeometry(300, 200, 600, 400)

        # Variables for input and output folders
        self.inputFolder = ""
        self.outputFolder = ""
        self.loadPreviousProgress = False

        self.worker = None
        self.thread = None
        self.selected_compression_speed = "fast"
        self.selected_image_quality = 20
        # Main layout (vertical)
        self.main_layout = QVBoxLayout()

        # Description at the top
        self.description = QLabel("A simple Video & Photo Compressor")
        self.description.setStyleSheet("font-size: 16px; font-weight: bold; padding-bottom: 10px;")
        self.main_layout.addWidget(self.description)

        # Input section layout (horizontal): Drag & Drop + Add Folder button
        self.input_section_layout = QHBoxLayout()

        # Drag-and-Drop area
        self.drag_drop_area = DragDropArea(self)
        self.input_section_layout.addWidget(self.drag_drop_area)

        # Add Folder button
        self.add_folder_button = QPushButton("Add Folder")
        self.add_folder_button.clicked.connect(self.add_folder)
        self.add_folder_button.setStyleSheet(self.button_style())
        self.input_section_layout.addWidget(self.add_folder_button)
        self.input_section_layout.setContentsMargins(0,0,0,0)
        
        # Add input section layout to the main layout
        self.main_layout.addLayout(self.input_section_layout)

        # Input folder path text area (editable)
        self.input_folder_edit = QLineEdit(self)
        self.input_folder_edit.setPlaceholderText("Input folder path...")
        self.input_folder_edit.setStyleSheet(self.input_field_style())
        self.input_folder_edit.textChanged.connect(self.update_input_folder)  # Reflect changes to inputFolder variable
        self.main_layout.addWidget(self.input_folder_edit)

        ############################################################################### 
        # Output section layout (horizontal): Set Output Folder button + input field
        self.output_section_layout = QHBoxLayout()

        self.output_folder_button = QPushButton("Set Output Folder")
        self.output_folder_button.clicked.connect(self.set_output_folder)
        self.output_folder_button.setStyleSheet(self.button_style())
        self.output_section_layout.addWidget(self.output_folder_button)

        # Output folder path text area (editable)
        self.output_folder_edit = QLineEdit(self)
        self.output_folder_edit.setPlaceholderText("Output folder path...")
        self.output_folder_edit.setStyleSheet(self.output_folder_input_field_style())
        self.output_folder_edit.textChanged.connect(self.update_output_folder)  # Reflect changes to outputFolder variable
        self.output_section_layout.addWidget(self.output_folder_edit)
        self.output_section_layout.setContentsMargins(0,70,0,10)

        # Add output section layout to the main layout
        self.main_layout.addLayout(self.output_section_layout)

        self.estimatedAndFiltersSection = QHBoxLayout();

        self.estimatedSection = QVBoxLayout()

        # Create a widget to hold the vertical layout
        self.estimated_section_widget = QWidget()

        self.estimateLabel = QLabel("Estimated Time Required: ")
        self.estimateLabel.setStyleSheet("font-size: 16px; font-weight: bold; padding-bottom: 10px;")
        self.estimatedSection.addWidget(self.estimateLabel)

        self.totalFiles = QLabel("Total Files: ")
        self.totalFiles.setStyleSheet("font-size: 12px; font-weight: light; padding-bottom: 10px;")
        self.estimatedSection.addWidget(self.totalFiles)

        self.totalImages = QLabel("Total Images: ")
        self.totalImages.setStyleSheet("font-size: 12px; font-weight: light; padding-bottom: 10px;")
        self.estimatedSection.addWidget(self.totalImages)

        self.totalVideos = QLabel("Total Videos: ")
        self.totalVideos.setStyleSheet("font-size: 12px; font-weight: light; padding-bottom: 10px;")
        self.estimatedSection.addWidget(self.totalVideos)

        self.totalUnsupportedFiles = QLabel("Total Unsupported Files: ")
        self.totalUnsupportedFiles.setStyleSheet("font-size: 12px; font-weight: light; padding-bottom: 10px;")
        self.estimatedSection.addWidget(self.totalUnsupportedFiles)

        # Set the vertical layout on the new QWidget
        self.estimated_section_widget.setLayout(self.estimatedSection)

        self.estimatedAndFiltersSection.addWidget(self.estimated_section_widget);

           # Add Filters Widget
        self.init_filter_ui()

        self.main_layout.addLayout(self.estimatedAndFiltersSection)          


        # Compress Section
        self.compressSection = QHBoxLayout()

        # Compress button, initially disabled
        self.start_button = QPushButton("Start")
        self.start_button.setEnabled(False)
        self.start_button.setStyleSheet(self.button_style())
        self.start_button.clicked.connect(self.onStartClicked)
        self.compressSection.addWidget(self.start_button)

        # Pause 
        self.pause_button = QPushButton("Pause")
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'gray'; padding: 10px; border-radius: 5px; color: 'white'")
        self.pause_button.clicked.connect(self.onPauseClicked)
        self.compressSection.addWidget(self.pause_button)

        # Cancel 
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'red'; padding: 10px; border-radius: 5px; color: 'white'")
        self.cancel_button.clicked.connect(self.onCancelClicked)
        self.compressSection.addWidget(self.cancel_button)

        self.compressSection.setSpacing(10)
        
        self.main_layout.addLayout(self.compressSection)          

        # Add progress bar 
        self.progress_bar_widget = ProgressBarWidget(self)
        self.progress_bar_widget.setContentsMargins(0,10,0,10)
        self.main_layout.addWidget(self.progress_bar_widget) 

        # Set main layout
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)


    def onCancelClicked(self):
        self.start_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'blue'; padding: 10px; border-radius: 5px; color: 'white'")
        self.pause_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'grey'; padding: 10px; border-radius: 5px; color: 'white'")
        self.cancel_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'red'; padding: 10px; border-radius: 5px; color: 'white'")
        self.start_button.setText("Start")
        self.progress = 0
        
        try:
            self.worker.progress.disconnect()
            print("Signal disconnected")
        except TypeError:
            # This will catch the error if there are no connections to disconnect
            print("Signal was not connected, nothing to disconnect")

        self.progress_bar_widget.update_progress(0) 
        self.stopProcessing()
        self.loadPreviousProgress = False

    def stopProcessing(self):
        if self.worker:
            self.worker.stop()  # Stop the worker
            if self.thread:
                if self.thread.isRunning():  # Check if the thread is still active
                    self.thread.quit()  # Stop the thread
                    self.thread.wait()  # Wait for the thread to finish
                else:
                    print("Thread already stopped!")
                self.thread = None  
            else:
                print("Thread reference is None or already stopped!")
        else:
            print("No self.worker available skip stopping")

    def onPauseClicked(self):
        print("Stopping on pause clicked")
        self.start_button.setText("Continue")
        self.start_button.setStyleSheet("font-size: 12px; font-weight: light; background-color: 'green'; padding: 10px; border-radius: 5px; color: 'white'")
        self.stopProcessing()  
        self.loadPreviousProgress = True

    def onStartClicked(self):
        def updateProgressBar(data):
            current_num_videos = data['processed_videos_count']
            current_videos_size = data['total_original_videos_size']

            current_images_size = data['total_original_images_size']
            current_num_images = data['processed_images_count']

            total_count = self.analysisResult['total_files_count']
            total_size = self.analysisResult['total_size']

            analysis_total_size = self.analysisResult['total_size']

            self.progress = (( current_images_size + current_videos_size ) / analysis_total_size) * 100

            print("Update progress" + math.ceil(self.progress).__str__())

            self.progress_bar_widget.update_progress(math.ceil(self.progress))
    
        #  Add worker and start thread
        self.worker = FileProcessingWorker(self.inputFolder, self.outputFolder, self.loadPreviousProgress, self.selected_compression_speed, self.selected_image_quality)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        # Connect the worker's progress signal to the UI update function
        self.worker.progress.connect(updateProgressBar)
        
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the process
        self.thread.started.connect(self.worker.run)
     
        self.thread.start()

        self.pause_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        
    def add_folder(self):
        """Open file dialog to manually select a folder."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder_path:
            self.input_folder_edit.setText(folder_path)  # Update input folder text area
            self.inputFolder = folder_path  # Update inputFolder variable

    def set_output_folder(self):
        """Open file dialog to select the output folder."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder_edit.setText(folder_path)  # Update output folder text area
            self.outputFolder = folder_path  # Update outputFolder variable
            self.start_button.setEnabled(True)  # Enable compress button once output folder is set

    def update_input_folder(self, text):
        """Update inputFolder variable when input folder text area changes."""
        self.inputFolder = text
        self.analysisResult = analyze_compression_time(text)

        self.estimateLabel.setText("Estimated Time Required: " + self.analysisResult['total_estimated_time_str'])
        self.totalFiles.setText("Total Files: " + self.analysisResult['total_files_count'] + ' files (' + self.analysisResult['formatted_total_size'] +' )')
        self.totalImages.setText("Total Images: " + self.analysisResult['image_files_count'] + ' files (' + self.analysisResult['formatted_image_size'] +' )')
        self.totalVideos.setText("Total Videos: " + self.analysisResult['video_files_count'] + ' files (' + self.analysisResult['formatted_video_size'] +' )')
        self.totalUnsupportedFiles.setText("Unsupported Files: " + self.analysisResult['unsupported_files_count'] + ' files (' + self.analysisResult['formatted_unsupported_size'] +' )')





    def update_output_folder(self, text):
        """Update outputFolder variable when output folder text area changes."""
        self.outputFolder = text

    def button_style(self):
        """Return styling for buttons."""
        return """
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """
    
    def button_style(self):
        """Return styling for buttons."""
        return """
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """

    def input_field_style(self):
        """Return styling for input fields."""
        return """
            QLineEdit {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 0
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """
   
    def output_folder_input_field_style(self):
        """Return styling for input fields."""
        return """
            QLineEdit {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """
    

    def init_filter_ui(self):
        # Filters Section (Integrate FilterWidget)
        filter_widget = FilterWidget()

        # Connect signals from FilterWidget to slots in MainWindow
        filter_widget.compression_speed_changed.connect(self.on_compression_speed_changed)
        # filter_widget.crf_changed.connect(self.on_crf_changed)
        filter_widget.image_quality_changed.connect(self.on_image_quality_changed)

        self.estimatedAndFiltersSection.addWidget(filter_widget);



   # Slot to handle compression speed changes
    def on_compression_speed_changed(self, value):
        self.selected_compression_speed = value
        print(f"Compression Speed changed to: {value}")

    # Slot to handle CRF changes
    # def on_crf_changed(self, value):
    #     self.selected_crf = value
    #     print(f"CRF changed to: {value}")

    # Slot to handle quality changes
    def on_image_quality_changed(self, value):
        self.selected_image_quality = value
        print(f"Image Quality changed to: {value}")