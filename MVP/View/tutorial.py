# MVP/View/tutorial.py
from PyQt6.QtWidgets import QDialog, QWidget, QPushButton
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
import os
from paths import resource_path  # ✅ NEW

class Tutorial:
    def __init__(self):
        super().__init__()
        
        self.tutorial_start = QPushButton("Welcome to the Interactive Tutorial \n\n Click Here to Begin", self)
        self.tutorial_start.setGeometry(600, 100, 140, 40)
        self.tutorial_start.resize(self.tutorial_start.sizeHint())
        self.tutorial_start.hide()
        
        self.tutorial_instument = QPushButton("\n⬅  Start by selecting an instrument\n", self)
        self.tutorial_instument.setGeometry(185, 120, 140, 40)
        self.tutorial_instument.resize(self.tutorial_instument.sizeHint())
        self.tutorial_instument.hide()
        
        self.tutorial_record = QPushButton("⬆\nClick to start recording\n", self)
        self.tutorial_record.setGeometry(390, 90, 140, 40)
        self.tutorial_record.resize(self.tutorial_record.sizeHint())
        self.tutorial_record.hide()
        
        self.tutorial_metronome = QPushButton("⬆\nClick for a metronome\n", self)
        self.tutorial_metronome.setGeometry(600, 90, 140, 40)
        self.tutorial_metronome.resize(self.tutorial_metronome.sizeHint())
        self.tutorial_metronome.hide()
        
        self.tutorial_track = QPushButton("\nDrag track location\n⬇", self)
        self.tutorial_track.setGeometry(700, 140, 140, 40)
        self.tutorial_track.resize(self.tutorial_track.sizeHint())
        self.tutorial_track.hide()
        
        self.tutorial_play = QPushButton("⬆\nClick to play recording\n", self)
        self.tutorial_play.setGeometry(490, 90, 140, 40)
        self.tutorial_play.resize(self.tutorial_play.sizeHint())
        self.tutorial_play.hide()
        
        self.tutorial_time = QPushButton("⬆\nForward/Rewind track\n", self)
        self.tutorial_time.setGeometry(290, 90, 140, 40)
        self.tutorial_time.resize(self.tutorial_time.sizeHint())
        self.tutorial_time.hide()
        
        
        if (self.presenter.tutorial_mode):
            self.tutorial_start.show()
        
        self.tutorial_start.clicked.connect(self.tutorial_start_next)
        self.tutorial_instument.clicked.connect(self.tutorial_instrument_next)
        self.tutorial_record.clicked.connect(self.tutorial_record_next)
        self.tutorial_metronome.clicked.connect(self.tutorial_metronome_next)
        self.tutorial_track.clicked.connect(self.tutorial_track_next)
        self.tutorial_play.clicked.connect(self.tutorial_play_next)
        self.tutorial_time.clicked.connect(self.tutorial_time_next)
            

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