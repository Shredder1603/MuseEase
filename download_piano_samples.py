import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL of the webpage containing the links
URL = "https://theremin.music.uiowa.edu/MISpiano.html"  # Update this to the correct URL

# Define the destination directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
DEST_DIR = os.path.join(BASE_DIR, "Instruments", "Piano")  # Save in Instruments/Piano
os.makedirs(DEST_DIR, exist_ok=True)  # Ensure directory exists

# Fetch the webpage
response = requests.get(URL)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all "Piano.ff" sample links
links = soup.find_all('a', href=True)
ff_links = {}

for a in links:
    href = a['href']
    if "Piano.ff" in href or "Piano.mf" in href or "Piano.pp" in href:  # Download all dynamics
        match = re.search(r"Piano\.(?:pp|mf|ff)\.(.*?)\.aiff", href)  # Extract note name
        if match:
            note_name = match.group(1)  # Extract "C8", "Db2", etc.
            full_url = urljoin(URL, href.replace(" ", "%20"))  # Fix spaces in URL
            ff_links[note_name] = full_url

# Download and rename files
for note_name, link in ff_links.items():
    new_name = f"{note_name}.aiff"  # Renaming format: "C1.aiff"
    file_path = os.path.join(DEST_DIR, new_name)

    # Download file
    print(f"Downloading {note_name} from {link} ...")
    file_data = requests.get(link).content
    with open(file_path, "wb") as f:
        f.write(file_data)

    print(f"Saved as {file_path}")

print("Download and renaming complete! ✅")
