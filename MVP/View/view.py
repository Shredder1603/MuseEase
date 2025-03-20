from PyQt6.QtWidgets import (QWidget, QLabel, QDialog, QApplication, QListView, QMessageBox, QMainWindow, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsItemGroup, QLineEdit, QHBoxLayout, QPushButton)
from PyQt6.QtGui import QPixmap, QBrush, QPen, QColor, QCursor, QPainter, QFont, QIcon, QAction
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel, Qt, QTimer, QRectF, QPointF
from MVP.View.Notes import NotesWindow, SoundGenerator
import sounddevice as sd
import time
import soundfile as sf
import json
import scipy
import subprocess
import tempfile
import numpy as np
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class Main_Menu(QMainWindow, QWidget):
    def __init__(self):
        super().__init__()

        # Load the Main Menu UI
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/MainMenu.ui')
        uic.loadUi(ui_path, self)

        # Initialize the background label
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        # Set up button functionality #
        # ---------------------------------------------------------------------- #
        self.exit_button = getattr(self, "exit_button")
        self.exit_button.clicked.connect(self.on_exit_requested)
        self.exit_requested_callback = None

        self.open_file_button = getattr(self, "open_file_button")
        self.open_file_button.clicked.connect(self.on_open_saved_projects_requested)
        self.open_saved_projects_callback = None

        self.new_project_button = getattr(self, "new_project_button")
        self.new_project_button.clicked.connect(self.on_new_project_requested)
        self.new_project_callback = None
        # ---------------------------------------------------------------------- #

        # Track the Saved Projects UI window
        self.saved_projects_window = None  

        self.setWindowTitle("MuseEase")

        # Set the window to fullscreen
        self.showFullScreen()  # This makes the window fullscreen upon opening

        # Background setup
        bg_image_path = os.path.join(os.path.dirname(ui_path), 'background.jpg')

        # Check if the background image file exists
        if os.path.exists(bg_image_path):
            self.bg_pixmap = QPixmap(bg_image_path)
            self.update_background()
        else:
            print(f"Error: Background image '{bg_image_path}' not found.")

        # Ensure background is placed behind all widgets
        self.bg_label.lower()

    def resizeEvent(self, event):
        """Resize the background dynamically when the window is resized."""
        if hasattr(self, 'bg_pixmap'):  # Check if bg_pixmap is initialized
            self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        """Scale the background image to fit the window size."""
        if hasattr(self, 'bg_pixmap'):  # Ensure bg_pixmap is available before using it
            self.bg_label.setGeometry(0, 0, self.width(), self.height())  
            scaled_pixmap = self.bg_pixmap.scaled(self.width(), self.height())
            self.bg_label.setPixmap(scaled_pixmap)

    def set_exit_callback(self, callback):
        self.exit_requested_callback = callback

    def on_exit_requested(self):
        if self.exit_requested_callback:
            self.exit_requested_callback()

    def execute_exit(self):
        QApplication.quit()

    def set_open_saved_projects_callback(self, callback):
        self.open_saved_projects_callback = callback

    def on_open_saved_projects_requested(self):
        if self.open_saved_projects_callback:
            self.open_saved_projects_callback()

    def set_new_project_callback(self, callback):
        self.new_project_callback = callback

    def on_new_project_requested(self):
        if self.new_project_callback:
            self.new_project_callback()

class Tutorial(QDialog, QWidget):
    def __init__(self, presenter=None):
        super().__init__()
        
        # Store a reference to the presenter
        self.presenter = presenter
        
        # Load the UI from the .ui file
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/Tutorial.ui')
        uic.loadUi(ui_path, self)
        
        forward_path = forward_png = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/FastForward.png')
        forward_png = QPixmap(forward_path)
        self.forward.setPixmap(forward_png)
        
        rewind_path = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/Rewind.png')
        rewind_png = QPixmap(rewind_path)
        self.rewind.setPixmap(rewind_png)
        
        record_path = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/Record.png')
        record_png = QPixmap(record_path)
        self.record.setPixmap(record_png)
        
        play_path = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/Play.png')
        play_png = QPixmap(play_path)
        self.play.setPixmap(play_png)
        
        metro_path = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/Metronome.png')
        metro_png = QPixmap(metro_path)
        self.metro.setPixmap(metro_png)
        
        drag_path = os.path.join(os.path.dirname(__file__), 'Icons/Tutorial_Icons/Drag_drop.png')
        drag_png = QPixmap(drag_path)
        self.Drag.setPixmap(drag_png)

        # Find buttons and labels in the UI
        self.close_button = self.findChild(QPushButton, 'back')

        # Connect the buttons to their respective methods
        self.close_button.clicked.connect(self.close_tutorial)

    def close_tutorial(self):
        """Close the tutorial window and notify the presenter."""
        if self.presenter:
            self.presenter.on_tutorial_closed()
        self.close()  # Close the dialog window

class Saved_Projects(QDialog, QWidget):
    def __init__(self, presenter=None):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'UI/SavedProjects.ui')
        uic.loadUi(ui_path, self)

        self.presenter = presenter
        self.openProjectButton = getattr(self, "openProjectButton")
        self.openProjectButton.clicked.connect(self.open_selected_project)

        self.deleteProjectButton = getattr(self, "deleteProjectButton")
        self.deleteProjectButton.clicked.connect(self.delete_selected_project)

        self.backButton = getattr(self, "backButton")
        self.backButton.clicked.connect(self.on_back_button_clicked)  # Connect back button

        self.savedProjectsListView = getattr(self, "savedProjectsListView")
        self.savedProjectsListView.setEditTriggers(QListView.EditTrigger.NoEditTriggers)

    def on_back_button_clicked(self):
        """Handles the back button click event to return to the main menu."""
        if self.presenter:
            self.presenter.on_exit_to_menu_requested()

    def populate_saved_projects(self, files):
        """Populates the saved projects list."""
        model = QStringListModel()
        model.setStringList(files)
        self.savedProjectsListView.setModel(model)

    def open_selected_project(self):
        """Opens the selected project."""
        selected_indexes = self.savedProjectsListView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Open Project", "No project selected.")
            return
        
        selected_file = selected_indexes[0].data()
        project_path = os.path.join(project_root, "Saves", f"{selected_file}.muse")  # Full path to .muse file
        QMessageBox.information(self, "Open Project", f"Opening project: {selected_file}")
        
        if self.presenter:
            self.presenter.stacked_widget.removeWidget(self.presenter.saved_projects)
            self.presenter.saved_projects = None  # Prevent reopening

        # Force the UI to switch to Main Menu before loading the project
        self.presenter.stacked_widget.setCurrentWidget(self.presenter.main_menu)

        # Open New_Project as usual
        daw = New_Project(self.presenter)
        self.presenter.new_project = daw
        self.presenter.stacked_widget.addWidget(daw)
        self.presenter.stacked_widget.setCurrentWidget(daw)
        daw.load_project(project_path)

    def delete_selected_project(self):
        """Deletes the selected project."""
        selected_indexes = self.savedProjectsListView.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Delete Project", "No project selected.")
            return
        
        selected_file = str(selected_indexes[0].data()) + ".muse"
        folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Saves")
        file_path = os.path.join(folder_path, selected_file)

        confirm = QMessageBox.question(self, "Delete Project", f"Are you sure you want to delete {selected_file}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            os.remove(file_path)
            QMessageBox.information(self, "Delete Project", f"Deleted: {selected_file}")
            self.populate_saved_projects([os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.muse')])
    

class New_Project(QMainWindow, QWidget):
    from PyQt6.QtCore import QMutex
    mutex = QMutex()
    def __init__(self, presenter=None):
        super().__init__()

        ui_path = os.path.join(os.path.dirname(__file__), "UI/DAW.ui")
        uic.loadUi(ui_path, self)

        self.track_height = 80  # View
        self.base_note_width = 100  # View
        self.note_height = 20  # View
        self.current_x = 0  # Presenter
        self.measure_width = 400  # View
        self.bpm = 120  # Model
        self.time_signature = "4/4"  # Model
        self.current_measure = 1  # Presenter
        self.current_beat = 1  # Presenter

        self.track_scene = QGraphicsScene()  # View
        self.trackView.setScene(self.track_scene)  # View
        self.trackView.setInteractive(True)
        self.trackView.setRenderHint(QPainter.RenderHint.Antialiasing, True)  # View
        self.trackView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)  # View
        self.track_scene.selectionChanged.connect(self.update_track_selection_feedback)  # View

        self.containers = []  # Model
        
        self.time_layout = QHBoxLayout(self.timeView)  # View
        self.timeView.setFixedHeight(60)  # View
        self.measure_edit = QLineEdit(f"Measure: {self.current_measure}:{self.current_beat}")  # View
        self.tempo_edit = QLineEdit(f"Tempo: {self.bpm} BPM")  # View
        self.time_edit = QLineEdit(f"Time: {self.time_signature}")  # View
        self.time_layout.addWidget(self.measure_edit)  # View
        self.time_layout.addSpacing(20)  # View
        self.time_layout.addWidget(self.tempo_edit)  # View
        self.time_layout.addSpacing(20)  # View
        self.time_layout.addWidget(self.time_edit)  # View

        font = QFont("Arial", 12)  # View
        self.measure_edit.setFont(font)  # View
        self.tempo_edit.setFont(font)  # View
        self.time_edit.setFont(font)  # View
        self.measure_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")  # View
        self.tempo_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")  # View
        self.time_edit.setStyleSheet(
            "QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")  # View
        self.timeView.setStyleSheet("background-color: #333333; border: 1px solid #555555;")  # View

        self.measure_edit.editingFinished.connect(self.update_measure)  # View
        self.tempo_edit.editingFinished.connect(self.update_tempo)  # View
        self.time_edit.editingFinished.connect(self.update_time)  # View

        self.track_background_group = QGraphicsItemGroup()  # View
        self.track_scene.addItem(self.track_background_group)  # View
        self.update_tracks_and_markers()  # View
        self.update_time_display()  # View

        self.recording = False  # Presenter
        self.recording_session = None  # Model
        self.playing = False  # Presenter
        self.paused = False  # Presenter
        self.playback_timer = QTimer()  # Presenter
        self.playback_timer.setInterval(10)  # Presenter
        self.playback_timer.timeout.connect(self.update_playhead_continuous)  # Presenter
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))  # View
        self.playhead.setZValue(10)  # View
        self.playhead.setVisible(True)  # View
        self.playback_start_time = None  # Presenter
        self.paused_position = None  # Presenter
        self.current_container = None  # Presenter
        self.active_note_items = {}  # View

        self.sample_rate = 44100  # Model
        self.active_playback_notes = {}  # Model
        self.phase = {}  # Model
        self.notes_window = NotesWindow()  # View
        self.sound = self.notes_window.sound
        self.playback_stream = sd.OutputStream(
            samplerate=self.sound.notes["A0"][1],
            channels=1,
            callback=self.playback_audio_callback,
        )  # Model

        self.note_playback_timer = QTimer()  # Presenter
        self.note_playback_timer.setInterval(10)  # Presenter
        self.note_playback_timer.timeout.connect(self.check_note_playback)  # Presenter
        self.scheduled_notes = []  # Model

        self.record.clicked.connect(self.toggle_recording)  # View
        self.play.clicked.connect(self.toggle_playback)  # View
        self.connect_rewind_button()  # View
        self.connect_fastforward_button()  # Presenter

        self.metronome_on = False  # Presenter
        self.metronome_timer = QTimer()  # Presenter
        self.metronome_timer.setInterval(int(60000 / self.bpm))  # Presenter
        self.metronome_timer.timeout.connect(self.metronome_click)  # Presenter
        self.metronome.clicked.connect(self.toggle_metronome)  # View

        self.update_timer = QTimer()  # Presenter
        self.update_timer.setInterval(50)  # Presenter
        self.update_timer.timeout.connect(self.update_active_notes)  # Presenter

        icons_dir = os.path.join(os.path.dirname(__file__), "Icons")  # View
        self.play_icon_path = os.path.join(icons_dir, "Play.png")  # View
        self.pause_icon_path = os.path.join(icons_dir, "Pause.png")  # View
        self.set_button_icons()

        self.autosave_file = "./Saves/autosave.muse"  # Model
        self.note_order = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']  # Model

        self.presenter = presenter
        self.exit_to_menu = self.findChild(QAction, "back")
        self.exit_to_menu.triggered.connect(self.exit_to_main_menu)
        
        # EXPORT FILE HANDLING 
        self.exportMP3 = self.findChild(QAction, "exportMP3")
        self.exportMP3.triggered.connect(self.export_as_mp3)
        
        self.instruments = {}  # Initialize instruments dictionary
        self.load_instrument_samples("Piano")  # Load piano samples
        
    def keyPressEvent(self, event):
        """Handle key presses, including Delete to remove selected track."""
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.track_scene.selectedItems()
            if selected_items:
                self.delete_selected_container(selected_items[0])  # Delete the first selected item
        super().keyPressEvent(event) 
    
    def delete_selected_container(self, container):
        """Remove the specified container from the scene and containers list."""
        if container in self.containers:
            self.track_scene.removeItem(container)
            self.containers.remove(container)
            self.autosave()  # Save after deletion
            self.update_tracks_and_markers()   
    
    def mousePressEvent(self, event):
        '''
        Update selected container when clicking on one.
        '''
        item = self.trackView.itemAt(event.pos())
        if isinstance(item, self.DraggableContainer):
            self.selected_container = item
            # Optional: Highlight the selected container
            item.setPen(QPen(QColor(255, 0, 0), 2))  # Red border for selection
            for container in self.containers:
                if container != item:
                    container.setPen(QPen(QColor(70, 130, 180, 200), 2))  # Reset others
        super().mousePressEvent(event)
        
    def update_container_selection_feedback(self):
        """Update visual feedback for selected containers."""
        for container in self.containers:
            if container.isSelected():
                container.setPen(QPen(QColor(255, 0, 0), 2))  # Red border 
            else:
                container.setPen(QPen(QColor(70, 130, 180, 200), 2))  # Default border  
                        
    def set_button_icons(self):
        '''
        Updates play/pause button icon based on state (View)
        '''
        if self.playing and not self.paused:
            icon = QIcon(self.pause_icon_path)
        else:
            icon = QIcon(self.play_icon_path)
        self.play.setIcon(icon)

    def update_track_selection_feedback(self):
        for track in self.track_rects:
            if track.isSelected():
                track.setBrush(QBrush(QColor(255, 45, 45, 100)))  # Red tint for selected track
                track.setPen(QPen(QColor(255, 0, 0), 2))
            else:
                track.setBrush(QBrush(QColor(45, 45, 45)))  # Default gray
                track.setPen(QPen(QColor(80, 80, 80)))
                
    def update_tracks_and_markers(self):
        '''
        Redraws track backgrounds, measure lines, and labels (View)
        '''
        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        view_width = max(self.trackView.width(), self.current_x + 2000)
        track_brush = QBrush(QColor(45, 45, 45))
        track_pen = QPen(QColor(80, 80, 80))
        self.track_rects = []  # Store track rectangles for selection
        for i in range(5):
            track = QGraphicsRectItem(0, i * self.track_height, view_width, self.track_height)
            track.setBrush(track_brush)
            track.setPen(track_pen)
            track.setData(0, i)  # Store track index
            track.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)  # Make selectable
            track.setAcceptHoverEvents(True)  # For feedback
            self.track_background_group.addToGroup(track)
            self.track_rects.append(track)
        
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
        self.update_track_selection_feedback()  # Update visual feedback

    def update_time_display(self):
        '''
        Updates time-related UI elementes with current values (View)
        '''
        self.measure_edit.setText(f"Measure: {self.current_measure}:{self.current_beat}")
        self.tempo_edit.setText(f"Tempo: {self.bpm} BPM")
        self.time_edit.setText(f"Time: {self.time_signature}")

    def resizeEvent(self, event):
        '''
        Resizes track markers and notes windows based off window size (View)

        If someone expands the window or full screns it, the UI adjusts accordingly
        '''
        super().resizeEvent(event)
        self.update_tracks_and_markers()
        if self.notes_window and self.recording:
            self.snap_notes_window()

    def toggle_recording(self):
        '''
        Toggles recoridng state between start/stop (Presenter)
        '''
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        '''
        Begins a new recording with new container and timers (Presenter)
        '''
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
        self.snap_notes_window()

        # Determine selected track
        selected_items = self.track_scene.selectedItems()
        if selected_items and isinstance(selected_items[0], QGraphicsRectItem):
            track_index = selected_items[0].data(0)  # Get track index from data
            y_position = track_index * self.track_height
            print(f"Recording on track {track_index}")
        else:
            track_index = 0
            y_position = 0
            print("No track selected, defaulting to track 0")

        # Use playhead position for x
        start_x = self.playhead.line().x1()  # Start at red playhead
        self.current_container = self.DraggableContainer(self.track_height, start_x, 0, 0, self.track_height)
        self.current_container.setPos(start_x, y_position)
        self.current_container.current_track = track_index
        self.current_container.setBrush(QBrush(QColor(173, 216, 230, 100)))
        self.current_container.setPen(QPen(QColor(70, 130, 180, 200), 2))
        self.track_scene.addItem(self.current_container)
        self.containers.append(self.current_container)
        self.update_timer.start()
        self.playback_start_time = self.recording_session['start_time']
        self.playback_timer.start()
        self.update_tracks_and_markers()  # Ensure scene is wide enough

    def snap_notes_window(self):
        print("snapping notes lol")
        '''
        Positions (snaps) the notes window to the bottom of the DAW window (View)'''
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
        Adds a new note to recording session with new container and timers (Presenter)
        '''
        if self.recording and note_name not in self.recording_session['active_notes']:
            start_time = time.time()
            self.recording_session['active_notes'][note_name] = start_time
            # Calculate timestamp relative to playhead position
            playhead_x = self.playhead.line().x1()
            time_per_beat = 60 / self.bpm
            start_beat = (start_time - self.recording_session['start_time']) / time_per_beat
            x = playhead_x + (start_beat * self.base_note_width)  # Offset from playhead
            y = self.calculate_note_position(note_name)
            note = QGraphicsRectItem(0, 0, 0, self.note_height)
            note.setPos(x - self.current_container.x(), y)  # Relative to container’s start
            note.setBrush(QBrush(QColor(100, 149, 237)))
            note.setPen(QPen(Qt.GlobalColor.white))
            note.setParentItem(self.current_container)
            self.active_note_items[note_name] = note

    def note_stopped(self, note_name):
        '''
        Finalizes a note in the recording session, updates the UI, and records the duration (Presenter)
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
        Updates the note rectangles within the container (solid boxes) during recording (Presenter)
        '''
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
        '''
        Adjusts the size of note container (semi-transparent box) based on the notes (Presenter)
        '''
        if not self.current_container or not self.recording_session['notes'] and not self.active_note_items:
            return
        max_end_beat = 0
        if self.recording_session['notes']:
            max_end_beat = max(
                note['timestamp'] + note['duration'] for note in self.recording_session['notes']) * self.bpm / 60
        for note_name, start_time in self.recording_session['active_notes'].items():
            current_time = time.time()
            duration_beats = (current_time - start_time) * self.bpm / 60
            end_beat = (start_time - self.recording_session['start_time']) * self.bpm / 60 + duration_beats
            max_end_beat = max(max_end_beat, end_beat)
        session_width = max_end_beat * self.base_note_width
        self.current_container.setRect(0, 0, session_width, self.track_height)

    def stop_recording(self):
        '''
        Ends recording, finalizes notes, and autosaves (Presenter)
        '''
        if not self.recording:
            return
        self.recording = False
        self.update_timer.stop()
        self.playback_timer.stop()
        if self.notes_window:
            self.notes_window.close()
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
        self.update_tracks_and_markers()
        self.autosave()

    def note_to_frequency(self, note_name):
        '''
        Converts note names and octave combo into frequency in Hz (Model)
        '''
        note = note_name[:-1]
        octave = int(note_name[-1])
        semitone = self.note_order.index(note) + (octave - 4) * 12
        frequency = 261.63 * (2 ** (semitone / 12))
        return round(frequency, 2)

    def autosave(self):
        '''
        Saves all project data into .muse file (Model)
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
                # Use current x() position or else we will get notes playing at the wrong time
                "notes": notes
            })
        with open(self.autosave_file, 'w') as f:
            json.dump(project_data, f, indent=4)

    def save_project(self, filename):
        '''
        Saves all project data into .muse file (Model)

        For now it is the same as autosave, but in the future will be used for MANUAL saving
        '''
        self.autosave()
        
        if self.presenter:
            self.presenter.saved_projects_init()

    def load_project(self, filename):
        '''
        Loads project data from .muse file and rebuilds the UI based off that data (Presenter)
        '''
        with open(filename, 'r') as f:
            project_data = json.load(f)

        self.bpm = project_data["tempo"]
        self.time_signature = project_data["time_signature"]
        self.containers.clear()
        self.track_scene.clear()
        self.update_tracks_and_markers()
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
        self.playhead.setZValue(10)
        self.playhead.setVisible(True)

        for container_data in project_data["containers"]:
            container = self.DraggableContainer(self.track_height, 0, 0, 0, self.track_height)
            container.setBrush(QBrush(QColor(173, 216, 230, 100)))
            container.setPen(QPen(QColor(70, 130, 180, 200), 2))
            container.setPos(container_data["start_x"], container_data["track"] * self.track_height)
            container.current_track = container_data["track"]
            container.recording_session = {"notes": container_data["notes"]}

            max_width = 0
            for note_data in container_data["notes"]:
                start_x = note_data["timestamp"] * self.bpm / 60 * self.base_note_width
                width = note_data["duration"] * self.bpm / 60 * self.base_note_width
                y = self.calculate_note_position(note_data["note_name"])
                note = QGraphicsRectItem(0, 0, width, self.note_height)
                note.setPos(start_x, y)
                note.setBrush(QBrush(QColor(100, 149, 237)))
                note.setPen(QPen(Qt.GlobalColor.white))
                note.setParentItem(container)
                max_width = max(max_width, start_x + width)
            container.setRect(0, 0, max_width, self.track_height)
            self.track_scene.addItem(container)
            self.containers.append(container)

        self.current_x = max([c.x() + c.rect().width() for c in self.containers], default=0)
        self.update_time_display()

    def calculate_note_position(self, note_name):
        '''
        Calculates y-position for a note on the track - WITHIN the container (View)

        C4 solid note box should be towards the bottom of the container, B4 should be towards the top

        This method calculates this position.
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
        Togles between play, pause and stop states (Presenter)
        '''
        if self.paused:
            # TOGGLE PLAY
            self.paused = False
            self.playback_start_time = time.time() - (self.paused_position / (self.base_note_width * self.bpm / 60))
            self.playhead.setLine(self.paused_position, 0, self.paused_position, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.start_audio_playback()
            self.note_playback_timer.start()
            self.playback_stream.start()
        elif self.playing:
            # TOGGLE PAUSE
            self.paused = True
            self.paused_position = self.playhead.line().x1()
            self.playback_timer.stop()
            self.note_playback_timer.stop()
            self.playback_stream.stop()
            self.active_playback_notes.clear()
            self.scheduled_notes.clear()
        else:
            # TOGGLE STOP
            self.playing = True
            self.paused = False
            self.paused_position = None
            self.playback_start_time = time.time()
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)
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
        Initializes audio playback via note scheduler (Model)
        '''
        self.active_playback_notes.clear()
        self.scheduled_notes.clear()
        pixels_per_second = self.base_note_width * self.bpm / 60
        for container in self.containers:
            if not hasattr(container, 'recording_session') or not container.recording_session['notes']:
                continue
            # Calculate time offset based on current container position
            container_x_time = container.x() / pixels_per_second
            for note in container.recording_session['notes']:
                adjusted_start_time = note['timestamp'] + container_x_time
                elapsed = time.time() - self.playback_start_time
                if adjusted_start_time <= elapsed <= adjusted_start_time + note['duration']:
                    self.active_playback_notes[note['note_name']] = True
                elif adjusted_start_time > elapsed:
                    self.scheduled_notes.append({
                        'name': note['note_name'],
                        'start_time': adjusted_start_time,
                        'duration': note['duration']
                    })

    def check_note_playback(self):
        '''
        Checks and triggers the scheduled notes during playback (Presenter)
        '''
        if not self.playing or self.paused:
            return
        current_time = time.time() - self.playback_start_time
        notes_to_remove = []
        for i, note in enumerate(self.scheduled_notes):
            start_time = note['start_time']
            end_time = start_time + note['duration']
            name = note['name']
            if start_time <= current_time < end_time:
                if name not in self.active_playback_notes:
                    self.sound.note_on(name)
            elif current_time >= end_time:
                self.sound.note_off(name)
                notes_to_remove.append(i)

        for i in sorted(notes_to_remove, reverse=True):
            self.scheduled_notes.pop(i)

    def note_on(self, note, loop=False):
        '''
        Plays a note for audio playback (Model)
        '''
        if note not in self.active_playback_notes:
            data, samplerate = self.sound.notes[note]
            self.mutex.lock()
            self.active_playback_notes[note] = {"data": data, "play_pos": 0, "loop": loop}
            self.mutex.unlock()

    def note_off(self, note):
        '''
        Stops a note for audio playback (Model)
        '''
        self.mutex.lock()
        if note in self.active_playback_notes:
            del self.active_playback_notes[note]
        self.mutex.unlock()

    def playback_audio_callback(self, outdata, frames, time_info, status):
        '''
        Generates audio for active notes (Model)
        '''
        self.notes_window.sound.audio_callback(outdata, frames, time_info, status)

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
        Moves playhead and updates time display during playback (Presenter)

        Also handles stopping playback if it reaches the end of the track
        '''
        if self.playback_start_time is None or self.paused:
            return
        elapsed_time = time.time() - self.playback_start_time
        pixels_per_second = self.base_note_width * self.bpm / 60
        x_position = elapsed_time * pixels_per_second
        project_end = self.get_project_end()
        
        if x_position >= project_end:
            self.stop_playback_internal()
            return
        
        self.playhead.setLine(x_position, 0, x_position, 5 * self.track_height)
        self.playhead.setVisible(True)
        beat_position = x_position / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(x_position, 0, 10, self.track_height))
        if self.metronome_on and not self.paused:
            self.align_metronome_to_playhead()

    def stop_playback_internal(self):
        '''
        Completely stops playback and moves playhead to start (Presenter)
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
        Connects rewind button to its function (View)
        '''
        self.rewind.clicked.connect(self.rewind_one_measure)

    def rewind_one_measure(self):
        '''
        Rewinds playhead one measure (4 beats) (Presenter)
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
            self.playback_start_time = time.time() - new_elapsed_time
            if self.paused:
                self.paused_position = new_x
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))

    def connect_fastforward_button(self):
        '''
        Connects fast forward button to its function (View)
        '''
        self.fastForward.clicked.connect(self.fastforward_one_measure)

    def fastforward_one_measure(self):
        '''
        Fast forwards playhead one measure (4 beats) (Presenter)
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
            self.playback_start_time = time.time() - new_elapsed_time
            if self.paused:
                self.paused_position = new_x
        beat_position = new_x / self.base_note_width
        self.current_measure = int(beat_position // 4) + 1
        self.current_beat = int(beat_position % 4) + 1
        self.update_time_display()
        self.trackView.ensureVisible(QRectF(new_x, 0, 10, self.track_height))

    def toggle_metronome(self):
        '''
        Toggles metronome on/off (Presenter)
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
        Syncs metronome timer to playhead position (Presenter)
        '''
        if self.playhead and (self.playing or self.paused):
            current_x = self.playhead.line().x1()
            beat_position = current_x / self.base_note_width
            time_per_beat = 60 / self.bpm
            offset = (beat_position % 1) * time_per_beat * 1000
            self.metronome_timer.setInterval(int(60000 / self.bpm) - int(offset))

    def metronome_click(self):
        '''
        Handles metronome beat, click sound and updates time (Presenter)
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

    def update_tempo(self):
        '''
        Updates BPM of DAW as well as metronome timer/display (Presenter)
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
        Updates time signature from user input (Presenter)
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
        Updates measure and beat from user input (Presenter)
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
        Autosaves, cleans and closes the DAW (Presenter)
        '''
        self.autosave()
        self.playback_stream.stop()
        self.note_playback_timer.stop()
        event.accept()
    
    def export_as_mp3(self, output_path=None):
        """
        Export the current project as an MP3 file using preloaded .aiff piano samples.
        If output_path is not provided, prompt the user for a file location.
        """
        try:
            # Determine output path if not provided
            if not output_path:
                from PyQt6.QtWidgets import QFileDialog
                output_path, _ = QFileDialog.getSaveFileName(
                    self, "Save MP3 File", "", "MP3 Files (*.mp3)"
                )
                if not output_path:
                    QMessageBox.warning(self, "Export Failed", "No output file selected.")
                    return

            # Calculate total duration of the project (in seconds)
            total_duration = 0
            pixels_per_second = self.base_note_width * self.bpm / 60  # Convert pixels to seconds
            for container in self.containers:
                if hasattr(container, 'recording_session') and container.recording_session['notes']:
                    container_start_time = container.x() / pixels_per_second
                    for note in container.recording_session['notes']:
                        end_time = container_start_time + note['timestamp'] + note['duration']
                        total_duration = max(total_duration, end_time)
            print(f"Calculated total duration: {total_duration} seconds")  # Debug

            if total_duration <= 0:
                QMessageBox.warning(self, "Export Failed", "No audio data to export.")
                return

            # Generate audio data using .aiff samples
            sample_rate = self.sample_rate  # 44100 Hz
            num_samples = int(total_duration * sample_rate)
            audio_data = np.zeros(num_samples, dtype=np.float32)
            print(f"Initializing audio_data with {num_samples} samples")  # Debug

            # Use piano samples exclusively
            instrument = "Piano"
            if instrument not in self.instruments:
                raise ValueError(f"Instrument {instrument} not found in self.instruments")

            # Process each note in all containers
            for container in self.containers:
                if hasattr(container, 'recording_session') and container.recording_session['notes']:
                    container_start_time = container.x() / pixels_per_second
                    print(f"Processing container at x={container.x()}, start_time={container_start_time} seconds")  # Debug
                    for note in container.recording_session['notes']:
                        adjusted_timestamp = container_start_time + note['timestamp']
                        start_sample = int(adjusted_timestamp * sample_rate)
                        duration_samples = int(note['duration'] * sample_rate)
                        note_name = note['note_name']
                        print(f"Processing note: {note_name}, start_sample: {start_sample}, duration_samples: {duration_samples}")  # Debug

                        # Load the .aiff sample
                        if note_name in self.instruments[instrument]:
                            sample_data = self.instruments[instrument][note_name]['data']
                            sample_rate_sample = self.instruments[instrument][note_name]['sample_rate']
                            print(f"Loaded sample for {note_name}, length: {len(sample_data)}, sample_rate: {sample_rate_sample}")  # Debug

                            # Resample if necessary
                            if sample_rate_sample != sample_rate:
                                from scipy import signal
                                sample_data = signal.resample(sample_data, int(len(sample_data) * sample_rate / sample_rate_sample))
                                print(f"Resampled {note_name} to {len(sample_data)} samples")  # Debug

                            # Trim or loop the sample to match duration
                            if len(sample_data) < duration_samples:
                                num_loops = (duration_samples + len(sample_data) - 1) // len(sample_data)
                                sample_data = np.tile(sample_data, num_loops)[:duration_samples]
                                print(f"Looped {note_name} {num_loops} times to match duration")  # Debug
                            elif len(sample_data) > duration_samples:
                                sample_data = sample_data[:duration_samples]
                                print(f"Trimmed {note_name} to match duration")  # Debug

                            # Apply volume scaling and mix
                            samples = sample_data * 0.5  # Adjust volume
                            end_sample = start_sample + duration_samples
                            if end_sample <= len(audio_data):
                                audio_data[start_sample:end_sample] += samples
                                print(f"Mixed {note_name} into audio_data[{start_sample}:{end_sample}]")  # Debug
                            else:
                                excess = end_sample - len(audio_data)
                                audio_data[start_sample:] += samples[:-excess]
                                print(f"Trimmed and mixed {note_name} due to length mismatch, excess: {excess}")  # Debug
                        else:
                            print(f"Warning: Sample for {note_name} not found in {instrument}")

            # Normalize audio to prevent clipping
            max_amplitude = np.max(np.abs(audio_data))
            if max_amplitude > 0:
                audio_data = audio_data / max_amplitude
                print(f"Normalized audio, max amplitude: {max_amplitude}")  # Debug
            else:
                print("Warning: Audio data is silent (max amplitude = 0)")

            # Save as temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
                sf.write(wav_path, audio_data, sample_rate, format='WAV')
                print(f"Saved temporary WAV file: {wav_path}")  # Debug

            # Use FFmpeg to convert WAV to MP3
            mp3_path = output_path
            ffmpeg_cmd = [
                'ffmpeg', '-i', wav_path, '-c:a', 'libmp3lame', '-q:a', '2',  # Quality setting (2 is VBR, good quality)
                '-y', mp3_path  # Overwrite output file if it exists
            ]
            result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(f"FFmpeg output: {result.stdout}")
            print(f"FFmpeg errors (if any): {result.stderr}")

            # Clean up temporary WAV file
            os.unlink(wav_path)

            QMessageBox.information(self, "Export Successful", f"Exported to: {mp3_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting MP3: {str(e)}")
            print(f"Export error details: {str(e)}")
    
    def load_instrument_samples(self, instrument_name):
        """
        Load .aiff samples for the specified instrument into self.instruments.
        """
        instrument_dir = os.path.join(project_root, "Instruments", instrument_name)
        if not os.path.exists(instrument_dir):
            return
        self.instruments[instrument_name] = {}
        
        for file in os.listdir(instrument_dir):
            if file.endswith('.aiff'):
                note_name = os.path.splitext(file)[0]  # e.g., "C4"
                file_path = os.path.join(instrument_dir, file)
                try:
                    data, sample_rate = sf.read(file_path)
                    if data.ndim > 1:
                        data = np.mean(data, axis=1)  # Convert stereo to mono if needed
                    
                    # Pre-process the sample (match SoundGenerator logic)
                    end_frame = int(2 * sample_rate)  # 2 seconds max
                    max_idx = np.argmax(abs(data))
                    start_frame = 0
                    for x in range(max_idx - 1, -1, -1):
                        if abs(data[x]) < 0.0010:  # Threshold for silence
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
        """
        Closes the DAW UI and opens the Main Menu UI by notifying the Presenter.
        """
        #print("EXIT TO MENU REQUESTED")
        # Signal the Presenter to switch back to Main_Menu and close this window
        if self.presenter:  # Assuming the Presenter is passed or accessible
            self.presenter.on_exit_to_menu_requested()
        else:
            # Fallback: Close this window and show Main_Menu directly (if Presenter isn’t available)
            self.close()
            main_menu = Main_Menu()
            main_menu.show()
            
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
        
        def mousePressEvent(self, event):
            print(f"Container clicked at track {self.current_track}")  # Debug
            super().mousePressEvent(event)