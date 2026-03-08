import csv
import requests
import genanki
import random
import os
import shutil
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------
# CONFIGURATION
# -----------------------
CSV_FILE = "french_nouns_top10.csv"

# Pexels API
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")

# ElevenLabs API
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "YOUR_YOUR_API_KEY")
ELEVEN_VOICE_ID = "EXAVITQu4vr4xnSDxMaL" # Bella (Standard Voice)
# Output directories
OUTPUT_DIR = "data"
MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# -----------------------
# HELPER FUNCTIONS
# -----------------------

def get_image_hash(img_path):
    """Generate a short hash of the image content."""
    with open(img_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def clean_old_hashed_images(base_name, current_hash):
    """Delete old hashed versions of the same image."""
    for f in os.listdir(MEDIA_DIR):
        if f.startswith(f"{base_name}_") and f.endswith(".jpg"):
            if f != f"{base_name}_{current_hash}.jpg":
                try:
                    os.remove(os.path.join(MEDIA_DIR, f))
                    print(f"Cleaned up old image: {f}")
                except Exception as e:
                    print(f"Error cleaning up {f}: {e}")

# Generate audio via ElevenLabs
def generate_audio_eleven(text, language, save_path):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'text': text,
        'model_id': 'eleven_multilingual_v2'
    }
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(resp.content)
        return save_path
    else:
        print(f"Error generating audio for {text}: {resp.text}")
        return None

# Sanitize filenames
def sanitize_filename(text):
    return text.replace("’","").replace(" ","_").lower()

# -----------------------
# CREATE ANKI DECK
# -----------------------

# Model
MODEL_ID = 1607392319
DECK_ID = 2059400110

model = genanki.Model(
    MODEL_ID,
    'French Noun With Image & Audio',
    fields=[
        {'name': 'French'},
        {'name': 'English'},
        {'name': 'Image'},
        {'name': 'Audio'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Image}}',
            'afmt': '{{FrontSide}}<hr id="answer"><b>{{French}}</b><br>{{English}}<br>{{Audio}}',
        }
    ]
)

# Deck
deck = genanki.Deck(
    DECK_ID,
    'Top French Nouns Deck'
)

media_files = []
missing_images = []

# -----------------------
# PROCESS CSV
# -----------------------

# Function to check if a file is already in image_links.txt
def is_already_in_links(img_path):
    if not os.path.exists("image_links.txt"):
        return False
    with open("image_links.txt", "r", encoding="utf-8") as f:
        return img_path in f.read()

with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        french = row['french'].strip()
        english = row['english'].strip()

        # Filenames
        base = sanitize_filename(french)
        img_file = os.path.join(MEDIA_DIR, f"{base}.jpg")
        fr_audio_file = os.path.join(MEDIA_DIR, f"{base}_fr.mp3")

        # Fetch image using English keyword (interactive selection)
        print(f"\n{'='*60}")
        print(f"Processing: {french} ({english})")
        print(f"{'='*60}")
        
        img_tag = ""
        if os.path.exists(img_file):
            print(f"✅ Image already exists: {img_file}")
            
            # Generate hash and unique filename for Anki
            img_hash = get_image_hash(img_file)
            clean_old_hashed_images(base, img_hash)
            
            hashed_img_name = f"{base}_{img_hash}.jpg"
            hashed_img_path = os.path.join(MEDIA_DIR, hashed_img_name)
            
            if not os.path.exists(hashed_img_path):
                shutil.copy2(img_file, hashed_img_path)
            
            media_files.append(hashed_img_path)
            img_tag = f'<img src="{hashed_img_name}">'
        else:
            print(f"❌ Image missing: {img_file}")
            # Only add to image_links.txt if it's not already there
            if not is_already_in_links(img_file):
                with open("image_links.txt", "a", encoding="utf-8") as f:
                    f.write(f"{img_file}, {english} [ADD URL HERE]\n")
            
            # Track missing images
            missing_images.append((os.path.basename(img_file), english))
            img_tag = f'<img src="{os.path.basename(img_file)}">'

        # Generate French audio only
        audio_tag = ""
        if os.path.exists(fr_audio_file):
            print(f"✅ Audio already exists: {fr_audio_file}")
            media_files.append(fr_audio_file)
            audio_tag = f'[sound:{os.path.basename(fr_audio_file)}]'
        elif generate_audio_eleven(french, 'fr', fr_audio_file):
            media_files.append(fr_audio_file)
            audio_tag = f'[sound:{os.path.basename(fr_audio_file)}]'

        # Generate a stable GUID based on the French word
        # This ensures Anki updates the card if fields change instead of creating duplicates
        note_id = genanki.guid_for(french)

        # Add note
        note = genanki.Note(
            model=model,
            fields=[
                french,
                english,
                img_tag,
                audio_tag.strip()
            ],
            guid=note_id
        )
        deck.add_note(note)

# -----------------------
# PACKAGE AND SAVE
# -----------------------
package = genanki.Package(deck)
package.media_files = media_files
output_file = os.path.join(OUTPUT_DIR, 'french_nouns_deck.apkg')
package.write_to_file(output_file)
print(f"Deck created: {output_file}")

# -----------------------
# MISSING IMAGES REPORT
# -----------------------
if missing_images:
    print(f"\n{'!'*60}")
    print("IMAGES NEEDED TO BE CREATED:")
    print(f"{'!'*60}")
    for filename, english_word in missing_images:
        print(f"{filename} : {english_word}")
    print(f"{'!'*60}\n")
