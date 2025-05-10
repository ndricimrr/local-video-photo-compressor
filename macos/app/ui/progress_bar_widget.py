from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt


class ProgressBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout for the progress bar
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # Ensure no margins inside layout

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setMinimumHeight(20)  # Set minimum height for better visibility
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: '#32CD32';
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

        # Percentage Label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.layout.addWidget(self.percentage_label)

        # Set the layout
        self.setLayout(self.layout)

    def update_progress(self, value):
        """
        Updates the progress bar and percentage label.

        :param value: Progress value from 0 to 100.
        """
        if 0 <= value <= 100:
            self.progress_bar.setValue(value)
            # self.percentage_label.setText(f"{value}%")
