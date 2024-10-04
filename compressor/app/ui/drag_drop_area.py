from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class DragDropArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.layout = QVBoxLayout()
        self.label = QLabel("Drag and drop a folder here")
        self.label.setStyleSheet(self.label_style())
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setStyleSheet(self.area_style(normal=True))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.area_style(normal=False))  # Change border color on hover

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.area_style(normal=True))  # Reset border color when drag leaves

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            self.update_folder_path(folder_path)
        self.setStyleSheet(self.area_style(normal=True))  # Reset border color after drop

    def update_folder_path(self, folder_path):
        """Update the label and input folder when a folder is dropped."""
        # self.label.setText(f"Selected folder: {folder_path}")
        self.parent().input_folder_edit.setText(folder_path)  # Update input folder text area
        self.parent().inputFolder = folder_path  # Update inputFolder variable

    def label_style(self):
        """Return styling for the label inside drag-and-drop area."""
        return """
            QLabel {
                color: #333333;
                font-size: 14px;
            }
        """

    def area_style(self, normal=True):
        """Return styling for the drag-and-drop area, with hover effect."""
        if normal:
            return """
                QWidget {
                    border: 2px dashed #0078d7;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                }
            """
        else:
            return """
                QWidget {
                    border: 2px dashed #ff9800;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0;
                }
            """
