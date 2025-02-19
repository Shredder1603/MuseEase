import sys
import os
import time
import subprocess
import signal
import psutil
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QPushButton
from PyQt6.QtGui import QBrush, QPen, QColor
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from Notes import NotesWindow

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
        self.notes_window = None

        # ✅ Connect Record Button (Toggle)
        if hasattr(self, 'record'):
            self.record.clicked.connect(self.toggle_recording)
        else:
            print("❌ ERROR: 'Record' button not found in UI")

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
        self.countdown_timer = QTimer()
        self.countdown = 4
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(int(beat_duration * 1000))

    def update_countdown(self):
        if self.countdown > 0:
            print(f"Count-in: {self.countdown}")
            self.countdown -= 1
        else:
            self.countdown_timer.stop()
            print("🎤 Recording started!")
            self.recording = True
            self.launch_notes_ui()

    def launch_notes_ui(self):
        """Open Notes UI for input"""
        self.notes_window = NotesWindow()
        self.notes_window.note_played.connect(self.add_note_to_track)
        self.notes_window.show()

    def close_notes_ui(self):
        """Close Notes UI if it's running."""
        if self.notes_window:
            self.notes_window.close()
            self.notes_window = None

    def get_note_y_position(self, note_name):
        """Map note name to vertical position within a single track"""
        # Note order from BOTTOM (low) to TOP (high)
        note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                
        # Get position within sequence (0-8)
        note_index = note_order.index(note_name)
        
        # Track dimensions
        track_top = 0  # For top track (change this number for different tracks)
        track_height = self.track_height
        
        # Calculate position within track (inverted for C=bottom)
        # Using 40-20px range to keep within track bounds
        y_offset = track_top + (track_height - 40)  # Center vertically
        return y_offset + (note_index * -4)  # Negative multiplier creates upward slope

    def add_note_to_track(self, note_name):
        """Modified to work within track bounds"""
        note_height = 20  # Smaller to fit in track
        note_width = 40
        
        # Get y-position within selected track
        y_pos = self.get_note_y_position(note_name)
        
        # Horizontal positioning
        x_pos = max(self.note_positions.values(), default=0) + note_width
        self.note_positions[note_name] = x_pos
        
        # Create note block
        note_block = QGraphicsRectItem(x_pos, y_pos, note_width, note_height)
        note_block.setBrush(QBrush(QColor(100, 149, 237)))
        note_block.setPen(QPen(QColor(255, 255, 255)))
        self.scene.addItem(note_block)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAWTest()
    window.show()
    sys.exit(app.exec())