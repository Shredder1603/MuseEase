import os
import numpy as np
from pydub import AudioSegment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "Raw Guitar Samples")
NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def get_note_range(start_note, end_note):
    def parts(n):
        return (n[:2], int(n[2])) if n[1] in ['b', '#'] else (n[0], int(n[1]))

    s_note, s_oct = parts(start_note)
    e_note, e_oct = parts(end_note)
    notes = []
    cur_oct, idx = s_oct, NOTES.index(s_note)

    while cur_oct < e_oct or (cur_oct == e_oct and idx <= NOTES.index(e_note)):
        while idx < len(NOTES):
            notes.append(f"{NOTES[idx]}{cur_oct}")
            if cur_oct == e_oct and NOTES[idx] == e_note:
                return notes
            idx += 1
        idx = 0
        cur_oct += 1
    return notes

def parse_range(rng):
    return (rng[:3], rng[3:]) if rng[1] in ['b', '#'] else (rng[:2], rng[2:])

def detect_onsets(audio, threshold_db=-30, min_spacing_ms=400):
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels)).mean(axis=1)
    samples /= np.max(np.abs(samples)) + 1e-9
    energy = 20 * np.log10(np.abs(samples) + 1e-10)
    spacing = int(min_spacing_ms * audio.frame_rate / 1000)
    onsets, last = [], 0
    for i in range(len(energy)):
        if energy[i] > threshold_db and (i - last) > spacing:
            onsets.append(int(i * 1000 / audio.frame_rate))
            last = i
    return onsets

# Pass 1: Convert .aif/.aiff to .wav
print(" Converting .aif/.aiff to .wav...")
for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith((".aif", ".aiff")):
        in_path = os.path.join(INPUT_DIR, fname)
        out_path = os.path.join(INPUT_DIR, fname.replace(".aif", ".wav").replace(".aiff", ".wav"))
        try:
            audio = AudioSegment.from_file(in_path, format="aiff")
            audio.export(out_path, format="wav", parameters=["-acodec", "pcm_s16le"])
            print(f" Converted: {fname} → {os.path.basename(out_path)}")
        except Exception as e:
            print(f" Failed to convert {fname}: {e}")

# Pass 2: Rename .wavf → .wav if needed
for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith(".wavf"):
        old_path = os.path.join(INPUT_DIR, fname)
        new_path = os.path.join(INPUT_DIR, fname.replace(".wavf", ".wav"))
        os.rename(old_path, new_path)
        print(f" Renamed: {fname} → {os.path.basename(new_path)}")

# Pass 3: Detect onsets and split into notes
print("\n🎼 Splitting into notes...")
for fname in os.listdir(INPUT_DIR):
    if fname.lower().endswith(".wav") and "sul" in fname:
        parts = fname.split('.')
        if len(parts) < 4:
            print(f" Skipping malformed filename: {fname}")
            continue
        technique = parts[2]
        note_range = parts[3]
        start_note, end_note = parse_range(note_range)
        note_list = get_note_range(start_note, end_note)

        path = os.path.join(INPUT_DIR, fname)
        audio = AudioSegment.from_file(path, format="wav")
        print(f"\n Processing {fname} ({len(audio)} ms, {audio.frame_rate} Hz)")

        onsets = detect_onsets(audio)
        print(f" Detected {len(onsets)} onsets (Expected: {len(note_list)})")

        if not onsets:
            print(f" No onsets found in {fname} — skipping")
            continue

        for i in range(min(len(note_list), len(onsets))):
            start = onsets[i]
            end = onsets[i + 1] if i + 1 < len(onsets) else len(audio)
            chunk = audio[start:end]
            out_name = f"{technique}_{note_list[i]}.wav"
            chunk.export(os.path.join(INPUT_DIR, out_name), format="wav", parameters=["-acodec", "pcm_s16le"])
            print(f" Saved: {out_name} ({end - start} ms)")

print("\n All done!")
