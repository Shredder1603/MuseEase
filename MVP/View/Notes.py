import sys
import os
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QMutex, QMutexLocker, pyqtSignal
from PyQt6 import uic
import matplotlib.pyplot as plt

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
        import soundfile as sf
        import threading
        self.threading = threading
        self.sf = sf
        self.audio_path = os.getcwd() + "/Instruments/Piano/"
        self.mutex = QMutex()
        self.active_notes = {}

    def note_on(self, note: str):

        '''
        Function Description:
            Start playing a note by adding its frequency to the active notes.
        Inputs:
            frequency (float): The frequency of the note to be played.
        Outputs:
            The note is added to active_notes and will be generated in the audio callback.
        '''
        with QMutexLocker(self.mutex):
            if note not in self.active_notes:
                self.active_notes[note] = True
                filename = self.audio_path + note + ".aiff"
                thread = self.threading.Thread(target=self.play_audio, args=(filename,))
                thread.start()

    def note_off(self, note: str):
        '''
        Function Description:
            Stop playing a note by removing its frequency from the active notes.
        Inputs:
            frequency (float): The frequency of the note to stop.
        Outputs:
            The note is removed from active_notes and its phase tracking is deleted.
        '''
        with QMutexLocker(self.mutex):
            if note in self.active_notes:
                del self.active_notes[note]

    def play_audio(self, filename: str):
        try:
            data, samplerate = self.sf.read(filename)
            if data.ndim > 1:
                data = np.mean(data, axis=1)

            end_frame = int(2 * samplerate)  # set end idx to 2 seconds in
            max_idx = np.argmax(abs(data))  # find where sound bite has max amplitude
            start_frame = 0  # initialize to zero idx

            # find first min amplitude at idx closest to max_idx
            for x in range(max_idx - 1, -1, -1):
                if abs(data[x]) < 0.0010:
                    start_frame = x
                    break

            # if end idx out of bounds, set to length of data array
            if end_frame > len(data):
                end_frame = len(data)

            # splice data array and save in snippet
            snippet = data[start_frame:end_frame]
            sd.play(snippet, samplerate)
            # sd.wait()  # wait until soundbite finishes
        except self.sf.SoundFileError:
            print(f"Error: could not read {filename}")
        except Exception as e:
            print(f"Unexpected error: {e}")

class NotesWindow(QMainWindow):
    note_started = pyqtSignal(str)  # Signal for note start
    note_stopped = pyqtSignal(str)  # Signal for note stop
    finished = pyqtSignal()         # Signal emitted when window is closed
    
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/Notes.ui')
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
            self.sound.note_on(note_with_octave)
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
                self.sound.note_off(note_with_octave)
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
        self.finished.emit()  # Emit finished signal when window closes
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NotesWindow()
    window.show()
    sys.exit(app.exec())