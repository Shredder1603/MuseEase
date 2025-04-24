import os
import shutil

# PATHS
BASE_DIR = r"C:\Users\Jo\Documents\ECE Senior Design\MuseEase"
RAW_DIR = os.path.join(BASE_DIR, "drum-samples\GSCW Drums Kit 1 Samples")
DEST_DIR = os.path.join(BASE_DIR, "Instruments", "Drums")
os.makedirs(DEST_DIR, exist_ok=True)

# MAPPING: (search keyword, output filename)
DRUM_MAP = {
    "Kick": ("kick", "Kick_C4.wav"),
    "Snare": ("snare", "Snare_C#4.wav"),
    "HiHat Closed": ("hhatscl", "HiHat_D4.wav"),
    "HiHat Open": ("hhatsop", "HiHatOpen_D#4.wav"),
    "Crash": ("crash", "Crash_E4.wav"),
    "Splash": ("splash", "Splash_F4.wav"),
    "Ride": ("ride", "Ride_F#4.wav"),
    "Bell": ("bell", "Bell_G4.wav"),
    "Rimshot": ("sstick", "Rim_G#4.wav"),
    "Tom": ("tom", "Tom_A4.wav")
}




def normalize(name):
    return name.lower().replace("_", "").replace("-", "")

all_files = [f for f in os.listdir(RAW_DIR) if f.lower().endswith(".wav")]
selected_files = {}

for label, (keyword, output_name) in DRUM_MAP.items():
    print(f"\n🔍 Searching for {label}...")
    for file in all_files:
        #print(f"🔍 Checking {file} for {label}...")
        if keyword in normalize(file):
            selected_files[output_name] = os.path.join(RAW_DIR, file)
            print(f"✅ Matched {label}: {file} → {output_name}")
            break
    else:
        print(f" Warning: No match found for {label}")

for output_name, src_path in selected_files.items():
    dest_path = os.path.join(DEST_DIR, output_name)
    shutil.copyfile(src_path, dest_path)

print("\n Drum kit created successfully in Instruments/Drums!")
