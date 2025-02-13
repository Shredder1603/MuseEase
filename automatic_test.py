import pytest
from PyQt6.QtCore import Qt
from Notes import MainWindow, SoundGenerator

# Expected note-to-frequency mapping at octave 4
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
    """Simulates a QKeyEvent for testing key press/release events."""
    def __init__(self, key):
        self._key = key
    def key(self):
        return self._key
    def isAutoRepeat(self):
        return False

def test_key_to_note_mapping(app, capsys):
    """Test if key presses correspond to the correct note names and print detailed output."""
    
    # Test ALL keys 
    key_map = {
        Qt.Key.Key_A: 'C', Qt.Key.Key_W: 'C#', Qt.Key.Key_S: 'D',
        Qt.Key.Key_E: 'D#', Qt.Key.Key_D: 'E', Qt.Key.Key_F: 'F',
        Qt.Key.Key_T: 'F#', Qt.Key.Key_G: 'G', Qt.Key.Key_Y: 'G#',
        Qt.Key.Key_H: 'A', Qt.Key.Key_U: 'A#', Qt.Key.Key_J: 'B'
    }

    for key, expected_note in key_map.items():
        event = MockEvent(key)
        app.keyPressEvent(event)

        actual_note = app.noteNameA.text()
        print(f"Key Pressed: {key} | Expected Note: {expected_note}{app.current_octave} | Actual Note: {actual_note}")

        assert actual_note == f"{expected_note}{app.current_octave}", f"FAILED for key {key}: Expected {expected_note}{app.current_octave}, but got {actual_note}"

        app.keyReleaseEvent(event)

    captured = capsys.readouterr()
    print("\nCaptured Output:\n", captured.out)

def test_octave_changes(app, capsys):
    """Test if octave buttons correctly increase and decrease octaves with detailed print."""
    initial_octave = app.current_octave

    print(f"Initial Octave: {initial_octave}")

    # Test octave up
    for _ in range(4):
        app.increase_octave()
        print(f"Octave Increased -> Current Octave: {app.current_octave}")
        assert app.current_octave <= 8, "Octave exceeded max limit (8)."

    # Test octave down
    for _ in range(4):
        app.decrease_octave()
        print(f"Octave Decreased -> Current Octave: {app.current_octave}")
        assert app.current_octave >= 1, "Octave dropped below min limit (1)."

    captured = capsys.readouterr()
    print("\nCaptured Output:\n", captured.out)

def test_frequency_calculation(app, capsys):
    """Test if the correct frequency is computed based on octave changes with detailed output."""
    
    # Test ALL frequencies 
    for octave in range(1, 9):
        app.current_octave = octave
        for note, base_freq in EXPECTED_FREQUENCIES.items():
            expected_freq = base_freq * (2 ** (octave - 4))
            app.make_press_handler(note)()

            actual_freq = app.active_notes[note]
            print(f"Note: {note}{octave} | Expected Frequency: {expected_freq:.2f} Hz | Actual Frequency: {actual_freq:.2f} Hz")

            assert actual_freq == expected_freq, f"FAILED for {note}{octave}: Expected {expected_freq}, but got {actual_freq}"

            app.make_release_handler(note)()

    captured = capsys.readouterr()
    print("\nCaptured Output:\n", captured.out)

def test_sound_generator(capsys):
    """Test the SoundGenerator class to ensure notes are added and removed correctly with detailed print."""
    
    # Test if Notes ON/OFF actually work
    sound = SoundGenerator()

    test_freq = 440.00  # A4
    sound.note_on(test_freq)
    print(f"Testing SoundGenerator | Note On: {test_freq} Hz | Active Notes: {list(sound.active_notes.keys())}")
    assert test_freq in sound.active_notes, "Failed to add active note"

    sound.note_off(test_freq)
    print(f"Testing SoundGenerator | Note Off: {test_freq} Hz | Active Notes: {list(sound.active_notes.keys())}")
    assert test_freq not in sound.active_notes, "Failed to remove active note"

    captured = capsys.readouterr()
    print("\nCaptured Output:\n", captured.out)
