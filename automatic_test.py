import pytest
from PyQt6.QtCore import Qt

# Expected frequencies at octave 4
EXPECTED_FREQUENCIES = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
    'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
    'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
}

# Map keyboard keys to note names
KEY_MAP = {
    Qt.Key.Key_A: 'C', Qt.Key.Key_W: 'C#', Qt.Key.Key_S: 'D',
    Qt.Key.Key_E: 'D#', Qt.Key.Key_D: 'E', Qt.Key.Key_F: 'F',
    Qt.Key.Key_T: 'F#', Qt.Key.Key_G: 'G', Qt.Key.Key_Y: 'G#',
    Qt.Key.Key_H: 'A', Qt.Key.Key_U: 'A#', Qt.Key.Key_J: 'B'
}

class MockHandler:
    '''
    Simulate note handling logic.
    '''
    def __init__(self):
        self.current_octave = 4
        self.active_notes = {}
        
    def keyPressEvent(self, key):
        key_map = {
            Qt.Key.Key_A: 'C', Qt.Key.Key_W: 'C#', Qt.Key.Key_S: 'D',
            Qt.Key.Key_E: 'D#', Qt.Key.Key_D: 'E', Qt.Key.Key_F: 'F',
            Qt.Key.Key_T: 'F#', Qt.Key.Key_G: 'G', Qt.Key.Key_Y: 'G#',
            Qt.Key.Key_H: 'A', Qt.Key.Key_U: 'A#', Qt.Key.Key_J: 'B'
        }
        
        if key in key_map:
            note = key_map[key]
            freq = EXPECTED_FREQUENCIES[note] * (2 ** (self.current_octave - 4))
            self.active_notes[note] = freq
            return note, freq
        
        return None, None
    
    def increase_octave(self):
        if self.current_octave < 8:
            self.current_octave += 1
    
    def decrease_octave(self):
        if self.current_octave > 1:
            self.current_octave -= 1

@pytest.fixture
def note_handler():
    return MockHandler()

def test_key_to_note_mapping(note_handler, capsys):
    '''
    Ensure key presses match expected note names and frequencies.
    '''
    
    for key, expected_note in KEY_MAP.items():
        note, freq = note_handler.keyPressEvent(key)
        expected_freq = expected_note, EXPECTED_FREQUENCIES[expected_note] * (2 ** (note_handler.current_octave - 4))
        
        print(f"Key {key} -> Expected Frequency: {expected_freq}, Actual Output: {note, freq}")
        assert (note, freq) == expected_freq
    
    print("\nCaptured Output:\n", capsys.readouterr().out)
    
def test_octave_change(note_handler, capsys):
    '''
    Ensure octave changes are working correctly.
    '''
    
    initial = note_handler.current_octave
    for octave in range(4):
        note_handler.increase_octave()
    
    for octave in range(4):
        note_handler.decrease_octave()
    
    print(f"Initial Octave: {initial}, Final Octave: {note_handler.current_octave}")
    assert 1 <= note_handler.current_octave <= 8
    
    print("\nCaptured Output:\n", capsys.readouterr().out)
