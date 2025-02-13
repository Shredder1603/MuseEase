import pytest
from PyQt6.QtCore import Qt
from Notes import MainWindow

# Expected frequencies at octave 4
EXPECTED_FREQUENCIES = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
    'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
    'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
}

@pytest.fixture
def app(qtbot):
    """Set up the Qt application for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

class MockEvent:
    """Mock QKeyEvent for testing."""
    def __init__(self, key): self._key = key
    def key(self): return self._key
    def isAutoRepeat(self): return False

def test_key_to_note_mapping(app, capsys):
    """Ensure key presses match expected note names."""
    key_map = {Qt.Key.Key_A: 'C', Qt.Key.Key_W: 'C#', Qt.Key.Key_S: 'D',
               Qt.Key.Key_E: 'D#', Qt.Key.Key_D: 'E', Qt.Key.Key_F: 'F',
               Qt.Key.Key_T: 'F#', Qt.Key.Key_G: 'G', Qt.Key.Key_Y: 'G#',
               Qt.Key.Key_H: 'A', Qt.Key.Key_U: 'A#', Qt.Key.Key_J: 'B'}
 
    # Test ALL keys   
    for key, expected_note in key_map.items():
        event = MockEvent(key)
        app.keyPressEvent(event)
        actual_note = app.noteNameA.text()
        print(f"Key {key} -> Expected: {expected_note}{app.current_octave}, Actual: {actual_note}")
        assert actual_note == f"{expected_note}{app.current_octave}"
        app.keyReleaseEvent(event)

    print("\nCaptured Output:\n", capsys.readouterr().out)

def test_octave_changes(app, capsys):
    """Ensure octave increase/decrease works correctly."""
    initial = app.current_octave
    for _ in range(4): app.increase_octave(); assert app.current_octave <= 8
    for _ in range(4): app.decrease_octave(); assert app.current_octave >= 1
    print(f"Initial: {initial}, Final: {app.current_octave}")
    print("\nCaptured Output:\n", capsys.readouterr().out)

def test_frequency_calculation(app, capsys):
    """Ensure note frequencies scale correctly across octaves."""
    
    # Test ALL frequencies 
    for octave in range(1, 9):
        app.current_octave = octave
        for note, base_freq in EXPECTED_FREQUENCIES.items():
            expected_freq = base_freq * (2 ** (octave - 4))
            app.make_press_handler(note)()
            actual_freq = app.active_notes[note]
            print(f"{note}{octave} -> Expected: {expected_freq:.2f} Hz, Actual: {actual_freq:.2f} Hz")
            assert actual_freq == expected_freq
            app.make_release_handler(note)()

    print("\nCaptured Output:\n", capsys.readouterr().out)
