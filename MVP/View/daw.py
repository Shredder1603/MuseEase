from PyQt6.QtWidgets import (QMainWindow, QWidget, QLineEdit, QHBoxLayout, QMessageBox, QFileDialog, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsItemGroup, QInputDialog, QPushButton, QVBoxLayout, QFrame, QLabel, QMenu)
from PyQt6.QtGui import QBrush, QPen, QColor, QIcon, QFont, QPainter, QAction, QPixmap
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QRectF, QMutex, QPoint
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
from paths import resource_path
from .equalizerView import EqualizerView
from ..Model.equalizerModel import EqualizerModel 
from MVP.Model.biquadFilter import BiquadFilter
from MVP.Model.ai_eq import apply_eq_from_text
from scipy.signal import butter, lfilter
from MVP.Model.echo import apply_echo
from MVP.Model.reverb import ReverbProcessor
import sys
import traceback

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.daw = None  # Reference to the DAW instance

    def set_daw(self, daw):
        """
        Sets the reference to the DAW instance.
        Allows the scene to interact with DAW properties and methods.
        """
        self.daw = daw

    def mousePressEvent(self, event):
        
        """
        Handles mouse press events in the scene.
        Moves the playhead to the clicked position unless a DraggableContainer is clicked,
        updates playback timing, and ensures the track view follows the playhead.
        """
        # Map the click position to scene coordinates
        pos = event.scenePos()
        x_pos = pos.x()
        y_pos = pos.y()
        print(f"Click at scene coordinates: x={x_pos}, y={y_pos}")
        
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        
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

        ui_path = resource_path("MVP/View/UI/DAW.ui")
        print(f"UI Path: {ui_path}")
        uic.loadUi(ui_path, self)

        self.track_height = 102
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
        self.trackView.setStyleSheet("background-color: transparent; border: none;")
        self.trackView.setInteractive(True)
        self.trackView.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.trackView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.track_scene.selectionChanged.connect(self.update_track_selection_feedback)
        self.trackView.setMinimumHeight(5 * self.track_height + 50)  # Ensure all tracks are visible
        self.trackView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.track_scene.setSceneRect(0, 0, self.trackView.viewport().width(), 5 * self.track_height)


        self.containers = []
        
        self.time_layout = QHBoxLayout(self.timeView)
        self.timeView.setFixedHeight(60)
        self.measure_edit = QLineEdit(f"Measure: {self.current_measure}:{self.current_beat}")
        self.measure_edit.setEnabled(False)
        self.tempo_edit = QLineEdit(f"Tempo: {self.bpm} BPM")
        self.tempo_edit.setEnabled(False)
        self.time_edit = QLineEdit(f"Time: {self.time_signature}")
        self.time_edit.setEnabled(False)
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
        self.timeView.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(80, 80, 80, 200),
                stop:1 rgba(110, 110, 110, 200)
            );
            border: 1px solid rgba(160, 160, 160, 200);
            border-radius: 10px;
        """)

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

        # Initialize SoundGenerator and set up instrument selection
        self.sound = SoundGenerator()
        self.available_instruments = self.sound.available_instruments
        self.track_instruments = ["Piano"] * 5 if "Piano" in self.available_instruments else [self.available_instruments[0]] * 5
        self.setup_instrument_selection()

        self.playback_stream = sd.OutputStream(
            samplerate=self.sound.samplerate,
            channels=1,
            blocksize=1024,
            callback=self.playback_audio_callback
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

        icons_dir = resource_path("MVP/View/Icons")
        print("ICONS: " + icons_dir)
        self.play_icon_path = os.path.join(icons_dir, "Play.png")
        self.pause_icon_path = os.path.join(icons_dir, "Pause.png")
        self.set_button_icons()

        self.autosave_file = resource_path("Saves/autosave.muse")
        self.note_order = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

        self.presenter = presenter
        self.exit_to_menu = self.findChild(QAction, "back")
        self.exit_to_menu.triggered.connect(self.exit_to_main_menu)
        
        # EXPORT FILE HANDLING 
        self.exportMP3 = self.findChild(QAction, "exportMP3")
        self.exportMP3.triggered.connect(self.export_as_mp3)
        
        self.save_project_action = self.findChild(QAction, "actionSave_project")
        self.save_project_action.triggered.connect(self.save_project)
        
        self.instruments = {}
        
                # --- EQ Integration ---
        self.equalizer_model = EqualizerModel()
        self.equalizer_view = EqualizerView()

        self.equalizer_frame = QFrame(self)
        self.equalizer_frame.setLayout(QVBoxLayout())
        self.equalizer_frame.layout().addWidget(self.equalizer_view)
        self.equalizer_frame.setVisible(False)
        self.equalizer_frame.setFixedHeight(350)
        self.equalizer_frame.setStyleSheet("background-color: white; border-top: 2px solid #ccc;")
        
        self.cached_eq_filters = None
        self.reverb_processor = ReverbProcessor()




        self.arrow_button = QPushButton("▲ EQ")
        self.arrow_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(100, 85, 140, 200),
                    stop:1 rgba(130, 115, 170, 200)
                );
                border: 1px solid rgba(0, 0, 0, 230);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
            }

            QPushButton:hover {
                border: 1px solid rgba(160, 140, 210, 255);
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 rgba(110, 95, 150, 220),
                    stop:1 rgba(140, 125, 180, 220)
                );
            }
        """)

        self.arrow_button.clicked.connect(self.toggle_equalizer_view)

        # Inject into container from UI file
        self.eqContainer.layout().addWidget(self.equalizer_frame)
        self.eqContainer.layout().addWidget(self.arrow_button)

        # Signal connections
        self.equalizer_view.gain_changed.connect(self.equalizer_model.set_gain)
        self.equalizer_view.lowpass_freq_changed.connect(self.equalizer_model.set_lowpass_freq)
        self.equalizer_view.highpass_freq_changed.connect(self.equalizer_model.set_highpass_freq)
        self.equalizer_view.reverb_changed.connect(self.equalizer_model.set_reverb)
        self.equalizer_model.gain_updated.connect(self.equalizer_view.set_gain)
        self.equalizer_model.lowpass_freq_updated.connect(self.equalizer_view.set_lowpass_freq)
        self.equalizer_model.highpass_freq_updated.connect(self.equalizer_view.set_highpass_freq)
        self.equalizer_model.reverb_updated.connect(self.equalizer_view.set_reverb)
        
        self.eq_filters = None
        
        bg_image_path = resource_path('MVP/View/UI/DAWbackground.jpg')  
        print(f"Background Image Path: {bg_image_path}")  # Debug print

        self.bg_label = QLabel(self.centralWidget())
        self.bg_label.setScaledContents(True)
        
        # Check if the background image file exists
        if os.path.exists(bg_image_path):
            self.bg_pixmap = QPixmap(bg_image_path)
            self.update_background()
        else:
            print(f"Warning: Background image '{bg_image_path}' not found.")

        # Ensure background is placed behind all widgets
        self.bg_label.lower()
        self.bg_label.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
        
         # Tutorial

        self.tutorial_start = QPushButton("Welcome to the Interactive Tutorial \n\n Click Here to Begin", self)
        self.tutorial_start.setGeometry(600, 100, 140, 40)
        self.tutorial_start.resize(self.tutorial_start.sizeHint())
        self.tutorial_start.hide()
        
        self.tutorial_instument = QPushButton("\n⬅  Start by selecting an instrument\n", self)
        self.tutorial_instument.setGeometry(185, 120, 140, 40)
        self.tutorial_instument.resize(self.tutorial_instument.sizeHint())
        self.tutorial_instument.hide()
        
        self.tutorial_record = QPushButton("⬆\nClick to start recording\n", self)
        self.tutorial_record.setGeometry(330, 90, 140, 40)
        self.tutorial_record.resize(self.tutorial_record.sizeHint())
        self.tutorial_record.hide()
        
        self.tutorial_metronome = QPushButton("⬆\nClick for a metronome\n", self)
        self.tutorial_metronome.setGeometry(490, 90, 140, 40)
        self.tutorial_metronome.resize(self.tutorial_metronome.sizeHint())
        self.tutorial_metronome.hide()
        
        self.tutorial_track = QPushButton("\nDrag track location\n⬇", self)
        self.tutorial_track.setGeometry(700, 100, 140, 40)
        self.tutorial_track.resize(self.tutorial_track.sizeHint())
        self.tutorial_track.hide()
        
        self.tutorial_play = QPushButton("⬆\nClick to play recording\n", self)
        self.tutorial_play.setGeometry(410, 90, 140, 40)
        self.tutorial_play.resize(self.tutorial_play.sizeHint())
        self.tutorial_play.hide()
        
        self.tutorial_time = QPushButton("⬆\nForward/Rewind track\n", self)
        self.tutorial_time.setGeometry(210, 90, 140, 40)
        self.tutorial_time.resize(self.tutorial_time.sizeHint())
        self.tutorial_time.hide()
        
        self.tutorial_end = QPushButton("\n\nEnd Tutorial\n\n", self)
        self.tutorial_end.setGeometry(700, 80, 140, 40)
        self.tutorial_end.resize(self.tutorial_end.sizeHint())
        self.tutorial_end.hide()
        
        
        if (self.presenter.tutorial_mode):
            self.tutorial_start.show()
        
        self.tutorial_start.clicked.connect(self.tutorial_start_next)
        self.tutorial_instument.clicked.connect(self.tutorial_instrument_next)
        self.tutorial_record.clicked.connect(self.tutorial_record_next)
        self.tutorial_metronome.clicked.connect(self.tutorial_metronome_next)
        self.tutorial_track.clicked.connect(self.tutorial_track_next)
        self.tutorial_play.clicked.connect(self.tutorial_play_next)
        self.tutorial_time.clicked.connect(self.tutorial_time_next)
        self.tutorial_end.clicked.connect(self.tutorial_end_next)
            

    def tutorial_start_next(self):
        self.tutorial_start.hide()
        self.tutorial_instument.show()
        
    def tutorial_instrument_next(self):
        self.tutorial_instument.hide()
        self.tutorial_record.show()
        
    def tutorial_record_next(self):
        self.tutorial_record.hide()
        self.tutorial_metronome.show()
        
    def tutorial_metronome_next(self):
        self.tutorial_metronome.hide()
        self.tutorial_track.show()
        
    def tutorial_track_next(self):
        self.tutorial_track.hide()
        self.tutorial_play.show()
        
    def tutorial_play_next(self):
        self.tutorial_play.hide()
        self.tutorial_time.show()
        
    def tutorial_time_next(self):
        self.tutorial_time.hide()
        self.tutorial_end.show()
        
    def tutorial_end_next(self):
        self.tutorial_end.hide()

    def update_background(self):
        """Scale the background image to fit the central widget size."""
        if hasattr(self, 'bg_pixmap'):
            # Use the central widget's size for scaling
            self.bg_label.setGeometry(0, 0, self.centralWidget().width(), self.centralWidget().height())
            scaled_pixmap = self.bg_pixmap.scaled(
                self.centralWidget().width(),
                self.centralWidget().height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding  # Adjust to fill while keeping aspect ratio
            )
            self.bg_label.setPixmap(scaled_pixmap)
            
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
        # Prevent redundant signal firing
        self.track_scene.blockSignals(True)

        if self.track_background_group is not None:
            self.track_scene.removeItem(self.track_background_group)

        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        self.track_background_group.setZValue(1)

        view_width = max(self.trackView.width(), self.current_x + 2000)
        track_brush = QBrush(QColor(45, 45, 45))
        track_pen = QPen(QColor(80, 80, 80))
        self.track_rects = []

        # Create new track rectangles
        for i in range(5):
            track = QGraphicsRectItem(0, i * self.track_height, view_width, self.track_height)
            track.setBrush(track_brush)
            track.setPen(track_pen)
            track.setData(0, i + 1)
            track.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
            track.setAcceptHoverEvents(True)
            self.track_scene.addItem(track)
            self.track_rects.append(track)

        # Draw measure lines and labels
        measure_pen = QPen(QColor(100, 100, 100), 2, Qt.PenStyle.SolidLine)
        beat_tick_pen = QPen(QColor(100, 100, 100), 1, Qt.PenStyle.DotLine)
        measures = int(view_width / self.measure_width) + 2

        for m in range(measures):
            x_pos = m * self.measure_width
            self.track_background_group.addToGroup(
                self.track_scene.addLine(x_pos, 0, x_pos, 5 * self.track_height, measure_pen))
            for b in range(1, 4):
                beat_x = x_pos + b * self.base_note_width
                self.track_background_group.addToGroup(
                    self.track_scene.addLine(beat_x, 0, beat_x, 5 * self.track_height, beat_tick_pen))
            text = self.track_scene.addText(str(m + 1))
            text.setPos(x_pos + 10, 5)
            text.setDefaultTextColor(QColor(150, 150, 150))
            self.track_background_group.addToGroup(text)

        self.track_scene.setSceneRect(0, 0, view_width, 5 * self.track_height)

        # Re-enable signals after the scene is fully rebuilt
        self.track_scene.blockSignals(False)

        # Now update the visual feedback for the selected track
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
        self.update_background()
        
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
        
        self.cached_eq_filters = None
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
            'notes': [],
            'instrument': self.track_instruments[self.selected_track_index]  # Store the selected instrument
        }
        if self.notes_window is None:
            self.notes_window = NotesWindow(sound_generator=self.sound, current_instrument=self.track_instruments[self.selected_track_index])
            self.notes_window.note_started.connect(self.note_started)
            self.notes_window.note_stopped.connect(self.note_stopped)
            self.notes_window.finished.connect(self.stop_recording)
        else:
            self.notes_window.set_current_instrument(self.track_instruments[self.selected_track_index])
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

        self.current_container = DraggableContainer(self.track_height, (int(self.track_scene.width()), int(self.track_scene.height())), start_x, 0, 0, self.track_height)
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
                "notes": notes,
                "instrument": container.recording_session.get('instrument', "Piano")  # Save the instrument
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

    def load_project(self, filename, muse_file):
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
            container = DraggableContainer(self.track_height, (int(self.track_scene.width()), int(self.track_scene.height())), 0, 0, 0, self.track_height)
            container.setBrush(QBrush(QColor(173, 216, 230, 100)))
            container.setPen(QPen(QColor(70, 130, 180, 200), 2))
            container.setZValue(5)
            container.setPos(container_data["start_x"], container_data["track"] * self.track_height)
            container.current_track = container_data["track"]
            container.recording_session = {
                "notes": container_data["notes"],
                "instrument": container_data["instrument"]  # Load the instrument
            }

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
        self.autosave_file = "./Saves/" + muse_file + ".muse"




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
            self.cached_eq_filters = None
            self.start_audio_playback()
            self.note_playback_timer.start()
            self.playback_stream.start()
        elif self.playing:
            self.paused = True
            self.paused_position = self.playhead.line().x1()
            self.playback_timer.stop()
            self.note_playback_timer.stop()
            try:
                self.playback_stream.stop()
            except Exception as e:
                print(f"Error stopping playback stream: {e}")
            self.active_playback_notes.clear()
            self.scheduled_notes.clear()
        else:
            self.playing = True
            self.paused = False
            self.paused_position = None
            current_x = self.playhead.line().x1()
            pixels_per_second = self.base_note_width * self.bpm / 60
            elapsed_time = current_x / pixels_per_second
            self.playback_start_time = time.perf_counter() - elapsed_time
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.cached_eq_filters = None
            self.start_audio_playback()
            self.playback_stream.stop()  # Reset stream
            self.playback_stream.start()  # Restart to apply EQ
            self.note_playback_timer.start()
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
            instrument = container.recording_session.get('instrument', "Piano")
            for note in container.recording_session['notes']:
                adjusted_start_time = note['timestamp'] + container_x_time
                # Adjust the start time relative to the playhead's position
                relative_start_time = adjusted_start_time - playhead_time_offset
                elapsed = time.perf_counter() - self.playback_start_time
                print(f"Note: {note['note_name']}, adjusted_start_time={adjusted_start_time}, relative_start_time={relative_start_time}, elapsed={elapsed}")
                if relative_start_time <= elapsed <= relative_start_time + note['duration']:
                    # Use the instrument from the container
                    if note['note_name'] in self.sound.instruments[instrument]:
                        data, samplerate = self.sound.instruments[instrument][note['note_name']]
                        self.mutex.lock()
                        self.active_playback_notes[note['note_name']] = {"data": data, "play_pos": 0, "loop": False}
                        self.mutex.unlock()
                        print(f"Playing note {note['note_name']} immediately with instrument {instrument}")
                elif relative_start_time > elapsed:
                    self.scheduled_notes.append({
                        'name': note['note_name'],
                        'start_time': relative_start_time,
                        'duration': note['duration'],
                        'instrument': instrument
                    })
                    print(f"Scheduled note {note['note_name']} at relative_start_time={relative_start_time}")

    def check_note_playback(self):
        """
        Checks and updates the playback of scheduled notes.
        Activates or removes notes based on the current playback time, applying equalizer settings.
        """
        if not self.playing or self.paused:
            return
        current_time = time.perf_counter() - self.playback_start_time
        notes_to_remove = []

        for i, note in enumerate(self.scheduled_notes):
            start_time = note['start_time']
            end_time = start_time + note['duration']
            name = note['name']
            instrument = note['instrument']

            if start_time <= current_time < end_time:
                if name not in self.active_playback_notes:
                    if name in self.sound.instruments[instrument]:
                        data, samplerate = self.sound.instruments[instrument][name]

                        self.mutex.lock()
                        self.active_playback_notes[name] = {
                            "data": data,
                            "play_pos": 0,
                            "loop": False
                        }
                        self.mutex.unlock()

                        print(f"Activated {name} at {current_time}")
                        for band in self.equalizer_model.bands:
                            band_settings = self.equalizer_model.settings[band]
                            gain = band_settings["gain"]
                            low = band_settings["highpass_freq"]
                            high = band_settings["lowpass_freq"]
                            print(f"[EQ DEBUG] {band}: Gain={gain} dB | HP={low} Hz | LP={high} Hz")
                            if low < high and abs(gain) > 0.1:
                                print(f"[EQ APPLY] Applying bandpass filter: {low}-{high} Hz with gain {gain} dB")
                            elif low >= high:
                                print(f"[EQ SKIP] Invalid filter: highpass ({low}) >= lowpass ({high})")

            elif current_time >= end_time:
                self.mutex.lock()
                if name in self.active_playback_notes:
                    del self.active_playback_notes[name]
                self.mutex.unlock()
                self.sound.note_off(name, instrument=instrument)
                notes_to_remove.append(i)
                print(f"Removed {name} at {current_time}")

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
            #self.active_playback_notes[note] = {"data": data, "play_pos": 0, "loop": loop}
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

    def toggle_equalizer_view(self):
        """
        Toggles the visibility of the equalizer view.
        Updates the arrow button text to reflect the current state (open or closed).
        """
        is_open = self.equalizer_frame.isVisible()
        self.equalizer_frame.setVisible(not is_open)
        self.arrow_button.setText("▼ EQ" if is_open else "▲ EQ")
    
    def apply_eq_filter(self, data, samplerate):
        """
        Applies equalizer filters to audio data for a given sample rate.
        Processes each band (low, mid, high) with appropriate filter types and settings.
        """
        output = np.zeros_like(data)

        for band in self.equalizer_model.bands:
            gain_db = self.equalizer_model.settings[band]["gain"]
            if abs(gain_db) < 0.1:
                continue

            hp = self.equalizer_model.settings[band]["highpass_freq"]
            lp = self.equalizer_model.settings[band]["lowpass_freq"]
            center_freq = (hp + lp) / 2
            bandwidth = lp - hp

            if bandwidth < 50 or hp >= lp:
                print(f"[EQ SKIP] Invalid {band} band: HP={hp}, LP={lp}")
                continue

            # Use peak filter for mid, and shelves for low/high
            if band.startswith("Mid"):
                biquad = BiquadFilter.create_mid_shelf(samplerate, center_freq, gain_db, Q=bandwidth/center_freq)
            elif band.startswith("Low"):
                biquad = BiquadFilter.create_low_shelf(samplerate, center_freq, gain_db, Q=0.707)
            elif band.startswith("High"):
                biquad = BiquadFilter.create_high_shelf(samplerate, center_freq, gain_db, Q=0.707)
            else:
                continue

            band_processed = np.array([biquad.process(x) for x in data])
            output += band_processed

        return output

    
    def apply_equalizer(self, chunk, sample_rate):
        """
        Applies the equalizer filters to an audio chunk.
        Processes the chunk through all configured filters and returns the filtered result.
        """
        if self.cached_eq_filters is None:
            self.cached_eq_filters = self.equalizer_model.get_filters(sample_rate)

        filters = self.cached_eq_filters
        filtered = np.zeros_like(chunk)

        for i in range(len(chunk)):
            x = chunk[i]
            if abs(x) < 1e-20:
                x = 0.0

            for f_idx, f in enumerate(filters):
                x = f.process(x)

            filtered[i] = x
        
        reverb_percent = max(self.equalizer_model.settings[b]["reverb"] for b in self.equalizer_model.bands)
        if reverb_percent > 0:
            self.reverb_processor.wet_level = reverb_percent / 100.0
            filtered = self.reverb_processor.process(filtered)

        return filtered


    
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
                data, play_pos, loop = note_data["data"], note_data["play_pos"], note_data.get("loop", False)

                if play_pos >= len(data):
                    if loop:
                        play_pos = 0
                    else:
                        to_remove.append(note)
                        continue

                chunk = data[play_pos: play_pos + frames]
                if len(chunk) < frames:
                    chunk = np.pad(chunk, (0, frames - len(chunk)), mode='constant')

                fade_len = min(32, len(chunk))
                fade_in = np.linspace(0.0, 1.0, fade_len)
                fade_out = np.linspace(1.0, 0.0, fade_len)
                if play_pos == 0:
                    chunk[:fade_len] *= fade_in
                if play_pos + frames >= len(data):
                    chunk[-fade_len:] *= fade_out

                #print(f"[DEBUG] Raw chunk max before EQ: {np.max(np.abs(chunk)):.6f}")
                chunk = self.apply_equalizer(chunk, self.sample_rate)
                #print(f"[DEBUG] Chunk max after EQ: {np.max(np.abs(chunk)):.6f}")
                
                mixed[:len(chunk)] += chunk
                self.active_playback_notes[note]["play_pos"] = play_pos + frames

            for note in to_remove:
                del self.active_playback_notes[note]

            if np.any(np.isnan(mixed)):
                mixed = np.nan_to_num(mixed)

            max_val = np.max(np.abs(mixed))
            if max_val > 1.0:
                mixed = mixed / max_val
            #print(f"[DEBUG] Final max amplitude: {np.max(np.abs(mixed)):.6f}, dtype: {mixed.dtype}, shape: {mixed.shape}")

            outdata[:] = mixed.reshape(-1, 1)

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
        try:
            self.playback_stream.stop()
        except Exception as e:
            print(f"Error stopping playback stream in stop_playback_internal: {e}")
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
        self.countoff_beats += 1
        print(f"Countoff beat {self.countoff_beats} at BPM: {self.bpm}")
        click_sample = np.sin(2 * np.pi * 1000 * np.arange(1000) / 44100) * 0.5
        sd.play(click_sample, samplerate=44100)
        
        if self.countoff_beats >= 4:
            self.countoff_timer.stop()
            self.countoff_active = False
            print("Countoff finished, starting recording")
            self.start_recording_internal()

    def update_measure(self):
        '''
        Updates measure and beat based on user input
        '''
        text = self.measure_edit.text()
        try:
            measure, beat = map(int, text.replace("Measure: ", "").split(":"))
            if measure < 1 or beat < 1 or beat > 4:
                raise ValueError("Invalid measure or beat")
            self.current_measure = measure
            self.current_beat = beat
            new_x = ((measure - 1) * 4 + (beat - 1)) * self.base_note_width
            self.playhead.setLine(new_x, 0, new_x, 5 * self.track_height)
            if self.playing or self.paused:
                pixels_per_second = self.base_note_width * self.bpm / 60
                new_elapsed_time = new_x / pixels_per_second
                self.playback_start_time = time.perf_counter() - new_elapsed_time
                if self.paused:
                    self.paused_position = new_x
            self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter measure and beat in the format 'Measure: M:B' (e.g., 'Measure: 1:1')")
            self.update_time_display()

    def update_tempo(self):
        '''
        Updates tempo based on user input
        '''
        text = self.tempo_edit.text()
        try:
            bpm = int(text.replace("Tempo: ", "").replace(" BPM", ""))
            if bpm < 1:
                raise ValueError("Tempo must be positive")
            self.bpm = bpm
            self.metronome_timer.setInterval(int(60000 / self.bpm))
            self.countoff_timer.setInterval(int(60000 / self.bpm))
            if self.playing or self.paused:
                current_x = self.playhead.line().x1()
                pixels_per_second = self.base_note_width * self.bpm / 60
                elapsed_time = current_x / pixels_per_second
                self.playback_start_time = time.perf_counter() - elapsed_time
                if self.paused:
                    self.paused_position = current_x
            self.update_time_display()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid tempo (e.g., 'Tempo: 120 BPM')")
            self.update_time_display()

    def update_time(self):
        '''
        Updates time signature based on user input
        '''
        text = self.time_edit.text()
        try:
            time_sig = text.replace("Time: ", "")
            if time_sig not in ["4/4", "3/4", "6/8"]:
                raise ValueError("Unsupported time signature")
            self.time_signature = time_sig
            self.update_time_display()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid time signature (e.g., 'Time: 4/4')")
            self.update_time_display()

    def setup_instrument_selection(self):
        '''
        Sets up the QComboBox widgets for instrument selection for each track.
        '''
        self.instrument_boxes = [
            self.instrument1,
            self.instrument2,
            self.instrument3,
            self.instrument4,
            self.instrument5
        ]

        for i, combo_box in enumerate(self.instrument_boxes):
            combo_box.addItems(self.available_instruments)
            combo_box.setCurrentText(self.track_instruments[i])
            # Connect the signal to update the instrument for the track
            combo_box.currentTextChanged.connect(lambda text, idx=i: self.update_track_instrument(idx, text))

    def update_track_instrument(self, track_index, instrument):
        '''
        Updates the instrument for the specified track and updates the UI.
        '''
        self.track_instruments[track_index] = instrument
        print(f"Track {track_index + 1} instrument updated to {instrument}")
        # If recording on this track, update the NotesWindow's instrument
        if self.recording and self.selected_track_index == track_index and self.notes_window:
            self.notes_window.set_current_instrument(instrument)

    def export_as_mp3(self):
        '''
        Exports the project as an MP3 file using ffmpeg.
        '''
        # Step 1: Collect all audio data
        pixels_per_second = self.base_note_width * self.bpm / 60
        total_duration = self.get_project_end() / pixels_per_second  # in seconds
        total_samples = int(total_duration * self.sample_rate)
        mixed_audio = np.zeros(total_samples)

        for container in self.containers:
            if not hasattr(container, 'recording_session') or not container.recording_session['notes']:
                continue
            container_start_time = container.x() / pixels_per_second
            instrument = container.recording_session.get('instrument', "Piano")
            for note in container.recording_session['notes']:
                note_start_time = container_start_time + note['timestamp']
                note_duration = note['duration']
                note_name = note['note_name']
                if note_name in self.sound.instruments[instrument]:
                    data, samplerate = self.sound.instruments[instrument][note_name]
                    if samplerate != self.sample_rate:
                        # Resample the audio data to match the DAW's sample rate
                        data = scipy.signal.resample(data, int(len(data) * self.sample_rate / samplerate))
                    start_sample = int(note_start_time * self.sample_rate)
                    end_sample = start_sample + len(data)
                    if end_sample > len(mixed_audio):
                        # Extend the mixed_audio array if necessary
                        mixed_audio = np.pad(mixed_audio, (0, end_sample - len(mixed_audio)), mode='constant')
                    # Mix the note into the audio
                    mixed_audio[start_sample:end_sample] += data[:end_sample - start_sample]

        # Step 2: Normalize and clip the audio
        mixed_audio = np.clip(mixed_audio, -1, 1)

        # Step 3: Save as WAV temporarily
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_wav.name, mixed_audio, self.sample_rate)

        # Step 4: Convert to MP3 using ffmpeg
        output_file, _ = QFileDialog.getSaveFileName(self, "Export MP3", "", "MP3 Files (*.mp3)")
        if output_file:
            if not output_file.endswith('.mp3'):
                output_file += '.mp3'
            try:
                subprocess.run(['ffmpeg', '-y', '-i', temp_wav.name, output_file], check=True)
                QMessageBox.information(self, "Export Successful", f"Project exported as {output_file}")
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export MP3: {str(e)}")
            finally:
                temp_wav.close()
                os.remove(temp_wav.name)
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)

        ai_eq_action = QAction("AI EQ", self)
        menu.addAction(ai_eq_action)

        def launch_textbox():
            self.eq_textbox = QLineEdit(self)
            self.eq_textbox.setPlaceholderText("Describe the sound (e.g. 'make it bassy')")
            self.eq_textbox.setGeometry(event.globalPos().x(), event.globalPos().y(), 300, 30)
            self.eq_textbox.setStyleSheet("""
                background-color: #1c1c1c;
                color: white;
                padding: 6px;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            """)
            self.eq_textbox.returnPressed.connect(lambda: self.handle_ai_eq(self.eq_textbox.text(), self.eq_textbox))
            self.eq_textbox.show()
            self.eq_textbox.setFocus()

        ai_eq_action.triggered.connect(launch_textbox)
        menu.exec(event.globalPos())

    def handle_ai_eq(self, text, textbox):
        apply_eq_from_text(self.equalizer_model, text)
        self.eq_textbox.deleteLater()

    def save_project(self):
        '''
        Saves project to chosen file name to Saves directory
        '''
        saved_path = resource_path("Saves")
        saved_files = os.listdir(saved_path)
        text, okPressed = QInputDialog.getText(self, "Save Project", "Project Name:")
        if okPressed:
            new_file = text + ".muse"
            if new_file in saved_files:
                over_write = QMessageBox.question(self, "Save Project", "Overwrite Existing Project",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if over_write == QMessageBox.StandardButton.Yes:
                    self.autosave_file = "./Saves/" + new_file
                    self.autosave()
            else:
                self.autosave_file = "./Saves/" + new_file
                self.autosave()

    def exit_to_main_menu(self):
        '''
        Exits to the main menu, autosaving the project.
        '''
        self.autosave()
        self.close()
        if self.presenter:
            self.presenter.show_main_menu()

    def closeEvent(self, event):
        '''
        Handles window close event, ensuring proper cleanup.
        '''
        self.autosave()
        if self.notes_window:
            self.notes_window.close()
        try:
            self.playback_stream.stop()
            self.playback_stream.close()
        except Exception as e:
            print(f"Error closing playback stream: {str(e)}")
            traceback.print_exc()
        event.accept()