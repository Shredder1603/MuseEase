import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                            QGraphicsScene, QGraphicsRectItem, QGraphicsItemGroup)
from PyQt6.QtGui import QBrush, QPen, QColor, QCursor, QPainter, QFont, QIcon
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6 import uic

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
from Notes import NotesWindow

class DraggableContainer(QGraphicsRectItem):
    def __init__(self, track_height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_height = track_height
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
        self.setZValue(1)
        self.notes_group = QGraphicsItemGroup(self)
        self.current_track = 0

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.snap_to_tracks()
        if self.x() < 0:
            self.setX(0)

    def snap_to_tracks(self):
        new_y = round(self.y() / self.track_height) * self.track_height
        self.setY(new_y)
        self.current_track = int(new_y / self.track_height)

class DAWTest(QMainWindow):
    def __init__(self):
        super().__init__()
        
        ui_path = os.path.join(os.path.dirname(__file__), "UI/DAW.ui")
        uic.loadUi(ui_path, self)
        
        # Track configuration
        self.track_height = 80
        self.base_note_width = 100
        self.note_height = 20
        self.current_x = 0  # Tracks recorded notes, but playhead can move independently
        self.measure_width = 400
        self.bpm = 120
        self.time_signature = "4/4"
        self.current_measure = 1
        self.current_beat = 1
        
        # Graphics setup
        self.track_scene = QGraphicsScene()
        self.trackView.setScene(self.track_scene)
        self.trackView.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.trackView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self.time_scene = QGraphicsScene()
        self.timeView.setScene(self.time_scene)
        self.timeView.setFixedHeight(60)
        
        # Initialize core elements
        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        self.update_tracks_and_markers()
        self.update_time_display()
        
        # State management
        self.recording = False
        self.recording_session = None
        self.playing = False
        self.paused = False
        self.playback_timer = QTimer()
        self.playback_timer.setInterval(10)
        self.playback_timer.timeout.connect(self.update_playhead_continuous)
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))  # Always initialize playhead
        self.playhead.setZValue(10)
        self.track_scene.addItem(self.playhead)
        self.playhead.setVisible(True)  
        self.playback_start_time = None
        self.paused_position = None
        self.current_container = None
        self.active_note_items = {}

        # UI connections
        self.record.clicked.connect(self.toggle_recording)
        self.play.clicked.connect(self.toggle_playback)
        self.stop.clicked.connect(self.stop_playback)
        self.connect_rewind_button()
        self.connect_fastforward_button()

        # Real-time update timer
        self.update_timer = QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.update_active_notes)

        # Load icon paths
        icons_dir = os.path.join(os.path.dirname(__file__), "Icons")  # Updated as per your change
        self.play_icon_path = os.path.join(icons_dir, "Play.png")
        self.pause_icon_path = os.path.join(icons_dir, "Pause.png")
        self.set_button_icons()

    def set_button_icons(self):
        """Set the play button icon based on current state."""
        if self.playing and not self.paused:
            icon = QIcon(self.pause_icon_path)
        else:
            icon = QIcon(self.play_icon_path)
        self.play.setIcon(icon)

    def update_tracks_and_markers(self):
        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        
        view_width = max(self.trackView.width(), self.current_x + 2000)
        
        track_brush = QBrush(QColor(45, 45, 45))
        track_pen = QPen(QColor(80, 80, 80))
        for i in range(5):
            track = QGraphicsRectItem(0, i * self.track_height, view_width, self.track_height)
            track.setBrush(track_brush)
            track.setPen(track_pen)
            self.track_background_group.addToGroup(track)
        
        measure_pen = QPen(QColor(100, 100, 100), 2, Qt.PenStyle.SolidLine)
        beat_tick_pen = QPen(QColor(100, 100, 100), 1, Qt.PenStyle.DotLine)
        measures = int(view_width / self.measure_width) + 2
        for m in range(measures):
            x_pos = m * self.measure_width
            self.track_background_group.addToGroup(
                self.track_scene.addLine(x_pos, 0, x_pos, 5 * self.track_height, measure_pen)
            )
            for b in range(1, 4):
                beat_x = x_pos + b * self.base_note_width
                self.track_scene.addLine(beat_x, 0, beat_x, 5 * self.track_height, beat_tick_pen)
            text = self.track_scene.addText(str(m + 1))
            text.setPos(x_pos + 10, 5)
            text.setDefaultTextColor(QColor(150, 150, 150))
            self.track_background_group.addToGroup(text)
        
        self.track_scene.setSceneRect(0, 0, view_width, 5 * self.track_height)

    def update_time_display(self):
        self.time_scene.clear()
        time_font = QFont("Arial", 12)
        
        measure_text = self.time_scene.addText(f"Measure: {self.current_measure}:{self.current_beat}")
        measure_text.setPos(10, 10)
        measure_text.setDefaultTextColor(QColor(200, 200, 200))
        measure_text.setFont(time_font)
        
        tempo_text = self.time_scene.addText(f"Tempo: {self.bpm} BPM")
        tempo_text.setPos(200, 10)
        tempo_text.setDefaultTextColor(QColor(200, 200, 200))
        tempo_text.setFont(time_font)
        
        ts_text = self.time_scene.addText(f"Time: {self.time_signature}")
        ts_text.setPos(400, 10)
        ts_text.setDefaultTextColor(QColor(200, 200, 200))
        ts_text.setFont(time_font)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_tracks_and_markers()

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.recording_session = {
            'start_time': time.time(),
            'active_notes': {},
            'notes': []
        }
        self.notes_window = NotesWindow()
        self.notes_window.note_started.connect(self.note_started)
        self.notes_window.note_stopped.connect(self.note_stopped)
        self.notes_window.finished.connect(self.stop_recording)
        self.notes_window.show()
        
        self.current_container = DraggableContainer(self.track_height, self.current_x, 0, 0, self.track_height)
        self.current_container.setBrush(QBrush(QColor(173, 216, 230, 100)))
        self.current_container.setPen(QPen(QColor(70, 130, 180, 200), 2))
        self.track_scene.addItem(self.current_container)
        self.update_timer.start()

        # Ensure playhead is visible and at start
        if self.playhead is None or not self.playhead.isVisible():
            self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
            self.playhead.setVisible(True)  # Explicitly set visible
        self.playback_start_time = self.recording_session['start_time']
        self.playback_timer.start()

    def note_started(self, note_name):
        if self.recording and note_name not in self.recording_session['active_notes']:
            start_time = time.time()
            self.recording_session['active_notes'][note_name] = start_time
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            x = start_beat * self.base_note_width
            y = self.calculate_note_position(note_name)
            note = QGraphicsRectItem(0, 0, 0, self.note_height)
            note.setPos(x, y)
            note.setBrush(QBrush(QColor(100, 149, 237)))
            note.setPen(QPen(Qt.GlobalColor.white))
            note.setParentItem(self.current_container)
            self.active_note_items[note_name] = note

    def note_stopped(self, note_name):
        if self.recording and note_name in self.recording_session['active_notes']:
            start_time = self.recording_session['active_notes'].pop(note_name)
            stop_time = time.time()
            duration = stop_time - start_time
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            duration_beats = duration / time_per_beat
            self.recording_session['notes'].append({
                'note_name': note_name,
                'start_beat': start_beat,
                'duration_beats': duration_beats
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                width = duration_beats * self.base_note_width
                note.setRect(0, 0, width, self.note_height)
                self.update_container_size()

    def update_active_notes(self):
        if not self.recording or not self.current_container:
            return
        current_time = time.time()
        time_per_beat = 60 / self.bpm
        for note_name, start_time in list(self.recording_session['active_notes'].items()):
            if note_name in self.active_note_items:
                duration = current_time - start_time
                duration_beats = duration / time_per_beat
                width = duration_beats * self.base_note_width
                note = self.active_note_items[note_name]
                note.setRect(0, 0, width, self.note_height)
        self.update_container_size()

    def update_container_size(self):
        if not self.current_container or not self.recording_session['notes'] and not self.active_note_items:
            return
        max_end_beat = 0
        if self.recording_session['notes']:
            max_end_beat = max(note['start_beat'] + note['duration_beats'] for note in self.recording_session['notes'])
        for note_name, start_time in self.recording_session['active_notes'].items():
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            current_time = time.time()
            duration_beats = (current_time - start_time) / time_per_beat
            end_beat = start_beat + duration_beats
            max_end_beat = max(max_end_beat, end_beat)
        session_width = max_end_beat * self.base_note_width
        self.current_container.setRect(0, 0, session_width, self.track_height)

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.update_timer.stop()
        self.playback_timer.stop()
        if self.notes_window:
            self.notes_window.close()
            self.notes_window = None
        current_time = time.time()
        for note_name in list(self.recording_session['active_notes'].keys()):
            start_time = self.recording_session['active_notes'].pop(note_name)
            duration = current_time - start_time
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            duration_beats = duration / time_per_beat
            self.recording_session['notes'].append({
                'note_name': note_name,
                'start_beat': start_beat,
                'duration_beats': duration_beats
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                note.setRect(0, 0, duration_beats * self.base_note_width, self.note_height)
        self.update_container_size()
        if self.current_container:
            self.current_x += self.current_container.rect().width()
            self.current_container = None
        self.update_tracks_and_markers()
        # Ensure playhead remains visible after recording stops
        if self.playhead and not self.playhead.isVisible():
            self.playhead.setVisible(True)
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)  # Reset to start

    def calculate_note_position(self, note_name):
        note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note = note_name[:-1]
        octave = int(note_name[-1])
        note_index = note_order.index(note)
        position = (octave - 3) * 12 + note_index
        total_notes = 24
        y_pos = (1 - position / total_notes) * (self.track_height - self.note_height)
        return y_pos

    def toggle_playback(self):
        if self.paused:
            # Resume playback from paused position
            self.paused = False
            self.playback_start_time = time.time() - (self.paused_position / (self.base_note_width * self.bpm / 60))
            if self.playhead is None:
                self.playhead = self.track_scene.addLine(self.paused_position, 0, self.paused_position, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
                self.track_scene.addItem(self.playhead)  # ✅ Explicitly add to scene
            self.playhead.setVisible(True)
            self.playback_timer.start()
        elif self.playing:
            # Pause playback
            self.paused = True
            self.paused_position = self.playhead.line().x1() if self.playhead else 0
            self.playback_timer.stop()
        else:
            # Start playback
            self.playing = True
            self.paused = False
            self.paused_position = None
            self.playback_start_time = time.time()
            if self.playhead is None:
                self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
                self.track_scene.addItem(self.playhead)  # ✅ Explicitly add to scene
            self.playhead.setVisible(True)
            self.playback_timer.start()
        self.set_button_icons()


    def stop_playback(self):
        self.playing = False
        self.paused = False
        self.paused_position = None
        self.playback_timer.stop()
        if self.playhead:
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)  # Reset to start instead of removing
            self.playhead.setVisible(True)  # Ensure visible after stopping
        self.update_time_display()

    def start_playback(self):
        # Start playback (always allowed, even with no notes)
        self.playing = True
        self.paused = False
        self.paused_position = None
        self.playback_start_time = time.time()
        if self.playhead is None or not self.playhead.isVisible():
            self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
            self.playhead.setVisible(True)
        self.playback_timer.start()

    def update_playhead_continuous(self):
        if self.playback_start_time is None or self.paused:
            return
        elapsed_time = time.time() - self.playback_start_time
        pixels_per_second = self.base_note_width * self.bpm / 60
        x_position = elapsed_time * pixels_per_second
        if x_position >= 2000:  # Arbitrary limit for empty playback (e.g., 20 seconds at 120 BPM)
            self.stop_playback()
            return
        if self.playhead:
            self.playhead.setLine(x_position, 0, x_position, 5 * self.track_height)
            self.playhead.setVisible(True)  # Ensure visible during updates
        else:
            self.playhead = self.track_scene.addLine(x_position, 0, x_position, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
            self.playhead.setVisible(True)
        beat_position = x_position / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()

        if self.recording:
            view_width = self.trackView.viewport().width()
            target_x = x_position - (view_width / 2)
            if target_x < 0:
                target_x = 0
            self.trackView.horizontalScrollBar().setValue(int(target_x))
        else:
            self.trackView.ensureVisible(QRectF(x_position, 0, 10, self.track_height))
    
    def connect_rewind_button(self):
        """Connect the rewind button to its handler"""
        self.rewind.clicked.connect(self.rewind_one_measure)

    def rewind_one_measure(self):
        """Rewind playback by one measure"""
        if self.playhead is None:
            return
            
        current_x = self.playhead.line().x1()
        # One measure is 4 beats * base_note_width
        measure_width = 4 * self.base_note_width
        
        # Calculate new position (go back one measure)
        new_x = max(0, current_x - measure_width)
        
        # Update playhead position
        self.playhead.setLine(new_x, 0, new_x, 5 * self.track_height)
        
        # If we're playing or paused, update the playback start time
        if self.playing or self.paused:
            # Calculate the time that corresponds to the new position
            pixels_per_second = self.base_note_width * self.bpm / 60
            new_elapsed_time = new_x / pixels_per_second
            self.playback_start_time = time.time() - new_elapsed_time
            
            # If paused, update the pause position
            if self.paused:
                self.paused_position = new_x
        
        # Update measure and beat display
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        
        # Ensure the playhead is visible in the view
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))
    
    def connect_fastforward_button(self):
        """Connect the fast forward button to its handler"""
        self.fastForward.clicked.connect(self.fastforward_one_measure)

    def fastforward_one_measure(self):
        """Fast forward playback by one measure"""
        if self.playhead is None:
            return
            
        current_x = self.playhead.line().x1()
        # One measure is 4 beats * base_note_width
        measure_width = 4 * self.base_note_width
        
        # Calculate new position (go forward one measure)
        new_x = current_x + measure_width
        
        # Make sure we have enough scene width
        required_width = new_x + measure_width
        current_width = self.track_scene.width()
        if required_width > current_width:
            self.update_tracks_and_markers()  # This will extend the scene if needed
        
        # Update playhead position
        self.playhead.setLine(new_x, 0, new_x, 5 * self.track_height)
        
        # If we're playing or paused, update the playback start time
        if self.playing or self.paused:
            # Calculate the time that corresponds to the new position
            pixels_per_second = self.base_note_width * self.bpm / 60
            new_elapsed_time = new_x / pixels_per_second
            self.playback_start_time = time.time() - new_elapsed_time
            
            # If paused, update the pause position
            if self.paused:
                self.paused_position = new_x
        
        # Update measure and beat display
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        
        # Ensure the playhead is visible in the view
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAWTest()
    window.show()
    sys.exit(app.exec())