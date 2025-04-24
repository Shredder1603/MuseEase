import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydub import AudioSegment

#  PATHS 
URL = "https://theremin.music.uiowa.edu/MIS-Pitches-2012/MISDoubleBass2012.html"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(BASE_DIR, "Instruments", "Bass")
os.makedirs(DEST_DIR, exist_ok=True)

#  Scrape the webpage
print(f" Fetching from {URL}...")
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.find_all("a", href=True)
print(f" Found {len(links)} total links.\n")

#  Match any pizzicato sample 
pattern = r"Bass\.pizz.*\.(C|Db|D|Eb|E|F|Gb|G|Ab|A|Bb|B)(\d)\.stereo\.aif(f?)"
matched = 0

for a in links:
    href = a['href']
    print(f"🧾 Scanning: {href}")

    if "pizz" in href and (href.endswith(".aif") or href.endswith(".aiff")):
        match = re.search(pattern, href)
        if match:
            note = match.group(1) + match.group(2)  # e.g., C1
            filename = f"{note}.wav"
            full_url = urljoin(URL, href.replace(" ", "%20"))
            local_aiff = os.path.join(BASE_DIR, "temp.aiff")
            local_wav = os.path.join(DEST_DIR, filename)

            print(f" Matched note: {note} → downloading as {filename}")
            try:
                with open(local_aiff, "wb") as f:
                    f.write(requests.get(full_url).content)

                # Convert AIFF → WAV (mono)
                audio = AudioSegment.from_file(local_aiff, format="aiff").set_channels(1)
                audio.export(local_wav, format="wav")
                print(f" Saved to: {local_wav}\n")
                matched += 1
            except Exception as e:
                print(f" Error processing {filename}: {e}\n")
        else:
            print(f" No note match found.\n")
    else:
        print(f"⏭ Skipped (not pizzicato or not .aiff)\n")

# Cleanup
temp = os.path.join(BASE_DIR, "temp.aiff")
if os.path.exists(temp):
    os.remove(temp)

print(f"\n Done: {matched} samples downloaded and converted.")
