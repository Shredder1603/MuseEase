import sys
import os
from paths import resource_path
import numpy as np
import sounddevice as sd
import scipy
import soundfile as sf
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QMutex, QMutexLocker, pyqtSignal
from PyQt6 import uic

class SoundGenerator:
    def __init__(self, instruments=None, current_instrument="Guitar"):
        self.sf = sf
        self.mutex = QMutex()
        self.active_notes = {}
        self.instruments = instruments if instruments else {}
        self.current_instrument = current_instrument
        self.notes = self.instruments.get(self.current_instrument, {})
        self.samplerate = 44100
        self.available_instruments = []
        self.sample_filepaths = {}
        if not self.instruments:
            self.load_all_instruments()
            self.notes = self.instruments.get(self.current_instrument, {})
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()

    def load_all_instruments(self):
        instruments_dir = resource_path("Instruments") 
        if not os.path.exists(instruments_dir):
            print(f"Instruments directory {instruments_dir} not found.")
            return
        
        self.available_instruments = []
        target_samplerate = 44100  # Target sample rate for playback
        
        for instrument_name in os.listdir(instruments_dir):
            instrument_path = os.path.join(instruments_dir, instrument_name)
            if os.path.isdir(instrument_path):
                self.instruments[instrument_name] = {}
                self.sample_filepaths[instrument_name] = {}
                for filename in os.listdir(instrument_path):
                    filepath = os.path.join(instrument_path, filename)
                    if filename.endswith(('.aiff', '.wav')):
                        base_name = os.path.splitext(filename)[0]
                        if "_" in base_name:
                            technique, note_name = base_name.split("_", 1)
                        else:
                            technique = None
                            note_name = base_name

                        try:
                            data, samplerate = self.sf.read(filepath)
                            if data.ndim > 1:
                                data = np.mean(data, axis=1)
                            
                            # Resample if the sample rate doesn't match the target
                            if samplerate != target_samplerate:
                                num_samples = int(len(data) * target_samplerate / samplerate)
                                data = scipy.signal.resample(data, num_samples)
                                samplerate = target_samplerate
                            
                            # Normalize the amplitude to a peak of 0.9
                            max_amplitude = np.max(np.abs(data))
                            if max_amplitude > 0:
                                data = data * (0.9 / max_amplitude)
                            else:
                                print(f"Warning: Sample {filepath} has zero amplitude")

                            max_idx = np.argmax(np.abs(data))
                            start_frame = 0
                            for x in range(max_idx - 1, -1, -1):
                                if np.abs(data[x]) <= 0.008 * np.abs(data[max_idx]):
                                    start_frame = x
                                    break
                            end_frame = len(data)
                            snippet = data[start_frame:end_frame]
                            self.instruments[instrument_name][note_name] = (snippet, samplerate)
                            self.sample_filepaths[instrument_name][note_name] = filepath
                            if self.samplerate is None:
                                self.samplerate = samplerate
                        except sf.SoundFileError as e:
                            print(f"Error loading {filepath}: {str(e)}")
                if self.instruments[instrument_name]:
                    self.available_instruments.append(instrument_name)
        print(f"Available instruments: {self.available_instruments}")

    def set_current_instrument(self, instrument):
        self.current_instrument = instrument
        self.notes = self.instruments.get(self.current_instrument, {})
        print(f"SoundGenerator: Switched to instrument {self.current_instrument}")

    def note_on(self, note: str, instrument: str = None, loop: bool = False):
        """
        Start playing a note.
        Args:
            note (str): The note to play (e.g., "C4").
            instrument (str, optional): The instrument to use.
            loop (bool, optional): Whether to loop the note.
        """
        target_instrument = instrument if instrument else self.current_instrument
        adjusted_note = note  # No pitch shift needed
        
        # Get target notes dictionary
        target_notes = self.instruments.get(target_instrument, {})
        
        # Determine the expected and actual sample files
        expected_file = self.sample_filepaths.get(target_instrument, {}).get(note, "Unknown filepath")
        actual_note = adjusted_note if adjusted_note in target_notes else None
        actual_file = self.sample_filepaths.get(target_instrument, {}).get(actual_note, "No file accessed")
        
        # Log the expected and actual note/file information
        print(f"NOTE_ON: Expected note: {note}, Actual note played: {actual_note}")
        print(f"NOTE_ON: Expected file: {expected_file}, Actual file accessed: {actual_file}")
        
        # Play the note if it exists
        if adjusted_note not in self.active_notes and adjusted_note in target_notes:
            data, samplerate = target_notes[adjusted_note]
            
            if self.samplerate is None:
                self.samplerate = samplerate
                
            self.mutex.lock()
            self.active_notes[adjusted_note] = {"data": data, "play_pos": 0, "loop": loop}
            self.mutex.unlock()
        else:
            if adjusted_note not in target_notes:
                print(f"Note {adjusted_note} not found in {target_instrument} samples")
            else:
                print(f"Note {adjusted_note} already active")

    def note_off(self, note: str, instrument: str = None):
        """
        Stop playing a note by removing it from the active notes.
        Args:
            note (str): The note to stop (e.g., "C4").
            instrument (str, optional): The instrument the note was played with.
        """
        target_instrument = instrument if instrument else self.current_instrument
        adjusted_note = note  # No pitch shift needed
        
        self.mutex.lock()
        if adjusted_note in self.active_notes:
            del self.active_notes[adjusted_note]
        self.mutex.unlock()

    def audio_callback(self, outdata, frames, time, status):
        """Stream callback to play audio samples."""
        self.mutex.lock()
        try:
            if not self.active_notes:
                outdata.fill(0)
                return
            mixed = np.zeros(frames)
            to_remove = []
            for note, note_data in self.active_notes.items():
                data, play_pos, loop = note_data["data"], note_data["play_pos"], note_data["loop"]
                chunk = data[play_pos: play_pos + frames]
                mixed[:len(chunk)] += chunk
                play_pos += frames
                if play_pos >= len(data):
                    if loop:
                        play_pos = 0
                    else:
                        to_remove.append(note)
                self.active_notes[note]["play_pos"] = play_pos
            for note in to_remove:
                del self.active_notes[note]
            mixed = np.clip(mixed, -1, 1)
            outdata[:len(mixed)] = mixed.reshape(-1, 1)
            outdata[len(mixed):] = 0
        finally:
            self.mutex.unlock()

class NotesWindow(QMainWindow):
    note_started = pyqtSignal(str)  # Signal for note start
    note_stopped = pyqtSignal(str)  # Signal for note stop
    finished = pyqtSignal()         # Signal emitted when window is closed
    
    def __init__(self, sound_generator=None, current_instrument="Piano"):
        super().__init__()
        ui_path = resource_path('MVP/View/UI/Notes.ui')
        uic.loadUi(ui_path, self)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        self.sound = sound_generator if sound_generator else SoundGenerator(current_instrument=current_instrument)
        self.current_instrument = current_instrument
        self.current_octave = 4
        self.active_notes = {}  # Maps note with octave (e.g., "C4") to frequency
        
        self.base_frequencies = {
            'C': 261.63,
            'Db': 277.18,
            'D': 293.66,
            'Eb': 311.13,
            'E': 329.63,
            'F': 349.23,
            'Gb': 369.99,
            'G': 392.00,
            'Ab': 415.30,
            'A': 440.00,
            'Bb': 466.16,
            'B': 493.88
        }
        
        # Connect note buttons
        note_buttons = {
            'ckey': 'C',
            'c#key': 'Db',
            'dkey': 'D',
            'd#key': 'Eb',
            'ekey': 'E',
            'fkey': 'F',
            'f#key': 'Gb',
            'gkey': 'G',
            'g#key': 'Ab',
            'akey': 'A',
            'a#key': 'Bb',
            'bkey': 'B'
        }
        for btn, note in note_buttons.items():
            button = getattr(self, btn)
            button.pressed.connect(self.make_press_handler(note))
            button.released.connect(self.make_release_handler(note))
        
        # Connect octave buttons
        self.octaveUp.clicked.connect(self.increase_octave)
        self.octaveDown.clicked.connect(self.decrease_octave)
        
        # Configure display
        self.noteNameA.setReadOnly(True)
        self.noteNameA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.noteNameA.font()
        font.setPointSize(48)
        font.setBold(True)
        self.noteNameA.setFont(font)

    def set_current_instrument(self, instrument):
        '''
        Update the current instrument for the NotesWindow and SoundGenerator.
        '''
        self.current_instrument = instrument
        self.sound.set_current_instrument(instrument)
        print(f"NotesWindow: Switched to instrument {self.current_instrument}")

    def make_press_handler(self, note):
        '''
        Function Description:
            Create a handler for pressing a note button.
        Inputs:
            note (str): The note letter (e.g., 'C', 'D').
        Outputs:
            A function (handler) that when called, plays the corresponding note.
        '''
        def handler():
            note_with_octave = f"{note}{self.current_octave}"
            if note_with_octave in self.active_notes:
                return
            freq = self.base_frequencies[note] * (2 ** (self.current_octave - 4))
            self.active_notes[note_with_octave] = freq
            self.sound.note_on(note_with_octave, instrument=self.current_instrument)
            self.update_display(note)
            self.note_started.emit(note_with_octave)
        return handler

    def make_release_handler(self, note):
        '''
        Function Description:
            Create a handler for releasing a note button.
        Inputs:
            note (str): The note letter (e.g., 'C', 'D').
        Outputs:
            A function (handler) that when called, stops playing the corresponding note.
        '''
        def handler():
            note_with_octave = f"{note}{self.current_octave}"
            if note_with_octave in self.active_notes:
                freq = self.active_notes.pop(note_with_octave)
                self.sound.note_off(note_with_octave, instrument=self.current_instrument)
                self.update_display("")
                self.note_stopped.emit(note_with_octave)
        return handler

    def update_display(self, note):
        '''
        Function Description:
            Update the note display in the UI.
        Inputs:
            note (str): The note letter to display; empty string clears the display.
        Outputs:
            The noteNameA widget is updated with the current note and octave.
        '''
        text = f"{note}{self.current_octave}" if note else ""
        self.noteNameA.setText(text)

    def increase_octave(self):
        '''
        Function Description:
            Increase the current octave.
        Inputs:
            None
        Outputs:
            Increments the current octave value (max 7).
        '''
        if self.current_octave < 7:
            self.current_octave += 1

    def decrease_octave(self):
        '''
        Function Description:
            Decrease the current octave.
        Inputs:
            None
        Outputs:
            Decrements the current octave value (min 1).
        '''
        if self.current_octave > 1:
            self.current_octave -= 1

    def keyPressEvent(self, event):
        '''
        Function Description:
            Handle key press events to start playing notes via keyboard.
        Inputs:
            event (QKeyEvent): The key press event.
        Outputs:
            Initiates note playback if the key corresponds to a valid note.
        '''
        if event.isAutoRepeat():
            return
        key_map = {
            Qt.Key.Key_A: 'C',
            Qt.Key.Key_W: 'Db',
            Qt.Key.Key_S: 'D',
            Qt.Key.Key_E: 'Eb',
            Qt.Key.Key_D: 'E',
            Qt.Key.Key_F: 'F',
            Qt.Key.Key_T: 'Gb',
            Qt.Key.Key_G: 'G',
            Qt.Key.Key_Y: 'Ab',
            Qt.Key.Key_H: 'A',
            Qt.Key.Key_U: 'Bb',
            Qt.Key.Key_J: 'B'
        }
        if note := key_map.get(event.key()):
            self.make_press_handler(note)()

    def keyReleaseEvent(self, event):
        '''
        Function Description:
            Handle key release events to stop playing notes via keyboard.
        Inputs:
            event (QKeyEvent): The key release event.
        Outputs:
            Stops note playback if the key corresponds to a valid note.
        '''
        if event.isAutoRepeat():
            return
        key_map = {
            Qt.Key.Key_A: 'C',
            Qt.Key.Key_W: 'Db',
            Qt.Key.Key_S: 'D',
            Qt.Key.Key_E: 'Eb',
            Qt.Key.Key_D: 'E',
            Qt.Key.Key_F: 'F',
            Qt.Key.Key_T: 'Gb',
            Qt.Key.Key_G: 'G',
            Qt.Key.Key_Y: 'Ab',
            Qt.Key.Key_H: 'A',
            Qt.Key.Key_U: 'Bb',
            Qt.Key.Key_J: 'B'
        }
        if note := key_map.get(event.key()):
            self.make_release_handler(note)()

    def closeEvent(self, event):
        self.finished.emit()  # Emit finished signal when window closes
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    sys.exit(app.exec())