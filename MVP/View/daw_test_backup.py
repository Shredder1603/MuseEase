import sys
import os
import time
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QPushButton
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6 import uic
from PyQt6.QtCore import Qt
import signal
import psutil
import threading

class DAWTest(QMainWindow):
    def __init__(self):
        super().__init__()

        # ✅ Load UI
        ui_path = os.path.join(os.path.dirname(__file__), "UI/DAW.ui")
        uic.loadUi(ui_path, self)

        # ✅ Set up QGraphicsView for track display
        self.scene = QGraphicsScene()
        self.trackView.setScene(self.scene)

        # ✅ Define Track Dimensions
        self.track_height = 60
        self.track_width = 1200  # Expandable width
        self.tracks = []
        self.active_notes = {}  # Track active notes to prevent duplicates

        # ✅ Create 5 dynamic tracks
        track_brush = QBrush(QColor(64, 64, 64))  # Gray background for tracks
        track_pen = QPen(QColor(200, 200, 200))   # Light gray border

        for i in range(5):
            track = QGraphicsRectItem(0, i * self.track_height, self.track_width, self.track_height)
            track.setBrush(track_brush)
            track.setPen(track_pen)
            self.scene.addItem(track)
            self.tracks.append(track)

        # ✅ Set scene boundaries
        self.scene.setSceneRect(0, 0, self.track_width, self.track_height * 5)

        # ✅ Recording Setup
        self.recording = False
        self.note_positions = {}  # Stores recorded note positions
        self.notes_process = None  # To keep track of Notes.py subprocess

        # ✅ Connect Record Button (Toggle)
        if hasattr(self, 'record'):
            self.record.clicked.connect(self.toggle_recording)
        else:
            print("❌ ERROR: 'Record' button not found in UI")

        # Start thread to read notes from file
        self.read_notes_thread = threading.Thread(target=self.read_notes_from_file)
        self.read_notes_thread.daemon = True
        self.read_notes_thread.start()

    def toggle_recording(self):
        """Start or stop recording when the button is pressed."""
        if self.recording:
            print("🛑 Recording stopped!")
            self.recording = False
            self.close_notes_ui()
        else:
            self.start_recording()

    def start_recording(self):
        """Start a 4-beat count-in and launch recording mode."""
        bpm = 120
        beat_duration = 60 / bpm

        print("Starting 4-beat count-in...")
        for i in range(4, 0, -1):
            print(f"Count-in: {i}")
            time.sleep(beat_duration)

        print("🎤 Recording started!")
        self.recording = True

        # ✅ Open Notes UI for input
        notes_path = os.path.join(os.path.dirname(__file__), "../../Notes.py")
        venv_python = os.path.join(os.path.dirname(__file__), "../../.venv/Scripts/python.exe")
        self.notes_process = subprocess.Popen([venv_python, notes_path])

    def close_notes_ui(self):
        """Close Notes UI if it's running."""
        if self.notes_process:
            parent = psutil.Process(self.notes_process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            self.notes_process = None

    def read_notes_from_file(self):
        """Read notes from file and update DAW."""
        while True:
            if self.recording:
                try:
                    with open('note_input.txt', 'r') as file:
                        lines = file.readlines()
                    for line in lines:
                        note_name = line.strip()
                        if note_name not in self.active_notes:
                            self.active_notes[note_name] = self.add_note_to_track(note_name)
                    # Clear the file after reading to avoid duplication
                    with open('note_input.txt', 'w') as file:
                        file.truncate(0)
                except Exception as e:
                    print(f"Error reading notes: {e}")
                time.sleep(0.1)  # Delay to avoid overloading the loop

    def add_note_to_track(self, note_name):
        """Adds a dynamically placed note to the correct track."""
        note_height = 40
        note_width = 60
        y_pos = self.get_note_y_position(note_name)

        # Move note to the next available x position
        x_pos = max(self.note_positions.values(), default=0) + note_width
        self.note_positions[note_name] = x_pos

        # 🎵 Note block with proper coloring
        note_block = QGraphicsRectItem(x_pos, y_pos, note_width, note_height)
        note_block.setBrush(QBrush(QColor(100, 149, 237)))  # Cornflower Blue (lighter)
        note_block.setPen(QPen(QColor(255, 255, 255)))     # White border
        self.scene.addItem(note_block)

        return note_block  # Store for later removal

    def get_note_y_position(self, note_name):
        """Map note name to correct track layer."""
        note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return note_order.index(note_name) * 40


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAWTest()
    window.show()
    sys.exit(app.exec())
