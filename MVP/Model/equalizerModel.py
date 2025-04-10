# MVP/Model/equalizerModel.py
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from .biquadFilter import BiquadFilter

class EqualizerModel(QObject):
    # Signals emitted when settings are updated
    gain_updated = pyqtSignal(str, int)  # (band, value)
    lowpass_freq_updated = pyqtSignal(str, int)  # (band, value)
    highpass_freq_updated = pyqtSignal(str, int)  # (band, value)
    reverb_updated = pyqtSignal(str, int)  # (band, value)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Frequency bands and their settings
        self.bands = ["Low (20-250 Hz)", "Mid (250-4000 Hz)", "High (4000-20000 Hz)"]

        self.highpass_limits = {
            "Low (20-250 Hz)": (20, 249),
            "Mid (250-4000 Hz)": (20, 3999),
            "High (4000-20000 Hz)": (4000, 19999)
        }

        self.lowpass_limits = {
            "Low (20-250 Hz)": (20, 250),
            "Mid (250-4000 Hz)": (250, 4000),
            "High (4000-20000 Hz)": (4000, 20000)
        }

        self.settings = {
            band: {"gain": 0, "lowpass_freq": self.lowpass_limits[band][1], "highpass_freq": self.highpass_limits[band][0], "reverb": 0}
            for band in self.bands
        }

    def set_band(self, band, gain=None, hp=None, lp=None):
        if gain is not None:
            self.set_gain(band, gain)
        if hp is not None:
            self.set_highpass_freq(band, hp)
        if lp is not None:
            self.set_lowpass_freq(band, lp)

    @pyqtSlot(str, int)
    def set_gain(self, band, value):
        self.settings[band]["gain"] = value
        self.gain_updated.emit(band, value)

    @pyqtSlot(str, int)
    def set_lowpass_freq(self, band, value):
        min_val, max_val = self.lowpass_limits[band]
        value = max(min_val, min(value, max_val))
        if value <= self.settings[band]["highpass_freq"]:
            value = self.settings[band]["highpass_freq"] + 1
        self.settings[band]["lowpass_freq"] = value
        self.lowpass_freq_updated.emit(band, value)

    @pyqtSlot(str, int)
    def set_highpass_freq(self, band, value):
        min_val, max_val = self.highpass_limits[band]
        value = max(min_val, min(value, max_val))

        if band == "High (4000-20000 Hz)":
            if value >= self.settings[band]["lowpass_freq"]:
                value = self.settings[band]["lowpass_freq"]
        else:
            if value >= self.settings[band]["lowpass_freq"]:
                value = self.settings[band]["lowpass_freq"] - 1

        self.settings[band]["highpass_freq"] = value
        self.highpass_freq_updated.emit(band, value)

    @pyqtSlot(str, int)
    def set_reverb(self, band, value):
        self.settings[band]["reverb"] = value
        self.reverb_updated.emit(band, value)

    def get_filters(self, sample_rate):
        filters = []
        for band in self.bands:
            settings = self.settings[band]
            gain = settings["gain"]
            hp = settings["highpass_freq"]
            lp = settings["lowpass_freq"]

            if band == "Low (20-250 Hz)":
                filters.append(BiquadFilter.create_low_shelf(sample_rate, lp, gain, Q=0.707))
            elif band == "Mid (250-4000 Hz)":
                center = (hp + lp) / 2
                bw = lp - hp
                Q = max(0.3, min(center / bw if bw != 0 else 1.0, 10))
                filters.append(BiquadFilter.create_peaking_eq(sample_rate, center, gain, Q=Q))
            elif band == "High (4000-20000 Hz)":
                filters.append(BiquadFilter.create_high_shelf(sample_rate, hp, gain, Q=0.707))

        return filters
