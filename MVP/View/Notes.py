import sys
import os
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QMutex, QMutexLocker, pyqtSignal
from PyQt6 import uic
import matplotlib.pyplot as plt
import soundfile as sf
import threading


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
        self.sf = sf
        self.mutex = QMutex()
        self.active_notes = {}
        self.notes = {}
        self.samplerate = None
        self.read_notes()

        self.stream = sd.OutputStream(samplerate=self.notes["A0"][1], channels=1, callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        """ Stream callback to play audio samples. """
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

    def note_on(self, note: str, loop: bool = False):

        '''
        Function Description:
            Start playing a note by adding its frequency to the active notes.
        Inputs:
            frequency (float): The frequency of the note to be played.
        Outputs:
            The note is added to active_notes and will be generated in the audio callback.
        '''
        if note not in self.active_notes:
            data, samplerate = self.notes[note]

            if self.samplerate is None:
                self.samplerate = samplerate

            self.mutex.lock()
            self.active_notes[note] = {"data": data, "play_pos": 0, "loop": loop}
            self.mutex.unlock()


    def note_off(self, note: str):
        '''
        Function Description:
            Stop playing a note by removing its frequency from the active notes.
        Inputs:
            frequency (float): The frequency of the note to stop.
        Outputs:
            The note is removed from active_notes and its phase tracking is deleted.
        '''
        self.mutex.lock()
        if note in self.active_notes:
            del self.active_notes[note]
        self.mutex.unlock()

    def read_notes(self):
        for filename in os.listdir(os.getcwd() + "/Instruments/Piano/"):
            filepath = os.getcwd() + "/Instruments/Piano/" + filename
            data, samplerate = self.sf.read(filepath)

            if data.ndim > 1:
                data = np.mean(data, axis=1)

            max_idx = np.argmax(np.abs(data))
            start_frame = 0
            for x in range(max_idx - 1, -1, -1):
                if np.abs(data[x]) <= 0.008 * np.abs(data[max_idx]):
                    start_frame = x
                    break
            end_frame = len(data)

            snippet = data[start_frame:end_frame]
            self.notes[filename.split(".")[0]] = (snippet, samplerate)
            if self.samplerate is None:
                self.samplerate = samplerate

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