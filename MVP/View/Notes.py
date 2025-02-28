import sys
import os
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QMutex, QMutexLocker, pyqtSignal
from PyQt6 import uic

class SoundGenerator:
    '''
    Function Description:
        Initialize the SoundGenerator, set up the audio stream, and initialize state.
    Inputs:
        None
    Outputs:
        An instance of SoundGenerator ready for generating audio.
    '''
    def __init__(self):
        self.mutex = QMutex()
        self.active_notes = {}
        self.sample_rate = 44100
        self.phase = {}

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=1024,
            channels=1,
            callback=self.audio_callback,
            dtype='float32'
        )
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        '''
        Function Description:
            Audio callback that fills the output buffer with the generated sine waves for active notes.
        Inputs:
            outdata: numpy array for audio output.
            frames: number of frames to generate.
            time: timing information (unused).
            status: stream status (unused).
        Outputs:
            Fills outdata with the combined sine wave samples.
        '''
        with QMutexLocker(self.mutex):
            outdata.fill(0)
            t = np.arange(frames) / self.sample_rate
            for freq in list(self.active_notes.keys()):
                if freq not in self.phase:
                    self.phase[freq] = 0
                samples = 0.3 * np.sin(2 * np.pi * freq * t + self.phase[freq])
                outdata[:, 0] += samples
                self.phase[freq] += 2 * np.pi * freq * frames / self.sample_rate
                self.phase[freq] %= 2 * np.pi

    def note_on(self, frequency):
        '''
        Function Description:
            Start playing a note by adding its frequency to the active notes.
        Inputs:
            frequency (float): The frequency of the note to be played.
        Outputs:
            The note is added to active_notes and will be generated in the audio callback.
        '''
        with QMutexLocker(self.mutex):
            if frequency not in self.active_notes:
                self.active_notes[frequency] = True
                if frequency not in self.phase:
                    self.phase[frequency] = 0

    def note_off(self, frequency):
        '''
        Function Description:
            Stop playing a note by removing its frequency from the active notes.
        Inputs:
            frequency (float): The frequency of the note to stop.
        Outputs:
            The note is removed from active_notes and its phase tracking is deleted.
        '''
        with QMutexLocker(self.mutex):
            if frequency in self.active_notes:
                del self.active_notes[frequency]
            if frequency in self.phase:
                del self.phase[frequency]

class NotesWindow(QMainWindow):
    note_started = pyqtSignal(str)  # Signal for note start
    note_stopped = pyqtSignal(str)  # Signal for note stop
    finished = pyqtSignal()         # Signal emitted when window is closed
    
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'MVP/View/UI/Notes.ui')
        uic.loadUi(ui_path, self)
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        self.sound = SoundGenerator()
        self.current_octave = 4
        self.active_notes = {}  # Maps note with octave (e.g., "C4") to frequency
        
        self.base_frequencies = {
            'C': 261.63,
            'C#': 277.18,
            'D': 293.66,
            'D#': 311.13,
            'E': 329.63,
            'F': 349.23,
            'F#': 369.99,
            'G': 392.00,
            'G#': 415.30,
            'A': 440.00,
            'A#': 466.16,
            'B': 493.88
        }
        
        # Connect note buttons
        note_buttons = {
            'ckey': 'C',
            'c#key': 'C#',
            'dkey': 'D',
            'd#key': 'D#',
            'ekey': 'E',
            'fkey': 'F',
            'f#key': 'F#',
            'gkey': 'G',
            'g#key': 'G#',
            'akey': 'A',
            'a#key': 'A#',
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
            self.sound.note_on(freq)
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
                self.sound.note_off(freq)
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
            Increments the current octave value (max 8).
        '''
        if self.current_octave < 8:
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
            Qt.Key.Key_W: 'C#',
            Qt.Key.Key_S: 'D',
            Qt.Key.Key_E: 'D#',
            Qt.Key.Key_D: 'E',
            Qt.Key.Key_F: 'F',
            Qt.Key.Key_T: 'F#',
            Qt.Key.Key_G: 'G',
            Qt.Key.Key_Y: 'G#',
            Qt.Key.Key_H: 'A',
            Qt.Key.Key_U: 'A#',
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
            Qt.Key.Key_W: 'C#',
            Qt.Key.Key_S: 'D',
            Qt.Key.Key_E: 'D#',
            Qt.Key.Key_D: 'E',
            Qt.Key.Key_F: 'F',
            Qt.Key.Key_T: 'F#',
            Qt.Key.Key_G: 'G',
            Qt.Key.Key_Y: 'G#',
            Qt.Key.Key_H: 'A',
            Qt.Key.Key_U: 'A#',
            Qt.Key.Key_J: 'B'
        }
        if note := key_map.get(event.key()):
            self.make_release_handler(note)()

    def closeEvent(self, event):
        self.sound.stream.stop()
        self.finished.emit()  # Emit finished signal when window closes
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    sys.exit(app.exec())