from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit
from PyQt6.QtCore import Qt
from ui.drag_drop_area import DragDropArea
from ui.progress_bar_widget import ProgressBarWidget  # Import the progress bar widget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Folder Compression Tool")
        self.setGeometry(300, 200, 600, 400)

        # Variables for input and output folders
        self.inputFolder = ""
        self.outputFolder = ""

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

        # Compress button, initially disabled
        self.compress_button = QPushButton("Compress")
        self.compress_button.setEnabled(False)
        self.compress_button.setStyleSheet(self.button_style())
        self.main_layout.addWidget(self.compress_button)


        # Add progress bar 
        self.progress_bar_widget = ProgressBarWidget(self)
        self.progress_bar_widget.setContentsMargins(0,10,0,10)
        self.main_layout.addWidget(self.progress_bar_widget) 

        # test it
        self.simulate_button = QPushButton("Simulate Progress")
        self.simulate_button.clicked.connect(self.simulate_progress)
        self.main_layout.addWidget(self.simulate_button)
 
        
            
        # Set main layout
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

    def simulate_progress(self):
        # Simulating the progress bar filling up
        for value in range(0, 101, 10):
            self.progress_bar_widget.update_progress(value)

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
            self.compress_button.setEnabled(True)  # Enable compress button once output folder is set

    def update_input_folder(self, text):
        """Update inputFolder variable when input folder text area changes."""
        self.inputFolder = text

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