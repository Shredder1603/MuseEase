from PyQt6.QtWidgets import (QMainWindow, QWidget, QLineEdit, QHBoxLayout, QMessageBox, QFileDialog, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsItemGroup)
from PyQt6.QtGui import QBrush, QPen, QColor, QIcon, QFont, QPainter, QAction
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QRectF, QMutex
from .Notes import NotesWindow, SoundGenerator
from .draggable_container import DraggableContainer
import sounddevice as sd
import time
import soundfile as sf
import json
import scipy
import subprocess
import tempfile
import numpy as np
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.daw = None  # Reference to the DAW instance

    def set_daw(self, daw):
        self.daw = daw

    def mousePressEvent(self, event):
        # Map the click position to scene coordinates
        pos = event.scenePos()
        x_pos = pos.x()
        y_pos = pos.y()
        print(f"Click at scene coordinates: x={x_pos}, y={y_pos}")

        # Check if a DraggableContainer was clicked
        items = self.items(pos)
        for item in items:
            if isinstance(item, DraggableContainer):
                print(f"Container clicked at track {item.current_track}, ignoring playhead movement")
                super().mousePressEvent(event)  # Let the scene handle the event (e.g., for dragging)
                return

        # Move the playhead to the exact clicked x-position (no snapping)
        if self.daw:
            self.daw.playhead.setLine(x_pos, 0, x_pos, 5 * self.daw.track_height)
            print(f"Moved playhead to x={x_pos}")
            # Update the playback start time to match the new playhead position
            pixels_per_second = self.daw.base_note_width * self.daw.bpm / 60
            elapsed_time = x_pos / pixels_per_second
            self.daw.playback_start_time = time.perf_counter() - elapsed_time
            # Update the measure and beat display
            beat_position = x_pos / self.daw.base_note_width
            self.daw.current_measure = int(beat_position // 4) + 1
            self.daw.current_beat = int(beat_position % 4) + 1
            self.daw.update_time_display()
            self.daw.trackView.ensureVisible(QRectF(x_pos, 0, 10, self.daw.track_height))

        # Let the scene handle the event for track selection
        super().mousePressEvent(event)

class DAW(QMainWindow, QWidget):
    mutex = QMutex()

    def __init__(self, presenter=None):
        super().__init__()

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ui_path = os.path.join(project_root, "MVP", "View", "UI", "DAW.ui")
        print(f"UI Path: {ui_path}")
        uic.loadUi(ui_path, self)

        self.track_height = 80
        self.base_note_width = 100
        self.note_height = 20
        self.current_x = 0
        self.measure_width = 400
        self.bpm = 120
        self.time_signature = "4/4"
        self.current_measure = 1
        self.current_beat = 1
        self.selected_track_index = 0  # Store the currently selected track index

        # Use the custom scene
        self.track_scene = CustomGraphicsScene()
        self.track_scene.set_daw(self)  # Set the DAW reference
        self.trackView.setScene(self.track_scene)
        self.trackView.setInteractive(True)
        self.trackView.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.trackView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.track_scene.selectionChanged.connect(self.update_track_selection_feedback)
        self.trackView.setMinimumHeight(5 * self.track_height + 50)  # Ensure all tracks are visible
        self.trackView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.containers = []
        
        self.time_layout = QHBoxLayout(self.timeView)
        self.timeView.setFixedHeight(60)
        self.measure_edit = QLineEdit(f"Measure: {self.current_measure}:{self.current_beat}")
        self.tempo_edit = QLineEdit(f"Tempo: {self.bpm} BPM")
        self.time_edit = QLineEdit(f"Time: {self.time_signature}")
        self.time_layout.addWidget(self.measure_edit)
        self.time_layout.addSpacing(20)
        self.time_layout.addWidget(self.tempo_edit)
        self.time_layout.addSpacing(20)
        self.time_layout.addWidget(self.time_edit)

        font = QFont("Arial", 12)
        self.measure_edit.setFont(font)
        self.tempo_edit.setFont(font)
        self.time_edit.setFont(font)
        self.measure_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.tempo_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.time_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.timeView.setStyleSheet("background-color: #333333; border: 1px solid #555555;")

        self.measure_edit.editingFinished.connect(self.update_measure)
        self.tempo_edit.editingFinished.connect(self.update_tempo)
        self.time_edit.editingFinished.connect(self.update_time)

        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        self.update_tracks_and_markers()
        if self.track_rects:  # Check if track_rects is populated
            self.selected_track_index = 0
            self.track_rects[0].setSelected(True)  # Visually select the first track by default
            print(f"Default selected track {self.selected_track_index}")
            self.update_track_selection_feedback()
        else:
            print("Warning: track_rects not initialized before setting default selection")
        self.update_time_display()

        self.recording = False
        self.recording_session = None
        self.playing = False
        self.paused = False
        self.playback_timer = QTimer()
        self.playback_timer.setInterval(5)  # Reduced for smoother playhead movement
        self.playback_timer.timeout.connect(self.update_playhead_continuous)
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
        self.playhead.setZValue(10)
        self.playhead.setVisible(True)
        self.playback_start_time = None
        self.paused_position = None
        self.current_container = None
        self.active_note_items = {}

        self.sample_rate = 44100
        self.active_playback_notes = {}
        self.phase = {}
        self.notes_window = None  # Initialized later in start_recording
        self.preloaded_samples = {}  # Store preloaded samples
        self.load_instrument_samples("Piano")  # Preload samples at startup
        self.sound = SoundGenerator(preloaded_samples=self.preloaded_samples)  # Use preloaded samples
        self.playback_stream = sd.OutputStream(
            samplerate=self.sound.notes["A0"][1] if "A0" in self.sound.notes else self.sample_rate,
            channels=1,
            callback=self.playback_audio_callback,
        )

        self.note_playback_timer = QTimer()
        self.note_playback_timer.setInterval(10)
        self.note_playback_timer.timeout.connect(self.check_note_playback)
        self.scheduled_notes = []

        self.record.clicked.connect(self.toggle_recording)
        self.play.clicked.connect(self.toggle_playback)
        self.connect_rewind_button()
        self.connect_fastforward_button()

        self.metronome_on = False
        self.metronome_timer = QTimer()
        self.metronome_timer.setInterval(int(60000 / self.bpm))
        self.metronome_timer.timeout.connect(self.metronome_click)
        self.metronome.clicked.connect(self.toggle_metronome)

        self.update_timer = QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.update_active_notes)

        # Add countoff timer and state
        self.countoff_timer = QTimer()
        self.countoff_timer.setInterval(int(60000 / self.bpm))
        self.countoff_timer.timeout.connect(self.handle_countoff)
        self.countoff_beats = 0  # Track the number of countoff beats
        self.countoff_active = False  # Flag to indicate if countoff is in progress

        icons_dir = os.path.join(os.path.dirname(__file__), "Icons")
        print("ICONS: " + icons_dir)
        self.play_icon_path = os.path.join(icons_dir, "Play.png")
        self.pause_icon_path = os.path.join(icons_dir, "Pause.png")
        self.set_button_icons()

        self.autosave_file = "./Saves/autosave.muse"
        self.note_order = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

        self.presenter = presenter
        self.exit_to_menu = self.findChild(QAction, "back")
        self.exit_to_menu.triggered.connect(self.exit_to_main_menu)
        
        # EXPORT FILE HANDLING 
        self.exportMP3 = self.findChild(QAction, "exportMP3")
        self.exportMP3.triggered.connect(self.export_as_mp3)
        
        self.instruments = {}
        self.load_instrument_samples("Piano")

    def keyPressEvent(self, event):
        '''
        Handle key presses, including Delete to remove selected track.
        '''
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.track_scene.selectedItems()
            if selected_items:
                self.delete_selected_container(selected_items[0])
        super().keyPressEvent(event) 
    
    def delete_selected_container(self, container):
        '''
        Remove the specified container from the scene and containers list.
        '''
        if container in self.containers:
            self.track_scene.removeItem(container)
            self.containers.remove(container)
            self.autosave()
            self.update_tracks_and_markers()   
        
    def set_button_icons(self):
        '''
        Updates play/pause button icon based on state
        '''
        if self.playing and not self.paused:
            icon = QIcon(self.pause_icon_path)
        else:
            icon = QIcon(self.play_icon_path)
        self.play.setIcon(icon)

    def update_track_selection_feedback(self):
        '''
        Update visual feedback for selected tracks and update selected_track_index.
        '''
        selected_items = self.track_scene.selectedItems()
        for track in self.track_rects:
            if track in selected_items:
                track.setBrush(QBrush(QColor(45, 45, 45)))  # Keep default background
                track.setPen(QPen(QColor(255, 255, 0), 2))  # Yellow border
                self.selected_track_index = track.data(0) - 1
                print(f"Selected track {self.selected_track_index} (data: {track.data(0)})")
            else:
                track.setBrush(QBrush(QColor(45, 45, 45)))
                track.setPen(QPen(QColor(80, 80, 80)))
        if not selected_items:
            print("No track selected, preserving previous selected_track_index")
                
    def update_tracks_and_markers(self):
        '''
        Redraws track backgrounds, measure lines, and labels
        '''
        # Clear existing track background group if it exists
        if self.track_background_group is not None:
            self.track_scene.removeItem(self.track_background_group)
        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        view_width = max(self.trackView.width(), self.current_x + 2000)
        track_brush = QBrush(QColor(45, 45, 45))
        track_pen = QPen(QColor(80, 80, 80))
        self.track_rects = []
        
        # Add tracks as top-level items (not in the group)
        for i in range(5):
            track = QGraphicsRectItem(0, i * self.track_height, view_width, self.track_height)
            track.setBrush(track_brush)
            track.setPen(track_pen)
            track.setData(0, i + 1)  # Set data to 1, 2, 3, 4, 5
            track.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
            track.setAcceptHoverEvents(True)
            self.track_scene.addItem(track)  # Add directly to scene, not group
            self.track_rects.append(track)
        
        # Add measure lines and labels to the group
        measure_pen = QPen(QColor(100, 100, 100), 2, Qt.PenStyle.SolidLine)
        beat_tick_pen = QPen(QColor(100, 100, 100), 1, Qt.PenStyle.DotLine)
        measures = int(view_width / self.measure_width) + 2
        for m in range(measures):
            x_pos = m * self.measure_width
            self.track_background_group.addToGroup(
                self.track_scene.addLine(x_pos, 0, x_pos, 5 * self.track_height, measure_pen))
            for b in range(1, 4):
                beat_x = x_pos + b * self.base_note_width
                self.track_scene.addLine(beat_x, 0, beat_x, 5 * self.track_height, beat_tick_pen)
            text = self.track_scene.addText(str(m + 1))
            text.setPos(x_pos + 10, 5)
            text.setDefaultTextColor(QColor(150, 150, 150))
            self.track_background_group.addToGroup(text)
        
        self.track_scene.setSceneRect(0, 0, view_width, 5 * self.track_height)
        self.update_track_selection_feedback()

    def update_time_display(self):
        '''
        Updates time-related UI elements with current values
        '''
        self.measure_edit.setText(f"Measure: {self.current_measure}:{self.current_beat}")
        self.tempo_edit.setText(f"Tempo: {self.bpm} BPM")
        self.time_edit.setText(f"Time: {self.time_signature}")

    def resizeEvent(self, event):
        '''
        Resizes track markers and notes windows based off window size
        '''
        super().resizeEvent(event)
        self.update_tracks_and_markers()
        if self.notes_window and self.recording:
            self.snap_notes_window()

    def toggle_recording(self):
        '''
        Toggles recording state between start/stop
        '''
        if self.recording:
            self.stop_recording()
        else:
            # Check if a track is selected
            selected_items = self.track_scene.selectedItems()
            print(f"Before recording: selected_track_index={self.selected_track_index}, selected_items={len(selected_items)}")
            if not selected_items:
                QMessageBox.warning(self, "No Track Selected", "Please select a track before recording.")
                return
            self.start_recording()

    def start_recording(self):
        '''
        Initiates a 4-beat countoff before starting a new recording.
        '''
        if self.countoff_active:
            print("Countoff already in progress, ignoring new recording request")
            return

        self.countoff_active = True
        self.countoff_beats = 0
        self.countoff_timer.setInterval(int(60000 / self.bpm))  # Match the BPM
        self.countoff_timer.start()
        print("Starting 4-beat countoff before recording")

    def start_recording_internal(self):
        '''
        Begins a new recording with new container and timers (called after countoff).
        '''
        self.recording = True
        self.recording_session = {
            'start_time': time.time(),
            'active_notes': {},
            'notes': []
        }
        if self.notes_window is None:
            self.notes_window = NotesWindow(sound_generator=self.sound)
            self.notes_window.note_started.connect(self.note_started)
            self.notes_window.note_stopped.connect(self.note_stopped)
            self.notes_window.finished.connect(self.stop_recording)
        self.notes_window.show()
        self.notes_window.activateWindow()
        self.notes_window.setFocus()
        self.snap_notes_window()

        # Use the stored selected track index
        track_index = self.selected_track_index
        if track_index < 0 or track_index >= 5:
            print(f"Invalid track index {track_index}, defaulting to track 0")
            track_index = 0
            self.selected_track_index = 0
        y_position = track_index * self.track_height
        print(f"Recording on track {track_index}, y_position={y_position}")

        # Stop any ongoing playback
        self.playback_timer.stop()

        # Use the playhead's current position as the starting point
        start_x = self.playhead.line().x1()
        self.playback_start_time = self.recording_session['start_time']  # Reset playback start time

        # Calculate start_x based on existing containers on this track
        for container in self.containers:
            if container.current_track == track_index:
                container_end_x = container.x() + container.rect().width()
                start_x = max(start_x, container_end_x)
        print(f"Calculated start_x={start_x} for track {track_index}")

        print(f"Creating container at start_x={start_x}, y_position={y_position}")

        self.current_container = DraggableContainer(self.track_height, start_x, 0, 0, self.track_height)
        self.current_container.setRect(0, 0, 50, self.track_height)  # Minimum width
        self.current_container.setPos(start_x, y_position)
        self.current_container.current_track = track_index
        self.current_container.setBrush(QBrush(QColor(173, 216, 230, 100)))
        self.current_container.setPen(QPen(QColor(70, 130, 180, 200), 2))
        self.current_container.setZValue(5)
        self.track_scene.addItem(self.current_container)
        self.containers.append(self.current_container)
        print(f"Container added to scene at track {self.current_container.current_track}, y={self.current_container.y()}, total containers: {len(self.containers)}")
        self.trackView.ensureVisible(self.current_container)
        self.update_timer.start()
        # Do not start playback_timer during recording
        self.update_tracks_and_markers()

    def snap_notes_window(self):
        print("snapping notes lol")
        '''
        Positions (snaps) the notes window to the bottom of the DAW window
        '''
        if not self.notes_window:
            return
        daw_geometry = self.geometry()
        notes_geometry = self.notes_window.geometry()
        x = daw_geometry.x()
        y = daw_geometry.bottom() - notes_geometry.height()
        notes_geometry.moveTo(x, y)
        notes_geometry.setWidth(daw_geometry.width())
        self.notes_window.setGeometry(notes_geometry)
        self.notes_window.raise_()

    def note_started(self, note_name):
        '''
        Adds a new note to recording session with new container and timers
        '''
        print(f"note_started called for note: {note_name}")
        if self.recording and note_name not in self.recording_session['active_notes']:
            start_time = time.time()
            self.recording_session['active_notes'][note_name] = start_time
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            note_x_relative = start_beat * self.base_note_width  # Position based on timing
            y = self.calculate_note_position(note_name)
            print(f"Adding note at relative_x={note_x_relative}, y={y}, container x={self.current_container.x()}")
            note = QGraphicsRectItem(0, 0, 0, self.note_height)
            note.setPos(note_x_relative, y)
            note.setBrush(QBrush(QColor(100, 149, 237)))
            note.setPen(QPen(Qt.GlobalColor.white))
            note.setZValue(6)
            note.setParentItem(self.current_container)
            self.active_note_items[note_name] = note
            self.track_scene.update()

    def note_stopped(self, note_name):
        '''
        Finalizes a note in the recording session, updates the UI, and records the duration
        '''
        if self.recording and note_name in self.recording_session['active_notes']:
            start_time = self.recording_session['active_notes'].pop(note_name)
            stop_time = time.time()
            duration = stop_time - start_time
            self.recording_session['notes'].append({
                'timestamp': start_time - self.recording_session['start_time'],
                'duration': duration,
                'note_name': note_name
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                width = (duration * self.bpm / 60) * self.base_note_width
                note.setRect(0, 0, width, self.note_height)
                self.update_container_size()

    def update_active_notes(self):
        '''
        Updates the note rectangles within the container (solid boxes) during recording
        '''
        if not self.recording or not self.current_container:
            return
        current_time = time.time()
        time_per_beat = 60 / self.bpm
        elapsed_time = current_time - self.recording_session['start_time']
        pixels_per_second = self.base_note_width * self.bpm / 60
        # Update playhead position based on recording progress
        playhead_x = self.current_container.x() + (elapsed_time * pixels_per_second)
        self.playhead.setLine(playhead_x, 0, playhead_x, 5 * self.track_height)
        self.playhead.setVisible(True)
        # Update measure and beat display
        beat_position = playhead_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(playhead_x, 0, 10, self.track_height))

        for note_name, start_time in list(self.recording_session['active_notes'].items()):
            if note_name in self.active_note_items:
                duration = current_time - start_time
                duration_beats = duration / time_per_beat
                width = duration_beats * self.base_note_width
                note = self.active_note_items[note_name]
                note.setRect(0, 0, width, self.note_height)
        self.update_container_size()

    def update_container_size(self):
        '''
        Adjusts the size of note container (semi-transparent box) based on the notes
        '''
        if not self.current_container or not self.recording_session['notes'] and not self.active_note_items:
            return

        # Calculate min and max x-positions of notes (relative to container)
        min_x = 0
        max_x = 0
        time_per_beat = 60 / self.bpm

        # For completed notes
        if self.recording_session['notes']:
            for note in self.recording_session['notes']:
                start_beat = note['timestamp'] * self.bpm / 60
                end_beat = (note['timestamp'] + note['duration']) * self.bpm / 60
                start_x = start_beat * self.base_note_width
                end_x = end_beat * self.base_note_width
                min_x = min(min_x, start_x)
                max_x = max(max_x, end_x)

        # For active notes
        for note_name, start_time in self.recording_session['active_notes'].items():
            current_time = time.time()
            start_beat = (start_time - self.recording_session['start_time']) * self.bpm / 60
            duration_beats = (current_time - start_time) * self.bpm / 60
            start_x = start_beat * self.base_note_width
            end_x = (start_beat + duration_beats) * self.base_note_width
            min_x = min(min_x, start_x)
            max_x = max(max_x, end_x)

        # Adjust container position and size
        if min_x < 0:
            # Shift the container left to include notes with negative x-positions
            current_pos = self.current_container.pos()
            self.current_container.setPos(current_pos.x() + min_x, current_pos.y())
            # Adjust the notes' positions to compensate for the container's shift
            for note in self.current_container.childItems():
                note_pos = note.pos()
                note.setPos(note_pos.x() - min_x, note_pos.y())
            # Update the min_x to 0 since we've shifted the container
            max_x -= min_x  # Adjust max_x to account for the shift
            min_x = 0

        # Set the container's width to encompass all notes
        session_width = max_x - min_x
        self.current_container.setRect(0, 0, max(session_width, 50), self.track_height)  # Ensure minimum width

    def stop_recording(self):
        '''
        Ends recording, finalizes notes, and autosaves
        '''
        if not self.recording:
            return
        self.recording = False
        self.update_timer.stop()
        if self.notes_window:
            self.notes_window.hide()
        current_time = time.time()
        for note_name in list(self.recording_session['active_notes'].keys()):
            start_time = self.recording_session['active_notes'].pop(note_name)
            duration = current_time - start_time
            self.recording_session['notes'].append({
                'timestamp': start_time - self.recording_session['start_time'],
                'duration': duration,
                'note_name': note_name
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                note.setRect(0, 0, (duration * self.bpm / 60) * self.base_note_width, self.note_height)
        self.update_container_size()
        if self.current_container:
            self.current_container.recording_session = self.recording_session
            self.current_container = None
        print("Recording stopped, current_container reset to None")
        self.update_tracks_and_markers()
        self.autosave()

    def note_to_frequency(self, note_name):
        '''
        Converts note names and octave combo into frequency in Hz
        '''
        note = note_name[:-1]
        octave = int(note_name[-1])
        semitone = self.note_order.index(note) + (octave - 4) * 12
        frequency = 261.63 * (2 ** (semitone / 12))
        return round(frequency, 2)

    def autosave(self):
        '''
        Saves all project data into .muse file
        '''
        project_data = {
            "tempo": self.bpm,
            "time_signature": self.time_signature,
            "containers": []
        }
        for container in self.containers:
            notes = container.recording_session['notes'] if hasattr(container,
                                                                    'recording_session') and container.recording_session else []
            project_data["containers"].append({
                "track": container.current_track,
                "start_x": container.x(),
                "notes": notes
            })
        with open(self.autosave_file, 'w') as f:
            json.dump(project_data, f, indent=4)

    def save_project(self, filename):
        '''
        Saves all project data into .muse file
        '''
        self.autosave()
        
        if self.presenter:
            self.presenter.saved_projects_init()

    def load_project(self, filename):
        '''
        Loads project data from .muse file and rebuilds the UI based off that data
        '''
        with open(filename, 'r') as f:
            project_data = json.load(f)

        self.bpm = project_data["tempo"]
        self.time_signature = project_data["time_signature"]
        self.containers.clear()
        self.track_scene.clear()
        self.track_background_group = None  # Reset to None since the group was deleted
        self.update_tracks_and_markers()
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
        self.playhead.setZValue(10)
        self.playhead.setVisible(True)

        for container_data in project_data["containers"]:
            container = DraggableContainer(self.track_height, 0, 0, 0, self.track_height)
            container.setBrush(QBrush(QColor(173, 216, 230, 100)))
            container.setPen(QPen(QColor(70, 130, 180, 200), 2))
            container.setZValue(5)
            container.setPos(container_data["start_x"], container_data["track"] * self.track_height)
            container.current_track = container_data["track"]
            container.recording_session = {"notes": container_data["notes"]}

            max_x = 0
            for note_data in container_data["notes"]:
                start_x = note_data["timestamp"] * self.bpm / 60 * self.base_note_width
                width = note_data["duration"] * self.bpm / 60 * self.base_note_width
                y = self.calculate_note_position(note_data["note_name"])
                note = QGraphicsRectItem(0, 0, width, self.note_height)
                note.setPos(start_x, y)
                note.setBrush(QBrush(QColor(100, 149, 237)))
                note.setPen(QPen(Qt.GlobalColor.white))
                note.setZValue(6)
                note.setParentItem(container)
                max_x = max(max_x, start_x + width)
            container.setRect(0, 0, max(max_x, 50), self.track_height)
            self.track_scene.addItem(container)
            self.containers.append(container)

        self.current_x = max([c.x() + c.rect().width() for c in self.containers], default=0)
        self.update_time_display()

    def calculate_note_position(self, note_name):
        '''
        Calculates y-position for a note on the track - WITHIN the container
        '''
        note = note_name[:-1]
        octave = int(note_name[-1])
        note_index = self.note_order.index(note)
        position = (octave - 3) * 12 + note_index
        total_notes = 24
        y_pos = (1 - position / total_notes) * (self.track_height - self.note_height)
        return y_pos

    def toggle_playback(self):
        '''
        Toggles between play, pause and stop states
        '''
        if self.paused:
            self.paused = False
            self.playback_start_time = time.perf_counter() - (self.paused_position / (self.base_note_width * self.bpm / 60))
            self.playhead.setLine(self.paused_position, 0, self.paused_position, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.start_audio_playback()
            self.note_playback_timer.start()
            self.playback_stream.start()
        elif self.playing:
            self.paused = True
            self.paused_position = self.playhead.line().x1()
            self.playback_timer.stop()
            self.note_playback_timer.stop()
            self.playback_stream.stop()
            self.active_playback_notes.clear()
            self.scheduled_notes.clear()
        else:
            self.playing = True
            self.paused = False
            self.paused_position = None
            # Start playback from the current playhead position
            current_x = self.playhead.line().x1()
            pixels_per_second = self.base_note_width * self.bpm / 60
            elapsed_time = current_x / pixels_per_second
            self.playback_start_time = time.perf_counter() - elapsed_time
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.start_audio_playback()
            self.note_playback_timer.start()
            self.playback_stream.start()
        self.set_button_icons()
        if not self.playing and not self.paused:
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.update_time_display()

    def start_audio_playback(self):
        '''
        Initializes audio playback via note scheduler
        '''
        self.active_playback_notes.clear()
        self.scheduled_notes.clear()
        pixels_per_second = self.base_note_width * self.bpm / 60
        # Calculate the playhead's time offset
        playhead_x = self.playhead.line().x1()
        playhead_time_offset = playhead_x / pixels_per_second
        print(f"Starting playback from playhead at x={playhead_x}, time offset={playhead_time_offset} seconds")
        for container in self.containers:
            if not hasattr(container, 'recording_session') or not container.recording_session['notes']:
                continue
            print(f"Playing container on track {container.current_track}, y={container.y()}")
            container_x_time = container.x() / pixels_per_second
            for note in container.recording_session['notes']:
                adjusted_start_time = note['timestamp'] + container_x_time
                # Adjust the start time relative to the playhead's position
                relative_start_time = adjusted_start_time - playhead_time_offset
                elapsed = time.perf_counter() - self.playback_start_time
                print(f"Note: {note['note_name']}, adjusted_start_time={adjusted_start_time}, relative_start_time={relative_start_time}, elapsed={elapsed}")
                if relative_start_time <= elapsed <= relative_start_time + note['duration']:
                    # Modified: Store the note data in the correct format instead of True
                    data, samplerate = self.sound.notes[note['note_name']]
                    self.mutex.lock()
                    self.active_playback_notes[note['note_name']] = {"data": data, "play_pos": 0, "loop": False}
                    self.mutex.unlock()
                    print(f"Playing note {note['note_name']} immediately")
                elif relative_start_time > elapsed:
                    self.scheduled_notes.append({
                        'name': note['note_name'],
                        'start_time': relative_start_time,
                        'duration': note['duration']
                    })
                    print(f"Scheduled note {note['note_name']} at relative_start_time={relative_start_time}")

    def check_note_playback(self):
        '''
        Checks and triggers the scheduled notes during playback
        '''
        if not self.playing or self.paused:
            return
        current_time = time.perf_counter() - self.playback_start_time
        notes_to_remove = []
        for i, note in enumerate(self.scheduled_notes):
            start_time = note['start_time']
            end_time = start_time + note['duration']
            name = note['name']
            if start_time <= current_time < end_time:
                if name not in self.active_playback_notes:
                    # Modified: Store the note data in the correct format instead of True
                    data, samplerate = self.sound.notes[name]
                    self.mutex.lock()
                    self.active_playback_notes[name] = {"data": data, "play_pos": 0, "loop": False}
                    self.mutex.unlock()
                    self.sound.note_on(name)
            elif current_time >= end_time:
                self.mutex.lock()
                if name in self.active_playback_notes:
                    del self.active_playback_notes[name]
                self.mutex.unlock()
                self.sound.note_off(name)
                notes_to_remove.append(i)

        for i in sorted(notes_to_remove, reverse=True):
            self.scheduled_notes.pop(i)

    def note_on(self, note, loop=False):
        '''
        Plays a note for audio playback
        '''
        self.notes_window.sound.note_on(note)
        if note not in self.active_playback_notes:
            data, samplerate = self.sound.notes[note]
            self.mutex.lock()
            self.active_playback_notes[note] = {"data": data, "play_pos": 0, "loop": loop}
            self.mutex.unlock()

    def note_off(self, note):
        '''
        Stops a note for audio playback
        '''
        self.notes_window.sound.note_off(note)
        self.mutex.lock()
        if note in self.active_playback_notes:
            del self.active_playback_notes[note]
        self.mutex.unlock()

    def playback_audio_callback(self, outdata, frames, time_info, status):
        '''
        Generates audio for active notes
        '''
        self.mutex.lock()
        try:
            if not self.active_playback_notes:
                outdata.fill(0)
                return

            mixed = np.zeros(frames)

            to_remove = []
            for note, note_data in self.active_playback_notes.items():
                data, play_pos, loop = note_data["data"], note_data["play_pos"], note_data["loop"]
                chunk = data[play_pos: play_pos + frames]

                mixed[:len(chunk)] += chunk
                play_pos += frames

                if play_pos >= len(data):
                    if loop:
                        play_pos = 0
                    else:
                        to_remove.append(note)

                self.active_playback_notes[note]["play_pos"] = play_pos

            for note in to_remove:
                del self.active_playback_notes[note]

            mixed = np.clip(mixed, -1, 1)
            outdata[:len(mixed)] = mixed.reshape(-1, 1)
            outdata[len(mixed):] = 0
        finally:
            self.mutex.unlock()

    def get_project_end(self):
        '''
        Calculate the total length of the project in pixels.
        '''
        if not self.containers:
            return 0
        max_end = 0
        pixels_per_second = self.base_note_width * self.bpm / 60
        for container in self.containers:
            if hasattr(container, 'recording_session') and container.recording_session['notes']:
                container_start_time = container.x() / pixels_per_second
                for note in container.recording_session['notes']:
                    end_time = (container_start_time + note['timestamp'] + note['duration']) * pixels_per_second
                    max_end = max(max_end, end_time)
        return max_end

    def update_playhead_continuous(self):
        '''
        Moves playhead and updates time display during playback
        '''
        if self.playback_start_time is None or self.paused:
            return
        elapsed_time = time.perf_counter() - self.playback_start_time
        pixels_per_second = self.base_note_width * self.bpm / 60
        x_position = elapsed_time * pixels_per_second
        project_end = self.get_project_end()
        
        if x_position >= project_end:
            self.stop_playback_internal()
            return
        
        # Update playhead position
        self.playhead.setLine(x_position, 0, x_position, 5 * self.track_height)
        self.playhead.setVisible(True)
        
        # Update measure and beat display
        beat_position = x_position / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        
        # Only scroll if the playhead is near the edge of the visible area
        viewport_rect = self.trackView.viewport().rect()
        playhead_scene_pos = self.trackView.mapFromScene(x_position, 0)
        if playhead_scene_pos.x() > viewport_rect.width() - 50 or playhead_scene_pos.x() < 50:
            self.trackView.ensureVisible(QRectF(x_position, 0, 10, self.track_height))
        
        if self.metronome_on and not self.paused:
            self.align_metronome_to_playhead()

    def stop_playback_internal(self):
        '''
        Completely stops playback and moves playhead to start
        '''
        self.playing = False
        self.paused = False
        self.paused_position = None
        self.playback_timer.stop()
        self.note_playback_timer.stop()
        self.playback_stream.stop()
        self.active_playback_notes.clear()
        self.scheduled_notes.clear()
        self.playhead.setLine(0, 0, 0, 5 * self.track_height)
        self.playhead.setVisible(True)
        self.update_time_display()

    def connect_rewind_button(self):
        '''
        Connects rewind button to its function
        '''
        self.rewind.clicked.connect(self.rewind_one_measure)

    def rewind_one_measure(self):
        '''
        Rewinds playhead one measure (4 beats)
        '''
        if self.playhead is None:
            return
        current_x = self.playhead.line().x1()
        measure_width = 4 * self.base_note_width
        new_x = max(0, current_x - measure_width)
        self.playhead.setLine(new_x, 0, new_x, 5 * self.track_height)
        if self.playing or self.paused:
            pixels_per_second = self.base_note_width * self.bpm / 60
            new_elapsed_time = new_x / pixels_per_second
            self.playback_start_time = time.perf_counter() - new_elapsed_time
            if self.paused:
                self.paused_position = new_x
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))

    def connect_fastforward_button(self):
        '''
        Connects fast forward button to its function
        '''
        self.fastForward.clicked.connect(self.fastforward_one_measure)

    def fastforward_one_measure(self):
        '''
        Fast forwards playhead one measure (4 beats)
        '''
        if self.playhead is None:
            return
        current_x = self.playhead.line().x1()
        measure_width = 4 * self.base_note_width
        new_x = current_x + measure_width
        required_width = new_x + measure_width
        if required_width > self.track_scene.width():
            self.update_tracks_and_markers()
        self.playhead.setLine(new_x, 0, new_x, 5 * self.track_height)
        if self.playing or self.paused:
            pixels_per_second = self.base_note_width * self.bpm / 60
            new_elapsed_time = new_x / pixels_per_second
            self.playback_start_time = time.perf_counter() - new_elapsed_time
            if self.paused:
                self.paused_position = new_x
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))

    def toggle_metronome(self):
        '''
        Toggles metronome on/off
        '''
        if self.metronome_on:
            self.metronome_on = False
            self.metronome_timer.stop()
            self.metronome.setChecked(False)
        else:
            self.metronome_on = True
            self.metronome_timer.start()
            self.metronome.setChecked(True)
            if self.playing or self.paused:
                self.align_metronome_to_playhead()

    def align_metronome_to_playhead(self):
        '''
        Syncs metronome timer to playhead position
        '''
        if self.playhead and (self.playing or self.paused):
            current_x = self.playhead.line().x1()
            beat_position = current_x / self.base_note_width
            time_per_beat = 60 / self.bpm
            offset = (beat_position % 1) * time_per_beat * 1000
            self.metronome_timer.setInterval(int(60000 / self.bpm) - int(offset))

    def metronome_click(self):
        '''
        Handles metronome beat, click sound and updates time
        '''
        print("Click - Beat at BPM:", self.bpm)

        click_sample = np.sin(2 * np.pi * 1000 * np.arange(1000) / 44100) * 0.5
        sd.play(click_sample, samplerate=44100)
        if self.playing or self.paused:
            current_x = self.playhead.line().x1()
            beat_position = current_x / self.base_note_width
            self.current_measure = int(beat_position // 4) + 1
            self.current_beat = int(beat_position % 4) + 1
            self.update_time_display()

    def handle_countoff(self):
        '''
        Handles the 4-beat countoff before recording starts.
        '''
        if self.countoff_beats < 4:
            print(f"Countoff beat {self.countoff_beats + 1} at BPM: {self.bpm}")
            self.metronome_click()  # Reuse the metronome click sound
            self.countoff_beats += 1
        else:
            # Stop the countoff and start recording
            self.countoff_timer.stop()
            self.countoff_active = False
            self.countoff_beats = 0
            print("Countoff finished, starting recording")
            self.start_recording_internal()

    def update_tempo(self):
        '''
        Updates BPM of DAW as well as metronome timer/display
        '''
        text = self.tempo_edit.text()
        try:
            new_bpm = int(text.split()[1])
            if new_bpm <= 0:
                raise ValueError
            self.bpm = new_bpm
            self.update_time_display()
            if self.metronome_on:
                self.metronome_timer.setInterval(int(60000 / self.bpm))
        except ValueError:
            print("Invalid BPM value. Using default 120.")
            self.bpm = 120
            self.tempo_edit.setText(f"Tempo: {self.bpm} BPM")
            if self.metronome_on:
                self.metronome_timer.setInterval(int(60000 / self.bpm))

    def update_time(self):
        '''
        Updates time signature from user input
        '''
        text = self.time_edit.text()
        try:
            if "/" in text.split()[1]:
                new_time_signature = text.split()[1]
                beats, beat_type = map(int, new_time_signature.split("/"))
                if beats > 0 and beat_type > 0:
                    self.time_signature = new_time_signature
                    self.update_time_display()
                    return
            raise ValueError
        except ValueError:
            print("Invalid time signature format. Using default 4/4.")
            self.time_signature = "4/4"
            self.time_edit.setText(f"Time: {self.time_signature}")

    def update_measure(self):
        '''
        Updates measure and beat from user input
        '''
        text = self.measure_edit.text()
        try:
            new_measure = text.split()[1]
            measure, beat = map(int, new_measure.split(":"))
            if measure > 0 and beat > 0 and beat <= 4:
                self.current_measure = measure
                self.current_beat = beat
                self.update_time_display()
                return
            raise ValueError
        except ValueError:
            print("Invalid measure format. Using default 1:1.")
            self.current_measure = 1
            self.current_beat = 1
            self.measure_edit.setText(f"Measure: {self.current_measure}:{self.current_beat}")

    def closeEvent(self, event):
        '''
        Autosaves, cleans and closes the DAW
        '''
        self.autosave()
        self.playback_stream.stop()
        self.note_playback_timer.stop()
        event.accept()
    
    def export_as_mp3(self, output_path=None):
        '''
        Export the current project as an MP3 file using preloaded .aiff piano samples.
        '''
        try:
            if not output_path:
                output_path, _ = QFileDialog.getSaveFileName(
                    self, "Save MP3 File", "", "MP3 Files (*.mp3)"
                )
                if not output_path:
                    QMessageBox.warning(self, "Export Failed", "No output file selected.")
                    return

            total_duration = 0
            pixels_per_second = self.base_note_width * self.bpm / 60
            for container in self.containers:
                if hasattr(container, 'recording_session') and container.recording_session['notes']:
                    container_start_time = container.x() / pixels_per_second
                    for note in container.recording_session['notes']:
                        end_time = container_start_time + note['timestamp'] + note['duration']
                        total_duration = max(total_duration, end_time)
            print(f"Calculated total duration: {total_duration} seconds")

            if total_duration <= 0:
                QMessageBox.warning(self, "Export Failed", "No audio data to export.")
                return

            sample_rate = self.sample_rate
            num_samples = int(total_duration * sample_rate)
            audio_data = np.zeros(num_samples, dtype=np.float32)

            print(f"Initializing audio_data with {num_samples} samples")

            instrument = "Piano"
            if instrument not in self.instruments:
                raise ValueError(f"Instrument {instrument} not found in self.instruments")

            for container in self.containers:
                if hasattr(container, 'recording_session') and container.recording_session['notes']:
                    container_start_time = container.x() / pixels_per_second
                    print(f"Processing container at x={container.x()}, start_time={container_start_time} seconds")
                    for note in container.recording_session['notes']:
                        adjusted_timestamp = container_start_time + note['timestamp']
                        start_sample = int(adjusted_timestamp * sample_rate)
                        duration_samples = int(note['duration'] * sample_rate)
                        note_name = note['note_name']
                        print(f"Processing note: {note_name}, start_sample: {start_sample}, duration_samples: {duration_samples}")

                        if note_name in self.instruments[instrument]:
                            sample_data = self.instruments[instrument][note_name]['data']
                            sample_rate_sample = self.instruments[instrument][note_name]['sample_rate']
                            print(f"Loaded sample for {note_name}, length: {len(sample_data)}, sample_rate: {sample_rate_sample}")

                            if sample_rate_sample != sample_rate:
                                from scipy import signal
                                sample_data = signal.resample(sample_data, int(len(sample_data) * sample_rate / sample_rate_sample))
                                print(f"Resampled {note_name} to {len(sample_data)} samples")

                            if len(sample_data) < duration_samples:
                                num_loops = (duration_samples + len(sample_data) - 1) // len(sample_data)
                                sample_data = np.tile(sample_data, num_loops)[:duration_samples]
                                print(f"Looped {note_name} {num_loops} times to match duration")
                            elif len(sample_data) > duration_samples:
                                sample_data = sample_data[:duration_samples]
                                print(f"Trimmed {note_name} to match duration")

                            samples = sample_data * 0.5
                            end_sample = start_sample + duration_samples
                            if end_sample <= len(audio_data):
                                audio_data[start_sample:end_sample] += samples
                                print(f"Mixed {note_name} into audio_data[{start_sample}:{end_sample}]")
                            else:
                                excess = end_sample - len(audio_data)
                                audio_data[start_sample:] += samples[:-excess]
                                print(f"Trimmed and mixed {note_name} due to length mismatch, excess: {excess}")
                        else:
                            print(f"Warning: Sample for {note_name} not found in {instrument}")

            max_amplitude = np.max(np.abs(audio_data))
            if max_amplitude > 0:
                audio_data = audio_data / max_amplitude
                print(f"Normalized audio, max amplitude: {max_amplitude}")
            else:
                print("Warning: Audio data is silent (max amplitude = 0)")

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
                sf.write(wav_path, audio_data, sample_rate, format='WAV')
                print(f"Saved temporary WAV file: {wav_path}")

            mp3_path = output_path
            ffmpeg_cmd = [
                'ffmpeg', '-i', wav_path, '-c:a', 'libmp3lame', '-q:a', '2',
                '-y', mp3_path
            ]
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(f"FFmpeg output: {result.stdout}")
            print(f"FFmpeg errors (if any): {result.stderr}")

            os.unlink(wav_path)

            QMessageBox.information(self, "Export Successful", f"Exported to: {mp3_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting MP3: {str(e)}")
            print(f"Export error details: {str(e)}")

    def load_instrument_samples(self, instrument_name):
            '''
            Load .aiff samples for the specified instrument into self.instruments.
            '''
            instrument_dir = os.path.join(project_root, "Instruments", instrument_name)
            if not os.path.exists(instrument_dir):
                return
            self.instruments[instrument_name] = {}
            
            for file in os.listdir(instrument_dir):
                if file.endswith('.aiff'):
                    note_name = os.path.splitext(file)[0]
                    file_path = os.path.join(instrument_dir, file)
                    try:
                        data, sample_rate = sf.read(file_path)
                        if data.ndim > 1:
                            data = np.mean(data, axis=1)
                        
                        end_frame = int(2 * sample_rate)
                        max_idx = np.argmax(abs(data))
                        start_frame = 0
                        for x in range(max_idx - 1, -1, -1):
                            if abs(data[x]) < 0.0010:
                                start_frame = x
                                break
                        if end_frame > len(data):
                            end_frame = len(data)
                        snippet = data[start_frame:end_frame]
                        
                        self.instruments[instrument_name][note_name] = {
                            'data': snippet,
                            'sample_rate': sample_rate
                        }
                    except sf.SoundFileError as e:
                        print(f"Error loading {file_path}: {str(e)}")
                    
    def exit_to_main_menu(self):
        '''
        Closes the DAW UI and opens the Main Menu UI by notifying the Presenter.
        '''
        if self.presenter:
            self.presenter.on_exit_to_menu_requested()
        else:
            self.close()
            from .main_menu import Main_Menu
            main_menu = Main_Menu()
            main_menu.show()