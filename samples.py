import os
from pydub import AudioSegment
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "Raw Guitar Samples")       # Raw input
OUTPUT_DIR = os.path.join(BASE_DIR, "Instruments", "Guitar")   # Final output
os.makedirs(OUTPUT_DIR, exist_ok=True)

NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def get_note_range(start_note, end_note):
    def note_parts(note):
        if note[1] in ['b', '#']:
            return note[:2], int(note[2])
        else:
            return note[0], int(note[1])
    
    start_n, start_oct = note_parts(start_note)
    end_n, end_oct = note_parts(end_note)

    note_list = []
    cur_oct = start_oct
    idx = NOTES.index(start_n)

    while cur_oct < end_oct or (cur_oct == end_oct and idx <= NOTES.index(end_n)):
        while idx < len(NOTES):
            note_list.append(f"{NOTES[idx]}{cur_oct}")
            if cur_oct == end_oct and NOTES[idx] == end_n:
                return note_list
            idx += 1
        idx = 0
        cur_oct += 1
    return note_list

def parse_note_range(range_str):
    if len(range_str) <= 3:
        return range_str, range_str
    return (range_str[:3], range_str[3:]) if range_str[1] in ['b', '#'] else (range_str[:2], range_str[2:])

def detect_onsets(audio, threshold_db=-35, min_spacing_ms=250):
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    if audio.channels > 1:
        samples = samples.reshape((-1, audio.channels)).mean(axis=1)
    samples /= np.max(np.abs(samples)) + 1e-9
    energy = 20 * np.log10(np.abs(samples) + 1e-10)

    min_spacing = int(min_spacing_ms * audio.frame_rate / 1000)
    onsets = []
    last_onset = 0
    for i in range(len(energy)):
        if energy[i] > threshold_db and (i - last_onset) > min_spacing:
            onsets.append(int(i * 1000 / audio.frame_rate))
            last_onset = i
    return onsets

# Process each WAV file
for file_name in os.listdir(INPUT_DIR):
    print(f"📂 Found file: {file_name}")
    if file_name.lower().endswith(".wav") and "sul" in file_name:
        print(f"➡️  Matched: {file_name}")
        base_name = os.path.splitext(file_name)[0]  # Remove extension
        parts = base_name.split('.')                # e.g., Guitar.mf.sul_E.C5B5.mono
        try:
            technique = parts[2].replace("_", "")   # e.g., sul_E → sulE
            note_range = parts[3]                   # e.g., C5B5
        except IndexError:
            print(f"⚠️ Skipping malformed filename: {file_name}")
            continue

        start_note, end_note = parse_note_range(note_range)
        note_list = get_note_range(start_note, end_note)

        audio_path = os.path.join(INPUT_DIR, file_name)
        audio = AudioSegment.from_file(audio_path, format="wav")
        print(f"\n📁 Processing {file_name} ({len(audio)} ms, {audio.frame_rate} Hz)")

        onsets = detect_onsets(audio, threshold_db=-25, min_spacing_ms=750)
        if len(onsets) < len(note_list) or len(onsets) > len(note_list) * 2:
            print("⚠️ Onset count unreliable — using even split")
            segment_len = len(audio) // len(note_list)
            onsets = [i * segment_len for i in range(len(note_list))]

        print(f"🎯 Detected {len(onsets)} onsets (Expected: {len(note_list)})")

        if not onsets:
            print(f"⚠️ No onsets found — skipping")
            continue

        for i in range(min(len(note_list), len(onsets))):
            start = onsets[i]
            end = onsets[i + 1] if i + 1 < len(onsets) else len(audio)
            chunk = audio[start:end]
            out_name = f"{technique}_{note_list[i]}.wav"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            chunk.export(out_path, format="wav", parameters=["-acodec", "pcm_s16le"])
            print(f"✅ Saved: {out_name} ({end - start} ms)")

print("\n✅ All guitar samples parsed and saved to Instruments/Guitar.")
