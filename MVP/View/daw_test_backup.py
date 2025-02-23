import sys
import os
import time
import json
import numpy as np
import sounddevice as sd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                            QGraphicsScene, QGraphicsRectItem, QGraphicsItemGroup, 
                            QLineEdit, QWidget, QHBoxLayout)
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
        
        self.track_height = 80
        self.base_note_width = 100
        self.note_height = 20
        self.current_x = 0
        self.measure_width = 400
        self.bpm = 120
        self.time_signature = "4/4"
        self.current_measure = 1
        self.current_beat = 1
        
        self.track_scene = QGraphicsScene()
        self.trackView.setScene(self.track_scene)
        self.trackView.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.trackView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
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
        self.measure_edit.setStyleSheet("QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.tempo_edit.setStyleSheet("QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.time_edit.setStyleSheet("QLineEdit {color: #C8C8C8; background-color: #333333; padding: 5px; border: none; qproperty-alignment: AlignCenter;} QLineEdit:focus {background-color: white; border: 1px solid gray;}")
        self.timeView.setStyleSheet("background-color: #333333; border: 1px solid #555555;")
        
        self.measure_edit.editingFinished.connect(self.update_measure)
        self.tempo_edit.editingFinished.connect(self.update_tempo)
        self.time_edit.editingFinished.connect(self.update_time)
        
        self.track_background_group = QGraphicsItemGroup()
        self.track_scene.addItem(self.track_background_group)
        self.update_tracks_and_markers()
        self.update_time_display()
        
        self.recording = False
        self.recording_session = None
        self.playing = False
        self.paused = False
        self.playback_timer = QTimer()
        self.playback_timer.setInterval(10)
        self.playback_timer.timeout.connect(self.update_playhead_continuous)
        self.playhead = self.track_scene.addLine(0, 0, 0, 5 * self.track_height, QPen(Qt.GlobalColor.red, 2))
        self.playhead.setZValue(10)
        self.playhead.setVisible(True)
        self.playback_start_time = None
        self.paused_position = None
        self.current_container = None
        self.active_note_items = {}
        self.containers = []
        
        self.sample_rate = 44100
        self.playback_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            blocksize=1024,
            channels=1,
            callback=self.playback_audio_callback,
            dtype='float32'
        )
        self.active_playback_notes = {}
        self.phase = {}
        self.notes_window = None  # Initialize as None

        self.record.clicked.connect(self.toggle_recording)
        self.play.clicked.connect(self.toggle_playback)
        self.connect_rewind_button()
        self.connect_fastforward_button()

        self.metronome_on = False
        self.metronome_timer = QTimer()
        self.metronome_timer.timeout.connect(self.metronome_click)
        self.metronome_timer.setInterval(int(60000 / self.bpm))
        self.metronome.clicked.connect(self.toggle_metronome)

        self.update_timer = QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.update_active_notes)

        icons_dir = os.path.join(os.path.dirname(__file__), "Icons")
        self.play_icon_path = os.path.join(icons_dir, "Play.png")
        self.pause_icon_path = os.path.join(icons_dir, "Pause.png")
        self.set_button_icons()

        self.autosave_file = "autosave.muse"
        self.note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def set_button_icons(self):
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
            self.track_background_group.addToGroup(self.track_scene.addLine(x_pos, 0, x_pos, 5 * self.track_height, measure_pen))
            for b in range(1, 4):
                beat_x = x_pos + b * self.base_note_width
                self.track_scene.addLine(beat_x, 0, beat_x, 5 * self.track_height, beat_tick_pen)
            text = self.track_scene.addText(str(m + 1))
            text.setPos(x_pos + 10, 5)
            text.setDefaultTextColor(QColor(150, 150, 150))
            self.track_background_group.addToGroup(text)
        self.track_scene.setSceneRect(0, 0, view_width, 5 * self.track_height)

    def update_time_display(self):
        self.measure_edit.setText(f"Measure: {self.current_measure}:{self.current_beat}")
        self.tempo_edit.setText(f"Tempo: {self.bpm} BPM")
        self.time_edit.setText(f"Time: {self.time_signature}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_tracks_and_markers()
        if self.notes_window and self.recording:  # Reposition notes window if open
            self.snap_notes_window()

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
        self.snap_notes_window()  # Snap to DAW bottom
        
        self.current_container = DraggableContainer(self.track_height, self.current_x, 0, 0, self.track_height)
        self.current_container.setBrush(QBrush(QColor(173, 216, 230, 100)))
        self.current_container.setPen(QPen(QColor(70, 130, 180, 200), 2))
        self.track_scene.addItem(self.current_container)
        self.containers.append(self.current_container)
        self.update_timer.start()
        self.playhead.setLine(0, 0, 0, 5 * self.track_height)
        self.playhead.setVisible(True)
        self.playback_start_time = self.recording_session['start_time']
        self.playback_timer.start()

    def snap_notes_window(self):
        """Snap NotesWindow to the bottom of DAWTest."""
        if not self.notes_window:
            return
        daw_geometry = self.geometry()
        notes_geometry = self.notes_window.geometry()
        
        # Position at bottom of DAW
        x = daw_geometry.x()  # Align left with DAW
        y = daw_geometry.bottom() - notes_geometry.height()  # Snap to bottom
        notes_geometry.moveTo(x, y)
        
        # Match DAW width
        notes_geometry.setWidth(daw_geometry.width())
        self.notes_window.setGeometry(notes_geometry)
        self.notes_window.raise_()  # Bring to front

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
            frequency = self.note_to_frequency(note_name)
            self.recording_session['notes'].append({
                'timestamp': start_time - self.recording_session['start_time'],
                'frequency': frequency,
                'duration': duration,
                'note_name': note_name
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                width = (duration * self.bpm / 60) * self.base_note_width
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
            max_end_beat = max(note['timestamp'] + note['duration'] for note in self.recording_session['notes']) * self.bpm / 60
        for note_name, start_time in self.recording_session['active_notes'].items():
            current_time = time.time()
            duration_beats = (current_time - start_time) * self.bpm / 60
            end_beat = (start_time - self.recording_session['start_time']) * self.bpm / 60 + duration_beats
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
            frequency = self.note_to_frequency(note_name)
            self.recording_session['notes'].append({
                'timestamp': start_time - self.recording_session['start_time'],
                'frequency': frequency,
                'duration': duration,
                'note_name': note_name
            })
            if note_name in self.active_note_items:
                note = self.active_note_items.pop(note_name)
                note.setRect(0, 0, (duration * self.bpm / 60) * self.base_note_width, self.note_height)
        self.update_container_size()
        if self.current_container:
            self.current_x += self.current_container.rect().width()
            self.current_container.recording_session = self.recording_session
            self.current_container = None
        self.update_tracks_and_markers()
        self.playhead.setLine(0, 0, 0, 5 * self.track_height)
        self.playhead.setVisible(True)
        self.autosave()

    def note_to_frequency(self, note_name):
        note = note_name[:-1]
        octave = int(note_name[-1])
        semitone = self.note_order.index(note) + (octave - 4) * 12
        frequency = 261.63 * (2 ** (semitone / 12))
        return round(frequency, 2)

    def autosave(self):
        project_data = {
            "tempo": self.bpm,
            "time_signature": self.time_signature,
            "containers": []
        }
        for container in self.containers:
            notes = container.recording_session['notes'] if hasattr(container, 'recording_session') and container.recording_session else []
            project_data["containers"].append({
                "track": container.current_track,
                "start_x": container.x(),
                "notes": notes
            })
        with open(self.autosave_file, 'w') as f:
            json.dump(project_data, f, indent=4)

    def save_project(self, filename):
        self.autosave()
        print(f"Manual save to {filename} not yet implemented; autosaved to {self.autosave_file}")

    def load_project(self, filename):
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
            container = DraggableContainer(self.track_height, 0, 0, 0, self.track_height)
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
        note = note_name[:-1]
        octave = int(note_name[-1])
        note_index = self.note_order.index(note)
        position = (octave - 3) * 12 + note_index
        total_notes = 24
        y_pos = (1 - position / total_notes) * (self.track_height - self.note_height)
        return y_pos

    def toggle_playback(self):
        if self.paused:
            self.paused = False
            self.playback_start_time = time.time() - (self.paused_position / (self.base_note_width * self.bpm / 60))
            self.playhead.setLine(self.paused_position, 0, self.paused_position, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.playback_stream.start()
        elif self.playing:
            self.paused = True
            self.paused_position = self.playhead.line().x1()
            self.playback_timer.stop()
            self.playback_stream.stop()
            self.active_playback_notes.clear()
        else:
            self.playing = True
            self.paused = False
            self.paused_position = None
            self.playback_start_time = time.time()
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.playback_timer.start()
            self.start_audio_playback()
            self.playback_stream.start()
        self.set_button_icons()
        if not self.playing and not self.paused:
            self.playhead.setLine(0, 0, 0, 5 * self.track_height)
            self.playhead.setVisible(True)
            self.update_time_display()

    def start_audio_playback(self):
        self.active_playback_notes.clear()
        for container in self.containers:
            if not hasattr(container, 'recording_session') or not container.recording_session['notes']:
                continue
            for note in container.recording_session['notes']:
                start_time = note['timestamp']
                elapsed = time.time() - self.playback_start_time
                if start_time <= elapsed <= start_time + note['duration']:
                    self.active_playback_notes[note['frequency']] = True
                elif start_time > elapsed:
                    delay = int((start_time - elapsed) * 1000)
                    QTimer.singleShot(delay, lambda f=note['frequency']: self.note_on(f))
                    QTimer.singleShot(delay + int(note['duration'] * 1000), lambda f=note['frequency']: self.note_off(f))

    def note_on(self, frequency):
        self.active_playback_notes[frequency] = True
        if frequency not in self.phase:
            self.phase[frequency] = 0

    def note_off(self, frequency):
        if frequency in self.active_playback_notes:
            del self.active_playback_notes[frequency]
        if frequency in self.phase:
            del self.phase[frequency]

    def playback_audio_callback(self, outdata, frames, time_info, status):
        outdata.fill(0)
        t = np.arange(frames) / self.sample_rate
        for freq in list(self.active_playback_notes.keys()):
            if freq not in self.phase:
                self.phase[freq] = 0
            samples = 0.3 * np.sin(2 * np.pi * freq * t + self.phase[freq])
            outdata[:, 0] += samples
            self.phase[freq] += 2 * np.pi * freq * frames / self.sample_rate
            self.phase[freq] %= 2 * np.pi

    def update_playhead_continuous(self):
        if self.playback_start_time is None or self.paused:
            return
        elapsed_time = time.time() - self.playback_start_time
        pixels_per_second = self.base_note_width * self.bpm / 60
        x_position = elapsed_time * pixels_per_second
        if x_position >= 2000:
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
        self.start_audio_playback()

    def stop_playback_internal(self):
        self.playing = False
        self.paused = False
        self.paused_position = None
        self.playback_timer.stop()
        self.playback_stream.stop()
        self.active_playback_notes.clear()
        self.playhead.setLine(0, 0, 0, 5 * self.track_height)
        self.playhead.setVisible(True)
        self.update_time_display()

    def connect_rewind_button(self):
        self.rewind.clicked.connect(self.rewind_one_measure)

    def rewind_one_measure(self):
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
        self.fastForward.clicked.connect(self.fastforward_one_measure)

    def fastforward_one_measure(self):
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
        if self.playhead and (self.playing or self.paused):
            current_x = self.playhead.line().x1()
            beat_position = current_x / self.base_note_width
            time_per_beat = 60 / self.bpm
            offset = (beat_position % 1) * time_per_beat * 1000
            self.metronome_timer.start(int(60000 / self.bpm) - offset)

    def metronome_click(self):
        print("Click - Beat at BPM:", self.bpm)
        if self.playing or self.paused:
            current_x = self.playhead.line().x1()
            beat_position = current_x / self.base_note_width
            self.current_measure = int(beat_position // 4) + 1
            self.current_beat = int(beat_position % 4) + 1
            self.update_time_display()

    def update_tempo(self):
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
        self.autosave()
        self.playback_stream.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAWTest()
    window.show()
    #window.load_project("autosave.muse")       # TESTING LOADING PROJECTS
    sys.exit(app.exec())