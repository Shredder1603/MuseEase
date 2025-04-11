# MVP/View/EqualizerView.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QMenu, QLineEdit, QDialog, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

class EqualizerView(QWidget):
    # Signals emitted when the user interacts with the UI
    gain_changed = pyqtSignal(str, int)  # (band, value)
    lowpass_freq_changed = pyqtSignal(str, int)  # (band, value)
    highpass_freq_changed = pyqtSignal(str, int)  # (band, value)
    reverb_changed = pyqtSignal(str, int)  # (band, value)
    ai_input_submitted = pyqtSignal(str)  # (user_input)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable context menu for right-click
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        # Main layout for the panel
        self.layout = QVBoxLayout(self)
        self.sections = []

        # Frequency bands
        self.bands = ["Low (20-250 Hz)", "Mid (250-4000 Hz)", "High (4000-20000 Hz)"]
        self.sliders = {band: {} for band in self.bands}

        # Define band-specific frequency ranges
        self.highpass_ranges = {
            "Low (20-250 Hz)": (20, 249),
            "Mid (250-4000 Hz)": (20, 3999),
            "High (4000-20000 Hz)": (4000, 19999)
        }
        self.lowpass_ranges = {
            "Low (20-250 Hz)": (20, 250),
            "Mid (250-4000 Hz)": (250, 4000),
            "High (4000-20000 Hz)": (4000, 20000)
        }

        # Create a section for each band
        for band in self.bands:
            # Header button
            header = QPushButton(band)
            header.setCheckable(True)
            header.toggled.connect(lambda checked, b=band: self.toggle_section(b, checked))

            # Content widget for the band
            content = QWidget()
            content_layout = QVBoxLayout(content)

            # Gain
            gain_label = QLabel("Gain (dB): 0")
            gain_slider = QSlider(Qt.Orientation.Horizontal)
            gain_slider.setRange(-6, 6)
            gain_slider.setValue(0)
            gain_slider.valueChanged.connect(lambda value, b=band, l=gain_label: self.update_slider_label(b, 'gain', value, l))
            gain_slider.valueChanged.connect(lambda value, b=band: self.gain_changed.emit(b, value))

            gain_layout = QHBoxLayout()
            gain_layout.addWidget(gain_label)
            gain_layout.addWidget(gain_slider)

            # Low-pass
            lowpass_label = QLabel(f"Low-Pass (Hz): {self.lowpass_ranges[band][1]}")  # Default to max
            lowpass_slider = QSlider(Qt.Orientation.Horizontal)
            lowpass_slider.setRange(self.lowpass_ranges[band][0], self.lowpass_ranges[band][1])
            lowpass_slider.setValue(self.lowpass_ranges[band][1])  # Default to max
            lowpass_slider.valueChanged.connect(lambda value, b=band, l=lowpass_label: self.update_slider_label(b, 'lowpass', value, l))
            lowpass_slider.valueChanged.connect(lambda value, b=band: self.lowpass_freq_changed.emit(b, value))

            lowpass_layout = QHBoxLayout()
            lowpass_layout.addWidget(lowpass_label)
            lowpass_layout.addWidget(lowpass_slider)

            # High-pass
            highpass_label = QLabel(f"High-Pass (Hz): {self.highpass_ranges[band][0]}")  # Default to min
            highpass_slider = QSlider(Qt.Orientation.Horizontal)
            highpass_slider.setRange(self.highpass_ranges[band][0], self.highpass_ranges[band][1])
            highpass_slider.setValue(self.highpass_ranges[band][0])  # Default to min
            highpass_slider.valueChanged.connect(lambda value, b=band, l=highpass_label: self.update_slider_label(b, 'highpass', value, l))
            highpass_slider.valueChanged.connect(lambda value, b=band: self.highpass_freq_changed.emit(b, value))

            highpass_layout = QHBoxLayout()
            highpass_layout.addWidget(highpass_label)
            highpass_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            highpass_slider.setTickInterval((self.highpass_ranges[band][1] - self.highpass_ranges[band][0]) // 10)
            highpass_layout.addWidget(highpass_slider)

            # Reverb
            reverb_label = QLabel("Reverb (%): 0")
            reverb_slider = QSlider(Qt.Orientation.Horizontal)
            reverb_slider.setRange(0, 100)
            reverb_slider.setValue(0)
            reverb_slider.valueChanged.connect(lambda value, b=band, l=reverb_label: self.update_slider_label(b, 'reverb', value, l))
            reverb_slider.valueChanged.connect(lambda value, b=band: self.reverb_changed.emit(b, value))

            reverb_layout = QHBoxLayout()
            reverb_layout.addWidget(reverb_label)
            reverb_layout.addWidget(reverb_slider)

            # Add widgets to content layout
            content_layout.addLayout(gain_layout)
            content_layout.addLayout(lowpass_layout)
            content_layout.addLayout(highpass_layout)
            content_layout.addLayout(reverb_layout)
            content.setVisible(False)

            # Store sliders
            self.sliders[band]["gain"] = gain_slider
            self.sliders[band]["lowpass"] = lowpass_slider
            self.sliders[band]["highpass"] = highpass_slider
            self.sliders[band]["reverb"] = reverb_slider

            # Add section
            self.layout.addWidget(header)
            self.layout.addWidget(content)
            self.sections.append((header, content))

        self.layout.addStretch()

    def update_slider_label(self, band, param, value, label):
        if param == "gain":
            label.setText(f"Gain (dB): {value}")
        elif param == "lowpass":
            label.setText(f"Low-Pass (Hz): {value}")
        elif param == "highpass":
            label.setText(f"High-Pass (Hz): {value}")
        elif param == "reverb":
            label.setText(f"Reverb (%): {value}")

    def toggle_section(self, band, checked):
        for header, content in self.sections:
            if header.text() == band:
                content.setVisible(checked)
            else:
                header.setChecked(False)
                content.setVisible(False)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        ai_action = menu.addAction("Adjust with AI...")
        action = menu.exec(self.mapToGlobal(pos))
        if action == ai_action:
            self.show_ai_input_dialog()

    @pyqtSlot(str, int)
    def set_gain(self, band, value):
        self.sliders[band]["gain"].setValue(value)

    @pyqtSlot(str, int)
    def set_lowpass_freq(self, band, value):
        self.sliders[band]["lowpass"].setValue(value)

    @pyqtSlot(str, int)
    def set_highpass_freq(self, band, value):
        self.sliders[band]["highpass"].setValue(value)

    @pyqtSlot(str, int)
    def set_reverb(self, band, value):
        self.sliders[band]["reverb"].setValue(value)