"""
French Grammar Cloze Card Generator

This script generates Anki cloze deletion cards for French grammar practice.
Audio is generated using ElevenLabs and only plays on the answer side.

CSV FORMAT REQUIRED:
The CSV file must have the following columns (in this order):
- cloze_sentence: Sentence with ___ where the blank should be
- answer: The correct word to fill in the blank
- full_sentence: Complete French sentence with the answer
- translation: English translation of the sentence
- verb_hint: French infinitive verb (e.g., être, avoir)
- verb_hint_en: English verb hint (e.g., to be, to have)

EXAMPLE CSV:
cloze_sentence,answer,full_sentence,translation,verb_hint,verb_hint_en
Je ___ fatigué,suis,Je suis fatigué,I am tired,être,to be
Tu ___ français,es,Tu es français,You are French,être,to be
J'___ un chat,ai,J'ai un chat,I have a cat,avoir,to have

"""

import csv
import requests
import genanki
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------
# CONFIGURATION
# -----------------------
CSV_FILE = "french_grammar.csv"

# ElevenLabs API
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "YOUR_ELEVEN_API_KEY")
ELEVEN_VOICE_ID = "rgFgMEXfdGwXCYio7I0J"#"dYjOkSQBPiH2igolJfeH"  # Use a multilingual voice


# Output directories
OUTPUT_DIR = "french_grammer"
MEDIA_DIR = os.path.join(OUTPUT_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# -----------------------
# HELPER FUNCTIONS
# -----------------------

# Generate audio via ElevenLabs
def generate_audio_eleven(text, save_path):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'text': text,
        'model_id': 'eleven_multilingual_v2',
           "voice_settings": {
            "stability": 1.0,          # 0.0 – 1.0
            "similarity_boost": 1.0,   # 0.0 – 1.0
            "style": 0.0,              # 0.0 – 1.0   (style exaggeration)
            "use_speaker_boost": True
        },
        "voice_generation": {
            "speed": 1.0               # Default is 1.0, lower = slower, higher = faster
        }
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
    return text.replace("'","").replace(" ","_").replace(",","").replace(".","").replace("?","").replace("!","").lower()

# -----------------------
# CREATE ANKI DECK
# -----------------------

# Model for Cloze cards with audio on back
model = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    'French Grammar Cloze',
    fields=[
        {'name': 'Text'},
        {'name': 'Extra'},
        {'name': 'Audio'},
        {'name': 'VerbHint'},
    ],
    templates=[
        {
            'name': 'Cloze Grammar Card',
            'qfmt': '{{cloze:Text}}<br><br><small>{{VerbHint}}</small>',
            'afmt': '{{cloze:Text}}<hr id="answer"><div>{{Extra}}</div><div>{{Audio}}</div>',
        }
    ],
    model_type=genanki.Model.CLOZE,
    css='''
.card {
 font-family: arial;
 font-size: 22px;
 text-align: center;
 color: black;
 background-color: white;
}
.cloze {
 font-weight: bold;
  color: #059669; 
  background-color: #ECFDF5;
}
'''
)

# Deck
deck = genanki.Deck(
    random.randrange(1 << 30, 1 << 31),
    'French Grammar Cloze Deck'
)

media_files = []

# -----------------------
# PROCESS CSV
# -----------------------
with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cloze_sentence = row['cloze_sentence'].strip()
        answer = row['answer'].strip()
        full_sentence = row['full_sentence'].strip()
        translation = row['translation'].strip()
        verb_hint = row['verb_hint'].strip()
        verb_hint_en = row['verb_hint_en'].strip()

        # Create the Text field with cloze formatting
        # Replace ___ with {{c1::answer}}
        text = cloze_sentence.replace("___", f"{{{{c1::{answer}}}}}")
        # Add English verb hint in parentheses
        text += f" ({verb_hint_en})"

        # Create the Extra field with translation only (French is already shown via cloze)
        extra = f"<i>{translation}</i>"

        # Generate audio for the full sentence
        base = sanitize_filename(full_sentence[:30])  # Use first 30 chars for filename
        audio_file = os.path.join(MEDIA_DIR, f"grammar_{base}.mp3")
        
        audio_tag = ""
        # Check if audio file already exists
        if os.path.exists(audio_file):
            print(f"  Audio already exists: {os.path.basename(audio_file)}")
            media_files.append(audio_file)
            audio_tag = f'[sound:{os.path.basename(audio_file)}]'
        elif generate_audio_eleven(full_sentence, audio_file):
            media_files.append(audio_file)
            audio_tag = f'[sound:{os.path.basename(audio_file)}]'

        # Add note with tags
        note = genanki.Note(
            model=model,
            fields=[
                text,           # Text: "Je {{c1::suis}} fatigué. (to be)"
                extra,          # Extra: "Je suis fatigué.<br>I am tired."
                audio_tag,      # Audio: [sound:filename.mp3]
                verb_hint       # VerbHint: "être"
            ],
            tags=[verb_hint]
        )
        deck.add_note(note)
        print(f"Added card: {cloze_sentence}")

# -----------------------
# PACKAGE AND SAVE
# -----------------------
package = genanki.Package(deck)
package.media_files = media_files
output_file = os.path.join(OUTPUT_DIR, 'french_grammar_deck.apkg')
package.write_to_file(output_file)
print(f"\nDeck created: {output_file}")
print(f"Total cards: {len(deck.notes)}")

