from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QComboBox, QHBoxLayout


class FilterWidget(QWidget):
    compression_speed_changed = pyqtSignal(str)
    crf_changed = pyqtSignal(int)
    image_quality_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        # Main layout for filters
        self.layout = QVBoxLayout()

        # Compression Speed (Video Filter)
        self.filtersTitle = QLabel("Filters")
        self.filtersTitle.setStyleSheet("font-size: 16px; font-weight: bold; ")
        self.layout.addWidget(self.filtersTitle)

        # Compression Speed (Video Filter)
        self.compression_speed_label = QLabel("Video Compression Speed:")
        self.compression_speed_label.setStyleSheet("font-size: 13px; font-weight:bold")
        self.layout.addWidget(self.compression_speed_label)

        self.compression_speed_combo = QComboBox()
        compression_speeds = [
            "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"
        ]
        self.compression_speed_combo.addItems(compression_speeds)
        self.compression_speed_combo.currentTextChanged.connect(self.on_compression_speed_changed)
        self.layout.addWidget(self.compression_speed_combo)

        # Commenting it out because users might not understand well. 
        # CRF (Video Filter)
        # self.crf_label = QLabel("Video Quality Reduction : (0 = No Reduction / 51 = High Reduction)")
        # self.crf_label.setStyleSheet("font-size: 13px; font-weight:bold")

        # self.crf_label.setContentsMargins(0,10,0,0)
        # self.layout.addWidget(self.crf_label)

        # # Horizontal layout to show min/max and the slider
        # crf_slider_layout = QHBoxLayout()

        # # Min/Max CRF labels
        # self.crf_min_label = QLabel("0")
        # crf_slider_layout.addWidget(self.crf_min_label)

        # # CRF Slider
        # self.crf_slider = QSlider(Qt.Orientation.Horizontal)
        # self.crf_slider.setRange(0, 51)
        # self.crf_slider.setValue(23)  # Default value
        # self.crf_slider.valueChanged.connect(self.on_crf_changed)
        # crf_slider_layout.addWidget(self.crf_slider)

        # self.crf_max_label = QLabel("51")
        # crf_slider_layout.addWidget(self.crf_max_label)


        # self.layout.addLayout(crf_slider_layout)

        # # Current CRF Value
        # self.crf_value_label = QLabel("Current Value: 23")  # Default value
        # self.crf_value_label.setStyleSheet("font-size: 11px; ")
        # self.crf_value_label.setContentsMargins(0,0,0,15)

        # self.layout.addWidget(self.crf_value_label)

        # Quality (Photo Filter)
        self.quality_label = QLabel("Image Quality (1-100):")
        self.quality_label.setStyleSheet("font-size: 13px; font-weight:bold")
        self.layout.addWidget(self.quality_label)

        # Horizontal layout for Quality slider
        quality_slider_layout = QHBoxLayout()

        # Min/Max Quality labels
        self.quality_min_label = QLabel("1")
        quality_slider_layout.addWidget(self.quality_min_label)

        # Quality Slider
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(20)  # Default value
        self.quality_slider.valueChanged.connect(self.on_image_quality_changed)
        quality_slider_layout.addWidget(self.quality_slider)

        self.quality_max_label = QLabel("100")
        quality_slider_layout.addWidget(self.quality_max_label)

        self.layout.addLayout(quality_slider_layout)

        # Current Quality Value
        self.quality_value_label = QLabel("Current Image Quality: 80")  # Default value
        self.quality_value_label.setStyleSheet("font-size: 11px; ")

        self.layout.addWidget(self.quality_value_label)

        # Set the layout for this widget
        self.setLayout(self.layout)

    # Emit signals and update the labels on value change
    def on_compression_speed_changed(self, value):
        self.compression_speed_changed.emit(value)

    def on_crf_changed(self, value):
        self.crf_value_label.setText(f"Current CRF Value: {value}")
        self.crf_changed.emit(value)

    def on_image_quality_changed(self, value):
        self.quality_value_label.setText(f"Current Image Quality: {value}")
        self.image_quality_changed.emit(value)
